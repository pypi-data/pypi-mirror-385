import re

import pytest

from usos_bridge.instance_config import UsosInstanceConfig, load_instance_configs


def test_instance_config_json_valid() -> None:
    load_instance_configs()


@pytest.mark.parametrize("instance_config", load_instance_configs().values())
def test_instance_config_regex_valid(instance_config: UsosInstanceConfig) -> None:
    regex = re.compile(instance_config.csrf_token_regex)

    assert regex.groups == 1  # noqa: S101
