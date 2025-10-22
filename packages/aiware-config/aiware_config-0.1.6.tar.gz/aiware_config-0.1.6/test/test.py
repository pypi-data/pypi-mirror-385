import os
from unittest import mock

import pytest
from pydantic import Field, ValidationError

from aiware_config import VeritoneBaseConfig


class SimpleSettings(VeritoneBaseConfig):
    apple: str = Field(default=...)


@pytest.fixture(autouse=True)
def clean_env():
    with mock.patch.dict(os.environ, clear=True):
        yield


def test_env_prefix(env):
    env.set("app_apple", "hello")
    s = SimpleSettings()
    assert s.apple == "hello"


def test_env_no_prefix_err(env):
    env.set("apple", "hello")
    with pytest.raises(ValidationError) as exc_info:
        SimpleSettings()
    assert exc_info.value.errors(include_url=False) == [
        {"type": "missing", "loc": ("apple",), "msg": "Field required", "input": {}}
    ]


def test_env_override(env):
    env.set("app_apple", "hello")
    s = SimpleSettings(apple="goodbye")
    assert s.apple == "goodbye"


def test_env_missing():
    with pytest.raises(ValidationError) as exc_info:
        SimpleSettings()
    assert exc_info.value.errors(include_url=False) == [
        {"type": "missing", "loc": ("apple",), "msg": "Field required", "input": {}}
    ]
