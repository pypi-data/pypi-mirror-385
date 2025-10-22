import json
from pathlib import Path
from typing import Callable, Generator, Iterable, Type, Tuple, Any, Dict, TypedDict, ParamSpec, TypeVar, Union, cast

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    CliSettingsSource,
    EnvSettingsSource,
    DotEnvSettingsSource,
    JsonConfigSettingsSource,
)
from pydantic import AliasGenerator, AliasChoices, ConfigDict, BaseModel, Field, model_validator
from pydantic.fields import FieldInfo

T = TypeVar("T")
MaybeNestedList = Union[T, Iterable["MaybeNestedList[T]"]]

def _flatten(seq: Iterable[MaybeNestedList[T]]) -> Generator[T, None, None]:
    for x in seq:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from _flatten(x)
        else:
            yield x  # pyright: ignore[reportReturnType]

def _collect_nested_aliases(cls: type[BaseModel]) -> dict[str, str]:
    """Collect alias mappings for nested models automatically."""
    alias_map: dict[str, str] = {}
    
    for name, field in cls.model_fields.items():
        has_alias = False
        def add_alias(alias: str, to: str = name):
            nonlocal has_alias
            alias_map[alias] = to
            has_alias = True

        field_type = field.annotation

        # if nested type is also an BaseModel, dive into it
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            nested_map = _collect_nested_aliases(field_type)
            for nested_alias, nested_path in nested_map.items():
                add_alias(nested_alias, f"{name}.{nested_path}")

        if not isinstance(field, NestedAliasFieldInfo):
            continue

        # include generated aliases
        if alias_generator := cls.model_config.get("alias_generator"):
            if callable(alias_generator):
                alias = alias_generator(name)
                add_alias(alias)
            else:
                _, validation_alias, _ = alias_generator.generate_aliases(name)
                if validation_alias:
                    if isinstance(validation_alias, str):
                        add_alias(validation_alias)
                    else:
                        aliases = list(_flatten(validation_alias.convert_to_aliases()))
                        for alias in aliases:
                            if isinstance(alias, str):
                                add_alias(alias)

        # also include this field's own alias
        if field.alias:
            add_alias(field.alias)

        # default to name
        if not has_alias:
            add_alias(name)

    return alias_map

class NestedAliasFieldInfo(FieldInfo):
    pass

P = ParamSpec("P")
R = TypeVar("R")

def _nested_alias_field_wrapper(_func: Callable[P, R]) -> Callable[P, R]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        # print("Before function call")
        return NestedAliasFieldInfo(*args, **kwargs)  # pyright: ignore[reportReturnType]
    return inner

NestedAliasField = _nested_alias_field_wrapper(Field)

def _snake_to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

class VeritoneNestedConfig(BaseModel):
    model_config = ConfigDict(
        # alias_generator=lambda x: _snake_to_camel(x),  # Convert snake_case to camelCase
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: AliasChoices(
                _snake_to_camel(field_name), field_name
            ),
            serialization_alias=lambda field_name: _snake_to_camel(field_name),
        ),
        validate_by_alias=True,
        serialize_by_alias=True
    )

class VeritoneBaseConfig(BaseSettings):
    """
    Load priority:
    1. command line args
    2. env vars
    3. .env files
        3.1. .env.local
        3.2. .env.stage
        3.3. .env.prod
        3.4. .env
    4. aiware-config.final.json
    5. config.json file
    6. aiware-config.json
    """

    model_config = SettingsConfigDict(
        # alias_generator=lambda x: _snake_to_camel(x),  # Convert snake_case to camelCase
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: AliasChoices(
                _snake_to_camel(field_name), field_name
            ),
            serialization_alias=lambda field_name: _snake_to_camel(field_name),
        ),
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="ignore",
        hide_input_in_errors=True,
        env_nested_delimiter="_",
        nested_model_default_partial_update=True,
        env_nested_max_split=1,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            # command line args
            CliSettingsSource(
                settings_cls,
                cli_parse_args=True,
                cli_ignore_unknown_args=True,
                cli_implicit_flags=True,
            ),
            # env vars
            EnvSettingsSource(settings_cls),
            # .env files
            DotEnvSettingsSource(
                settings_cls,
                env_file=(
                    ".env",
                    ".env.prod",
                    ".env.stage",
                    ".env.dev",
                    ".env.local",
                    ".env.prod.local",
                    ".env.stage.local",
                    ".env.dev.local",
                ),
            ),
            # aiware-config.final.json (injected by aiware docker containers)
            JsonConfigSettingsSourceParseAllAsJson(
                settings_cls, json_file="aiware-config.final.json"
            ),
            # config.json
            JsonConfigSettingsSource(settings_cls, json_file="config.json"),
            # aiware-config.json (aiware defaults)
            AiwareConfigJsonConfigSettingsSource(
                settings_cls, json_file="aiware-config.json"
            ),
        )

    @model_validator(mode="before")
    def expand_nested_aliases(cls, data: Any) -> Any:
        """Rewrite incoming data so aliases map to nested fields."""
        if not isinstance(data, dict):
            return data

        nested_aliases = _collect_nested_aliases(cast(type[BaseModel], cls))

        for alias, path in nested_aliases.items():
            if alias in data:
                current = data
                # walk into the dict using the dotted path
                parts = path.split(".")
                for p in parts[:-1]:
                    current = current.setdefault(p, {})
                current.setdefault(parts[-1], data.pop(alias))

        return data


def _parse_as_json_if_str(obj: Any) -> Any:
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except json.decoder.JSONDecodeError:
            return obj
    else:
        return obj


class JsonConfigSettingsSourceParseAllAsJson(JsonConfigSettingsSource):
    def _read_file(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding=self.json_file_encoding) as json_file:
            config_json: dict[str, Any] = json.load(json_file)
            return {
                entry_key: _parse_as_json_if_str(config_json[entry_key])
                for entry_key in config_json.keys()
            }


class _AiwareConfigJsonEntry(TypedDict):
    entry_key: str
    configuration: dict[str, Any] | None


class AiwareConfigJsonConfigSettingsSource(JsonConfigSettingsSource):
    """
    A source class that loads variables from an aiware-config.json file.
    This is a special case because aiware-config.json is an array, not an object.
    """

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding=self.json_file_encoding) as json_file:
            config_json: list[str | dict[str, Any]] = json.load(json_file)

            flattened_entries: list[_AiwareConfigJsonEntry] = []
            for config_entry in config_json:
                if isinstance(config_entry, dict):
                    for entry_key in config_entry:
                        flattened_entries.append(
                            {
                                "entry_key": entry_key,
                                "configuration": config_entry[entry_key],
                            }
                        )
                elif isinstance(config_entry, str):
                    flattened_entries.append(
                        {"entry_key": config_entry, "configuration": None}
                    )

            result: Dict[str, Any] = {}
            for entry in flattened_entries:
                entry_key = entry["entry_key"]
                entry_path = entry_key.split('.')

                entry_configuration = entry["configuration"]
                if entry_configuration is None:
                    continue

                default = entry_configuration.get("default", None)
                if default is None:
                    continue

                parent = result

                for entry_path_entry in entry_path[:-1]:
                    if entry_path_entry not in parent:
                        parent[entry_path_entry] = {}

                    parent = parent[entry_path_entry]

                parent[entry_path[-1]] = _parse_as_json_if_str(default)

            return result
