import re
import importlib
import os

import config as cfg


def test_key_val_re_matches_simple_pair():
    m = cfg.KEY_VAL_RE.search("value=123 other=5")
    assert m is not None
    assert m.group(1) == "value"
    assert m.group(2) == "123"


def test_var_regex_default_is_none_when_not_set():
    # TRACK_VARIABLES default in repository is empty -> VAR_REGEX should be None
    assert cfg.VAR_REGEX is None


def test_config_defaults_types():
    # basic type checks for a couple of config values
    assert isinstance(cfg.CHUNK_SIZE, int)
    assert isinstance(cfg.POLL_INTERVAL, float)
    assert isinstance(cfg.NUM_PROCESSES, int)