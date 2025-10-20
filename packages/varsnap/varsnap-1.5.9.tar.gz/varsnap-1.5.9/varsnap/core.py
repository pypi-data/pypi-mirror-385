from __future__ import annotations

import base64
import binascii
import copy
import inspect
import json
import logging
import os
from pathlib import Path
import pprint
import shutil
import subprocess
import sys
import threading
import traceback
from typing import Any, Callable, Optional, Union
import unittest
import warnings

import dill as pickle
import requests

from .__version__ import __version__

# Types
ArgsType = list[Any]
KwargsType = dict[Any, Any]
GlobalsType = Any
OutputType = Any
TargetFunction = Callable[..., Any]

VERSION: str = __version__
CLIENT_NAME = 'python.%s' % __version__
PRODUCE_SNAP_URL = 'https://www.varsnap.com/api/snap/produce/'
CONSUME_SNAP_URL = 'https://www.varsnap.com/api/snap/consume/'
PRODUCE_TRIAL_URL = 'https://www.varsnap.com/api/trial/produce/'
UNPICKLE_ERRORS = [
    binascii.Error,
    ImportError,
    ModuleNotFoundError,
    pickle.UnpicklingError,
]
PICKLE_ERRORS = [
    AttributeError,
    ModuleNotFoundError,
    pickle.PicklingError,
    TypeError,
]

# Names of different environment variables used by varsnap
# See readme for descriptions
ENV_VARSNAP = 'VARSNAP'
ENV_ENV = 'ENV'
ENV_PRODUCER_TOKEN = 'VARSNAP_PRODUCER_TOKEN'
ENV_CONSUMER_TOKEN = 'VARSNAP_CONSUMER_TOKEN'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(handler)

# A list of Varsnap functions for testing and tracing
CONSUMERS = []
PRODUCERS = []


def env_var(env: str) -> str:
    return os.environ.get(env, '').lower()


def get_signature(target_func: TargetFunction) -> str:
    return '%s.%s' % (CLIENT_NAME, target_func.__qualname__)


def align_report(report: list[tuple[str, str]]) -> str:
    # Vertically align report's second column
    key_length = max([len(x[0]) for x in report]) + 2
    report_lines = [
        x[0] + ' '*(key_length - len(x[0])) + str(x[1])
        for x in report
    ]
    log = "\n".join(report_lines)
    return log


def limit_string(x: str) -> str:
    limit = 30
    ellipsis = '...'
    if len(x) <= limit:
        return x
    return x[:limit - len(ellipsis)] + ellipsis


def get_branch() -> str:
    path = Path.cwd()
    if not shutil.which('git'):
        return ''
    git_branch_command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    process = subprocess.run(
        git_branch_command,
        cwd=str(path),
        capture_output=True, check=False,
    )
    return process.stdout.decode('utf-8').strip()


class DeserializeError(ValueError):
    pass


class SerializeError(ValueError):
    pass


class Inputs():
    def __init__(
        self,
        args: ArgsType,
        kwargs: KwargsType,
        global_vars: GlobalsType,
    ):
        self.args = args
        self.kwargs = kwargs
        self.globals = global_vars

    def marshal(
        self,
    ) -> dict[str, Union[ArgsType, KwargsType, GlobalsType]]:
        data = {
            'args': self.args,
            'kwargs': self.kwargs,
            'globals': self.globals,
        }
        return data

    def serialize(self) -> str:
        serialized_data = Producer.serialize(self.marshal())
        return serialized_data

    def serialize_formatted(self) -> str:
        serialized_data = Producer.serialize_formatted(self.marshal())
        return serialized_data

    @staticmethod
    def deserialize(serialized_data: str) -> Inputs:
        data = Consumer.deserialize(serialized_data)
        assert 'args' in data
        assert 'kwargs' in data
        assert 'globals' in data
        inputs = Inputs(data['args'], data['kwargs'], data['globals'])
        return inputs


class Trial():
    def __init__(
        self,
        inputs: Inputs,
        prod_outputs: OutputType,
    ):
        self.inputs: Inputs = inputs
        self.prod_outputs: OutputType = prod_outputs
        self.local_outputs: Optional[OutputType] = None
        self.exception: Optional[str] = None
        self.matches: Optional[bool] = None
        self.report: Optional[str] = None


class TrialGroup():
    def __init__(
        self,
        project_id: str,
        trial_group_id: str,
        trial_group_url: str,
    ):
        self.project_id: str = project_id
        self.trial_group_id: str = trial_group_id
        self.trial_group_url: str = trial_group_url


