from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from utic_public_types.plugins.models import Constraint, ConstraintMatch, PluginType


class PluginSettings(BaseModel):
    """
    Settings use to configure running instances of the plugin.

    These are what can be configured by the user and what will be
    available in the UI.
    """

    string_field: str | None = Field(
        "default value", title="String Field", description="This is a string field"
    )


PLUGIN_MANIFEST = PluginType(
    name="{{cookiecutter.name}}",
    type="{{cookiecutter.type}}",
    subtype="{{cookiecutter.subtype}}",
    version="0.0.1",
    image_name="plugin-{{cookiecutter.type}}-{{cookiecutter.subtype}}",
    settings=PluginSettings,
    presentation={
        "default": {},  # inspector panel,
        "docs": {},  # documentation
    },
    constraints=[
        Constraint(allow_after=ConstraintMatch(type="chunk")),
        Constraint(allow_before=ConstraintMatch(type="destination")),
    ],
    metadata={
        "tags": ["test"],
    },
)


class EnvSettings(BaseSettings):
    """
    Required runtime env var settings in order to correctly run the plugin.

    These will be provided by our runtime environment when the plugin is
    scheduled to run on the platform.
    """

    # mounted shared filepath where plugins can write output to
    shared_filepath: Path = "./"
    # path to plugin settings encoded in JSON
    job_settings_file: str = "settings.json"


class ElementDict(TypedDict):
    type: str
    element_id: str
    text: str
    metadata: dict[str, Any]


class Response(BaseSettings):
    element_dicts: list[dict]


@dataclass
class Plugin:
    """
    This method is called after the object is initialized.

    This object is initialized on startup.
    """

    env_settings: EnvSettings = field(default_factory=EnvSettings)
    plugin_settings: PluginSettings = field(init=False)

    def __post_init__(self):
        with open(self.env_settings.job_settings_file) as f:
            self.plugin_settings = PluginSettings.model_validate_json(f.read())

    def id(self) -> str:
        return "{{cookiecutter.type}}_{{cookiecutter.subtype}}"

    def run(self, element_dicts: list[dict]) -> Response:
        """
        This method is called once for every file that is processed.

        element_dicts is a list of elements:

        See https://docs.unstructured.io/open-source/concepts/document-elements
        """
        for element in element_dicts:
            element: ElementDict
            # this plugin is simply demonstrating updating the metadata
            # with the settings configuration.
            element["metadata"].update(self.plugin_settings.model_dump())

        return Response(element_dicts=element_dicts)
