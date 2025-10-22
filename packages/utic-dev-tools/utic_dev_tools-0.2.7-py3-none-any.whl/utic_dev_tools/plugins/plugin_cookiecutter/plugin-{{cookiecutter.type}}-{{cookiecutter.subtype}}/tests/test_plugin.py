import json
from pathlib import Path

import pytest

from plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}} import EnvSettings, Plugin


@pytest.fixture
def plugin(tmp_path):
    settings_filepath: Path = tmp_path / "settings.json"
    settings = {"string_field": "string_field"}
    settings_filepath.write_text(json.dumps(settings))

    yield Plugin(
        env_settings=EnvSettings(
            shared_filepath=tmp_path,
            job_settings_file=str(settings_filepath),
        )
    )


@pytest.fixture
def elements():
    yield [
        {
            "type": "NarrativeText",
            "element_id": "1453c80530ef11712374570a086dbd64",
            "text": "TEXT HERE",
            "metadata": {
                "languages": ["eng"],
                "filetype": "text/plain",
                "data_source": {
                    "record_locator": {
                        "path": "/path/to/file.txt",
                    },
                    "permissions_data": [{"mode": 33188}],
                },
            },
        }
    ]


def test_plugin(plugin: Plugin, elements: list[dict]):
    plugin.plugin_settings.string_field = "test_string_field"

    output = plugin.run(elements)
    output_elements = output.element_dicts

    assert len(output_elements) == 1
    element_output = output_elements[0]
    assert element_output["metadata"]["string_field"] == "test_string_field"