class Producer():
    def __init__(self, target_func: TargetFunction) -> None:
        self.target_func = target_func
        PRODUCERS.append(self)

    @staticmethod
    def is_enabled() -> bool:
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'production':
            return False
        if not env_var(ENV_PRODUCER_TOKEN):
            return False
        return True

    @staticmethod
    def normalize_data(data: Any) -> Any:
        if str(type(data)) == "<class 'flask.wrappers.Response'>":
            # Disable ResourceWarning from flask send_file
            # TODO: remove this after werkzeug flask client
            # correctly closes send_file
            with warnings.catch_warnings(
                action='ignore', category=ResourceWarning,
            ):
                data.freeze()
            data = data.get_data()
        return data

    @staticmethod
    def serialize(
        data: Union[
            OutputType,
            dict[str, Union[ArgsType, KwargsType, GlobalsType]],
        ],
    ) -> str:
        data = Producer.normalize_data(data)
        try:
            pickle_data = pickle.dumps(data)
        except Exception as e:
            if type(e) in PICKLE_ERRORS:
                raise SerializeError(e) from e
            raise
        serialized_data = base64.b64encode(pickle_data).decode('utf-8')
        return serialized_data

    @staticmethod
    def serialize_formatted(
        data: Union[
            OutputType,
            dict[str, Union[ArgsType, KwargsType, GlobalsType]],
        ],
    ) -> str:
        serialized_data = pprint.pformat(data)
        return serialized_data

    @staticmethod
    def get_globals() -> dict[str, GlobalsType]:
        """
        This function's logic is being reconsidered given the possibility of
        globals breaking logic
        """
        global_vars: dict[str, GlobalsType] = {}
        return global_vars
        """
        # TODO - need to fix this to be safer
        for k, v in globals().items():
            if k[:2] == '__':
                continue
            try:
                pickle.dumps(v)
            # Ignore unpickable data
            except Exception as e:
                if type(e) in PICKLE_ERRORS:
                    continue
                raise
            global_vars[k] = v
        return global_vars
        """

    def produce(
        self,
        args: ArgsType,
        kwargs: KwargsType,
        output: OutputType,
    ) -> None:
        if not Producer.is_enabled():
            return
        LOGGER.debug(
            'Varsnap producing call for %s' %
            self.target_func.__qualname__,
        )
        global_vars = Producer.get_globals()
        inputs = Inputs(args, kwargs, global_vars)
        data = {
            'producer_token': env_var(ENV_PRODUCER_TOKEN),
            'signature': get_signature(self.target_func),
        }
        try:
            data['inputs'] = inputs.serialize()
        except SerializeError as e:
            LOGGER.warning(
                'Varsnap cannot serialize inputs for %s: %s' %
                (self.target_func.__qualname__, e),
            )
            return
        try:
            data['prod_outputs'] = Producer.serialize(output)
        except SerializeError as e:
            LOGGER.warning(
                'Varsnap cannot serialize outputs for %s: %s' %
                (self.target_func.__qualname__, e),
            )
            return
        requests.post(PRODUCE_SNAP_URL, data=data, timeout=5)


