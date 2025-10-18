from importlib import resources

from pydantic import BaseModel, ConfigDict, TypeAdapter

from usos_bridge import data

USOS_INSTANCES_FILENAME: str = "usos_instances.json"


class UsosInstanceConfig(BaseModel):
    instance_id: str
    auth_page_url: str
    proxy_endpoint: str
    proxy_api_method_param_key: str
    session_cookie_name: str
    login_form_selector: str
    csrf_token_regex: str
    csrf_token_page: str
    csrf_token_data_key: str

    model_config = ConfigDict(frozen=True)


UsosInstanceConfigList = TypeAdapter(list[UsosInstanceConfig])


def _read_instances_json() -> str:
    return (resources.files(data) / USOS_INSTANCES_FILENAME).read_text()


def load_instance_configs() -> dict[str, UsosInstanceConfig]:
    instances_list_str: str = _read_instances_json()

    instance_list: list[UsosInstanceConfig] = UsosInstanceConfigList.validate_json(instances_list_str)

    instance_id_to_instance_config: dict[str, UsosInstanceConfig] = {}

    for instance_config in instance_list:
        if instance_config.instance_id in instance_id_to_instance_config:
            msg = f"Duplicate instance id {instance_config.instance_id} found in pkg configuration"
            raise ValueError(msg)

        instance_id_to_instance_config[instance_config.instance_id] = instance_config

    return instance_id_to_instance_config
