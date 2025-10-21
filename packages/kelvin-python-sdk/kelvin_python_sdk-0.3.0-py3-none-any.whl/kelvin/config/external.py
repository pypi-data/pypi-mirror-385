from __future__ import annotations

from pathlib import Path
from typing import Dict, Literal, Optional

from kelvin.config.common import AppBaseConfig, AppTypes, ConfigBaseModel, read_schema_file

from .manifest import (
    AppDefaults,
    AppManifest,
    DefaultsDefinition,
    Flags,
    RuntimeUpdateFlags,
    SchemasDefinition,
)


class RuntimeUpdateConfig(ConfigBaseModel):
    configuration: bool = False


class ExternalFlags(ConfigBaseModel):
    enable_runtime_update: RuntimeUpdateConfig = RuntimeUpdateConfig()


class SchemasConfig(ConfigBaseModel):
    configuration: Optional[str] = None


class DeploymentDefaults(ConfigBaseModel):
    system: Dict = {}
    configuration: Dict = {}


class ExternalConfig(AppBaseConfig):
    """
    Represents the configuration for an external (docker) app.
    """

    type: Literal[AppTypes.docker]  # type: ignore
    spec_version: str = "5.0.0"

    flags: ExternalFlags = ExternalFlags()
    ui_schemas: SchemasConfig = SchemasConfig()
    defaults: DeploymentDefaults = DeploymentDefaults()

    def to_manifest(self, read_schemas: bool = True, workdir: Path = Path(".")) -> AppManifest:
        return convert_external_to_manifest(self, read_schemas=read_schemas, workdir=workdir)


def convert_external_to_manifest(
    config: ExternalConfig, read_schemas: bool = True, workdir: Path = Path(".")
) -> AppManifest:
    """
    Converts an ExternalConfig object to an AppManifest object.

    Args:
        config (ExternalConfig): The external app configuration.
        read_schemas (bool): Whether to read schema files.
        workdir (Path): The working directory to use for reading schema files.

    Returns:
        AppManifest: The generated app manifest.
    """

    defaults = DefaultsDefinition()
    defaults_has_content = False
    if {"configuration"} & config.defaults.model_fields_set:
        defaults.app = AppDefaults(configuration=config.defaults.configuration)
        defaults_has_content = True
    if "system" in config.defaults.model_fields_set:
        defaults.system = config.defaults.system
        defaults_has_content = True

    manif_defaults = defaults if defaults_has_content else None

    flags = Flags(
        spec_version=config.spec_version,
        enable_runtime_update=RuntimeUpdateFlags(
            configuration=config.flags.enable_runtime_update.configuration,
        ),
    )

    schemas = SchemasDefinition()
    if read_schemas:
        schemas.configuration = (
            read_schema_file(workdir / config.ui_schemas.configuration) if config.ui_schemas.configuration else {}
        )

    return AppManifest(
        type=config.type,
        name=config.name,
        title=config.title,
        description=config.description,
        version=config.version,
        category=config.category,
        defaults=manif_defaults,
        flags=flags,
        schemas=schemas,
    )