class Consumer():
    def __init__(self, target_func: Callable[..., Any]) -> None:
        self.target_func = target_func
        self.test_case = unittest.TestCase()
        CONSUMERS.append(self)

    @staticmethod
    def is_enabled() -> bool:
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'development':
            return False
        if not env_var(ENV_CONSUMER_TOKEN):
            return False
        return True

    @staticmethod
    def deserialize(data: str) -> Any:
        decoded_data = base64.b64decode(data.encode('utf-8'))
        try:
            deserialized_data = pickle.loads(decoded_data)
        except Exception as e:
            if type(e) in UNPICKLE_ERRORS:
                raise DeserializeError(e) from e
            raise
        return deserialized_data

    def consume(self, trial_group: TrialGroup) -> list[Trial]:
        if not Consumer.is_enabled():
            return []
        data = {
            'consumer_token': env_var(ENV_CONSUMER_TOKEN),
            'signature': get_signature(self.target_func),
        }
        response = requests.post(CONSUME_SNAP_URL, data=data, timeout=5)
        try:
            response_data = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            response_data = {}
        if not response_data or response_data['status'] != 'ok':
            return []
        trials: list[Trial] = []
        for result in response_data['results']:
            trial = self.consume_one(trial_group, result)
            if trial:
                trials.append(trial)
        return trials

    def target_func_params_matches(self, inputs: Inputs) -> bool:
        func_signature = inspect.signature(self.target_func)
        parameters = func_signature.parameters
        for param_name in parameters.keys():
            param = parameters[param_name]
            if param.kind in [param.VAR_POSITIONAL, param.VAR_KEYWORD]:
                # Function has variadic params, so cannot match param counts.
                # Default to true
                return True
        inputs_len = len(inputs.args) + len(inputs.kwargs)
        return len(parameters) == inputs_len

    def equal(self, x: OutputType, y: OutputType) -> bool:
        if isinstance(x, Exception) and isinstance(y, Exception):
            try:
                with self.test_case.assertRaises(type(x)):
                    raise y
                with self.test_case.assertRaises(type(y)):
                    raise x
            except self.test_case.failureException:
                return False
            return True

        try:
            self.test_case.assertEqual(x, y)
        except self.test_case.failureException:
            if not hasattr(x, '__dict__') or not hasattr(y, '__dict__'):
                return False
            for key in x.__dict__:
                if key not in y.__dict__:
                    return False
                if not self.equal(x.__dict__[key], y.__dict__[key]):
                    return False
            return True
        return True

    def consume_one(
        self,
        trial_group: TrialGroup,
        snap_data: dict[Any, Any],
    ) -> Optional[Trial]:
        LOGGER.info(
            'Testing with Varsnap snap uuid: ' + str(snap_data['id']),
        )
        try:
            inputs = Inputs.deserialize(snap_data['inputs'])
            prod_outputs = Consumer.deserialize(snap_data['prod_outputs'])
        except DeserializeError:
            return None
        trial = Trial(inputs, prod_outputs)
        trial.inputs.globals = {}
        for k, v in inputs.globals.items():
            globals()[k] = v
        if not self.target_func_params_matches(inputs):
            return None
        try:
            trial.local_outputs = self.target_func(
                *inputs.args,
                **inputs.kwargs,
            )
        except Exception as e:
            trial.local_outputs = e
            trial.exception = traceback.format_exc()
        trial.local_outputs = Producer.normalize_data(trial.local_outputs)
        trial.matches = self.equal(trial.prod_outputs, trial.local_outputs)
        report_lines: list[tuple[str, str]] = []
        report_lines += self.report_central(
            trial_group,
            env_var(ENV_CONSUMER_TOKEN),
            snap_data['id'],
            inputs,
            trial.prod_outputs,
            trial.local_outputs,
            trial.matches,
        )
        report_lines += self.report_log(
            trial.inputs, str(trial.prod_outputs), str(trial.local_outputs),
            trial.exception, trial.matches,
        )
        trial.report = align_report(report_lines)
        if trial.matches:
            LOGGER.info(trial.report)
        else:
            LOGGER.error(trial.report)

        return trial

    def report_central(
        self, trial_group: TrialGroup, consumer_token: str, snap_id: str,
        inputs: Inputs, prod_outputs: OutputType, local_outputs: OutputType,
        matches: bool,
    ) -> list[tuple[str, str]]:
        inputs_formatted = inputs.serialize_formatted()
        prod_outputs_formatted = Producer.serialize_formatted(prod_outputs)
        test_outputs_formatted = Producer.serialize_formatted(local_outputs)
        data = {
            'trial_group_id': trial_group.trial_group_id,
            'consumer_token': consumer_token,
            'snap_id': snap_id,
            'test_outputs': Producer.serialize(local_outputs),
            'matches': matches,
            'inputs_formatted': inputs_formatted,
            'snap_outputs_formatted': prod_outputs_formatted,
            'test_outputs_formatted': test_outputs_formatted,
        }
        response = requests.post(PRODUCE_TRIAL_URL, data=data, timeout=5)
        try:
            response_data = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            response_data = {}
        if not response_data or response_data['status'] != 'ok':
            return []
        trial_url = response_data.get('trial_url', '')
        report_line = ('Report URL:', trial_url)
        return [report_line]

    def report_log(
        self, inputs: Inputs, prod_outputs: str, local_outputs: str,
        exception: Optional[str], matches: bool,
    ) -> list[tuple[str, str]]:
        function_name = self.target_func.__qualname__
        report = []
        report.append(('Function:', function_name))
        report.append(('Function input args:', limit_string(str(inputs.args))))
        report.append((
            'Function input kwargs:', limit_string(str(inputs.kwargs)),
        ))
        report.append((
            'Production function outputs:', limit_string(prod_outputs),
        ))
        report.append(('Your function outputs:', limit_string(local_outputs)))
        if exception:
            report.append(('Local exception:', limit_string(exception)))
        report.append(('Matching outputs:', str(matches)))
        return report


def varsnap(
    orig_func: Union[TargetFunction, staticmethod[Any, Any]],
) -> TargetFunction:
    try:
        # Have this operate on the actual function in case it is wrapping a
        # staticmethod object
        func = orig_func.__func__  # type: ignore
    except AttributeError:
        func = orig_func

    producer = Producer(func)
    Consumer(func)

    def magic(*args: Any, **kwargs: Any) -> Any:
        try:
            original_args = copy.deepcopy(args)
        except RecursionError:
            original_args = args
        try:
            original_kwargs = copy.deepcopy(kwargs)
        except RecursionError:
            original_kwargs = kwargs
        try:
            output = func(*args, **kwargs)
        except Exception as e:
            threading.Thread(
                target=producer.produce,
                args=(original_args, original_kwargs, e),
            ).start()
            raise
        threading.Thread(
            target=producer.produce,
            args=(original_args, original_kwargs, output),
        ).start()
        return output
    LOGGER.debug('Varsnap Loaded')
    # Reuse the original function name so it works with flask handlers
    magic.__name__ = func.__name__

    # Function attributes aren't supported by mypy
    # see https://github.com/python/mypy/issues/2087
    magic.orig_function = orig_func  # type: ignore
    return magic
