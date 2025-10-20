import logging
import json
import sys

import requests
from typing import Optional

from . import core


TRIAL_GROUP_URL = 'https://www.varsnap.com/api/trial_group/'


def _configure_logger(verbosity: int) -> logging.Logger:
    varsnap_logger = logging.getLogger(core.__name__)
    varsnap_logger.handlers = []
    varsnap_logger.disabled = True
    varsnap_logger.propagate = False

    test_logger = logging.getLogger(__name__)
    test_logger.setLevel(verbosity)
    handler = logging.StreamHandler(sys.stdout)
    test_logger.addHandler(handler)
    return test_logger


def generate_trial_group() -> core.TrialGroup:
    data = {
        'consumer_token': core.env_var(core.ENV_CONSUMER_TOKEN),
        'client': core.CLIENT_NAME,
        'branch': core.get_branch(),
    }
    response = requests.post(TRIAL_GROUP_URL, data=data)
    try:
        response_data = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        response_data = {}
    if not response_data or response_data['status'] != 'ok':
        trial_group = core.TrialGroup('', '', '')
    else:
        trial_group = core.TrialGroup(
            response_data['project_id'],
            response_data['trial_group_id'],
            response_data['trial_group_url'],
        )
    return trial_group


def _test(test_logger: logging.Logger) -> tuple[list[core.Trial], str]:
    trial_group = generate_trial_group()
    test_logger.info("")
    test_logger.info(
        "Starting Varsnap Tests.  Test Results: %s" %
        trial_group.trial_group_url,
    )
    all_trials: list[core.Trial] = []
    for consumer in core.CONSUMERS:
        consumer_name = consumer.target_func.__qualname__
        test_logger.info("Running Varsnap tests for %s" % consumer_name)
        all_trials += consumer.consume(trial_group)
    test_logger.info("Test Results: %s" % trial_group.trial_group_url)
    test_logs = "Test Results: %s" % trial_group.trial_group_url
    return all_trials, test_logs


def test(verbosity:int=logging.INFO) -> tuple[Optional[bool], str]:
    test_logger = _configure_logger(verbosity)
    trials, test_logs = _test(test_logger)
    all_matches: Optional[bool] = None
    if trials:
        all_matches = all([t.matches for t in trials])
    all_logs = test_logs
    if all_matches is not None and not all_matches:
        all_logs = "\n\n".join(['', test_logs] + [
            t.report for t in trials if t.report and not t.matches
        ] + [test_logs, ''])
    return all_matches, all_logs
