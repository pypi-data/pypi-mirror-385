from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from .appyaml import AppYaml
from .common import AppTypes, ConfigError
from .exporter import ExporterConfig
from .external import ExternalConfig
from .importer import ImporterConfig
from .manifest import AppManifest
from .smart_app import SmartAppConfig


def missing_config_error(file_path: str) -> str:
    return f"Config file {file_path} does not exist."


def invalid_yaml_error(file_path: str) -> str:
    return f"Invalid YAML in config file {file_path}."


@dataclass
class AppConfigObj:
    name: str
    version: str
    type: AppTypes
    config: ExporterConfig | ImporterConfig | SmartAppConfig | ExternalConfig | AppYaml

    def is_legacy(self) -> bool:
        return self.type in [AppTypes.kelvin_app, AppTypes.bridge, AppTypes.legacy_docker]

    def to_app_manifest(self, read_schemas: bool = True, workdir: Path = Path(".")) -> AppManifest:
        return self.config.to_manifest(read_schemas=read_schemas, workdir=workdir)


def parse_config_file(file_path: str) -> AppConfigObj:
    """
    Parses a YAML configuration file and returns an AppConfigObj.

    Args:
        file_path (str): The path to the configuration file.

    Raises:
        ConfigError: If the file does not exist or contains invalid YAML.

    Returns:
        AppConfigObj: The parsed configuration object.
    """
    if not os.path.exists(file_path):
        raise ConfigError(missing_config_error(file_path))

    try:
        with open(file_path, encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except (ParserError, ScannerError) as e:
        raise ConfigError(invalid_yaml_error(file_path)) from e

    return parse_config(config)


def parse_config(config: dict) -> AppConfigObj:
    app_type = config.get("type")
    if app_type is None and config.get("app", {}).get("type"):
        app_type = config["app"]["type"]

        if app_type == AppTypes.docker:
            # Convert type to legacy docker
            app_type = AppTypes.legacy_docker

    if app_type == AppTypes.app:
        smart_app_conf = SmartAppConfig.model_validate(config)
        return AppConfigObj(
            name=smart_app_conf.name, version=smart_app_conf.version, type=smart_app_conf.type, config=smart_app_conf
        )
    elif app_type == AppTypes.importer:
        importer_conf = ImporterConfig.model_validate(config)
        return AppConfigObj(
            name=importer_conf.name, version=importer_conf.version, type=importer_conf.type, config=importer_conf
        )
    elif app_type == AppTypes.exporter:
        exporter_conf = ExporterConfig.model_validate(config)
        return AppConfigObj(
            name=exporter_conf.name, version=exporter_conf.version, type=exporter_conf.type, config=exporter_conf
        )
    elif app_type == AppTypes.docker:
        external_conf = ExternalConfig.model_validate(config)
        return AppConfigObj(
            name=external_conf.name, version=external_conf.version, type=external_conf.type, config=external_conf
        )
    elif app_type in [AppTypes.kelvin_app, AppTypes.bridge, AppTypes.legacy_docker]:
        app_type_enum = AppTypes(app_type)
        app_conf = AppYaml.model_validate(config)
        return AppConfigObj(
            name=app_conf.info.name,
            version=app_conf.info.version,
            type=app_type_enum,
            config=app_conf,
        )
    else:
        raise ConfigError(f"Unknown app type: {app_type}")
