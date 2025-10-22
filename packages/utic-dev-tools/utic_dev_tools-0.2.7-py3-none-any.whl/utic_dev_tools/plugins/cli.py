import argparse
import hashlib
import io
import os
import shutil
from http.cookiejar import DefaultCookiePolicy

import orjson
import requests
from pydantic_settings import BaseSettings
from requests.auth import HTTPBasicAuth
from utic_public_types.plugins.json_schema import generate_json_schema
from utic_public_types.plugins.models import PluginType


class EnvSettings(BaseSettings):
    plugin_registry: str | None = None
    plugin_registry_username: str | None = None
    plugin_registry_password: str | None = None
    plugin_registry_project: str | None = None
    plugin_registry_verify_ssl: bool = True


env_settings = EnvSettings()

parser = argparse.ArgumentParser(description="CLI to publish plugin metadata")

# Positional argument for the action
parser.add_argument(
    "cli_action",
    type=str,
    help="Action type (publish|list)",
)

# Positional argument for the plugin path
parser.add_argument(
    "plugin_path",
    type=str,
    nargs="?",
    help="The full path to the plugin in the format 'myplugin.module.MY_PLUGIN'.",
)

parser.add_argument(
    "--from-channel",
    type=str,
    default=None,
    help="If promoting, the originating channel to promote from.",
)

parser.add_argument(
    "--channel",
    type=str,
    default="dev",
    help="The channel to publish to (default: 'dev').",
)

parser.add_argument(
    "--registry",
    type=str,
    default=env_settings.plugin_registry,
    help="The registry to publish to.",
    required=False,
)

parser.add_argument(
    "--registry-project",
    type=str,
    default=env_settings.plugin_registry_project,
    help="The registry project to publish to.",
    required=False,
)

parser.add_argument(
    "--registry-username",
    type=str,
    default=env_settings.plugin_registry_username,
    help="The username to use for authentication.",
    required=False,
)

parser.add_argument(
    "--registry-password",
    type=str,
    default=env_settings.plugin_registry_password,
    help="The password to use for authentication.",
    required=False,
)

parser.add_argument(
    "--override-name",
    type=str,
    default=None,
    help="Override the plugin name from the manifest.",
    required=False,
)

parser.add_argument(
    "--override-type",
    type=str,
    default=None,
    help="Override the plugin type from the manifest.",
    required=False,
)

parser.add_argument(
    "--override-subtype",
    type=str,
    default=None,
    help="Override the plugin subtype from the manifest.",
    required=False,
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    default=False,
    help=(
        "Show what would be published without making any changes to the registry "
        "(publish command only)."
    ),
)


class RegistryException(Exception):
    pass


class OCIRegistry:
    """OCI-compliant registry client for plugin metadata."""

    def __init__(self, args):
        self.registry = args.registry.strip("/")
        self.headers = {}
        self.auth = None
        self.verify_ssl = env_settings.plugin_registry_verify_ssl
        if args.registry_username:
            self.auth = HTTPBasicAuth(args.registry_username, args.registry_password)

        self.base_url = os.path.join(self.registry, "v2")
        if args.registry_project:
            self.base_url = os.path.join(self.base_url, args.registry_project)

        self.session: requests.Session = requests.Session()
        self.session.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))

    def _build_url(self, *parts: str) -> str:
        """Build a URL from base_url and path parts."""
        return os.path.join(self.base_url, *parts)

    def _handle_response(
        self, response: requests.Response, operation: str, object_name: str, tag: str
    ) -> requests.Response | None:
        """Handle common response status codes for registry operations."""
        if response.status_code == 200:
            return response
        elif response.status_code == 404:
            return None
        else:
            raise RegistryException(
                f"Failed to {operation} for {object_name} with tag "
                f"{tag}: {response.status_code}: {response.text}"
            )

    def get_digest(self, registry_object_name: str, tag: str) -> tuple[str, int] | None:
        """Retrieve the digest and size for a manifest."""
        manifest_url = self._build_url(registry_object_name, "manifests", tag)

        response = self.session.get(
            manifest_url,
            auth=self.auth,
            headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
            verify=self.verify_ssl,
        )

        handled_response = self._handle_response(response, "get digest", registry_object_name, tag)
        if handled_response:
            metadata_index = handled_response.json()
            return metadata_index["config"]["digest"], metadata_index["config"]["size"]
        return None

    def get_data(self, registry_object_name: str, tag: str) -> dict | None:
        """Retrieve blob data for a given tag."""
        digest = self.get_digest(registry_object_name, tag)

        if digest is not None:
            index_url = self._build_url(registry_object_name, "blobs", digest[0])
            response = self.session.get(index_url, auth=self.auth, verify=self.verify_ssl)
            handled_response = self._handle_response(
                response, "get data", registry_object_name, tag
            )
            if handled_response:
                return handled_response.json()
        return None

    def upload_object(self, registry_object_name: str, data: bytes, tags: list[str]) -> None:
        """Upload a blob object and tag it."""
        upload_url = self._build_url(registry_object_name, "blobs/uploads/")

        response = self.session.post(upload_url, auth=self.auth, verify=self.verify_ssl)
        response.raise_for_status()

        # Get the upload location URL
        upload_location = response.headers["Location"]

        # Complete the blob upload with the JSON file
        sha_digest = calculate_sha256(data)
        if not upload_location.startswith("http://") and not upload_location.startswith("https://"):
            upload_location = f"{self.registry}{upload_location}"

        if "?" in upload_location:
            upload_location = f"{upload_location}&digest=sha256:{sha_digest}"
        else:
            upload_location = f"{upload_location}?digest=sha256:{sha_digest}"

        blob_response = self.session.put(
            upload_location,
            data=data,
            auth=self.auth,
            verify=self.verify_ssl,
        )
        blob_response.raise_for_status()

        # Push the manifest to the registry with the specified tag
        for tag in tags:
            self.tag(registry_object_name, f"sha256:{sha_digest}", len(data), tag)

    def list_tags(self, registry_object_name: str) -> list[str]:
        """List all tags for a repository."""
        list_url = self._build_url(registry_object_name, "tags/list")

        response = self.session.get(list_url, auth=self.auth, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()["tags"]

    def copy_tag(self, registry_object_name: str, from_tag: str, to_tag: str) -> None:
        """Copy a tag to a new tag name."""
        digest = self.get_digest(registry_object_name, from_tag)
        if digest is None:
            raise ValueError(f"Tag {from_tag} does not exist for {registry_object_name}")
        self.tag(registry_object_name, digest[0], digest[1], to_tag)

    def tag(self, registry_object_name: str, digest: str, size: int, tag: str) -> None:
        """Create or update a tag pointing to a digest."""
        manifest = {
            "schemaVersion": 2,
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": digest,
                "size": size,
            },
        }

        headers = {"Content-Type": "application/vnd.oci.image.manifest.v1+json"}

        # Push the manifest to the registry with the specified tag
        manifest_url = self._build_url(registry_object_name, "manifests", tag)
        response = self.session.put(
            manifest_url,
            headers=headers,
            data=orjson.dumps(manifest),
            auth=self.auth,
            verify=self.verify_ssl,
        )
        response.raise_for_status()


def calculate_sha256(data: bytes) -> str:
    sha256_hash = hashlib.sha256()
    io_data = io.BytesIO(data)
    for byte_block in iter(lambda: io_data.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_applied_overrides(args) -> list[tuple[str, str]]:
    """Extract non-empty override values from args.
    
    Returns:
        List of tuples containing (field_name, value) for applied overrides.
    """
    overrides = []
    for field in ["name", "type", "subtype"]:
        attr = f"override_{field}"
        if hasattr(args, attr) and getattr(args, attr):
            overrides.append((field, getattr(args, attr)))
    return overrides


def build_overrides(args) -> dict[str, str]:
    """Build override dict from command line arguments."""
    overrides = {}

    if args.override_type:
        overrides["type"] = args.override_type
    if args.override_subtype:
        overrides["subtype"] = args.override_subtype
    if args.override_name:
        overrides["name"] = args.override_name.strip()

    return overrides


def apply_metadata_overrides(plugin: PluginType, overrides: dict[str, str]) -> PluginType:
    """Apply metadata overrides to a plugin, returning a new PluginType instance."""
    plugin_dict = plugin.model_dump()
    for field, value in overrides.items():
        plugin_dict[field] = value
    return PluginType(**plugin_dict)


def get_plugin(plugin_path: str) -> PluginType:
    """Load a plugin from a module path like 'module.submodule:PLUGIN_MANIFEST'."""
    module_path, _, plugin_name = plugin_path.partition(":")

    names = module_path.split(".")
    used = names.pop(0)
    found = __import__(used)
    for n in names:
        used += "." + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    plugin = getattr(found, plugin_name)
    assert isinstance(plugin, PluginType)
    return plugin


def get_plugin_registry_name(plugin: PluginType) -> str:
    """Generate the OCI repository name for plugin metadata."""
    return f"plugin-metadata-{plugin.type}-{plugin.subtype}"


METADATA_INDEX_KEY = "plugin-metadata"


def update_plugin_index_with_plugin(args, plugin: PluginType) -> None:
    """Update the global plugin metadata index with a new or updated plugin."""
    oci_repo_name = get_plugin_registry_name(plugin)
    registry = OCIRegistry(args)

    plugin_metadata = {
        "name": plugin.name,
        "type": plugin.type,
        "subtype": plugin.subtype,
        "metadata": plugin.metadata,
    }

    metadata = registry.get_data(METADATA_INDEX_KEY, "latest")
    if metadata is not None:
        existing_data = metadata.get("plugins", {})
        if not isinstance(existing_data, dict):
            metadata["plugins"] = {}
        elif metadata["plugins"].get(oci_repo_name) == plugin_metadata:
            return
    else:
        metadata = {"plugins": {}}

    metadata["plugins"][oci_repo_name] = plugin_metadata
    raw_metadata = orjson.dumps(metadata)

    registry.upload_object(METADATA_INDEX_KEY, raw_metadata, ["latest"])


def update_plugin_index(args) -> None:
    """Update the plugin index for the plugin specified in args."""
    plugin = get_plugin(args.plugin_path)
    update_plugin_index_with_plugin(args, plugin)


def format_plugin(metadata: dict) -> None:
    """Print formatted plugin metadata."""
    print(
        f"""Name: {metadata["name"]}
Type: {metadata["type"]}
Subtype: {metadata["subtype"]}
Version: {metadata["version"]}
Image Name: {metadata["image_name"]}
Metadata: {metadata["metadata"]}
"""
    )


def display_dry_run_publish(plugin: PluginType, oci_metadata: dict, args) -> None:
    """Display comprehensive dry-run information for plugin publishing."""
    import json

    oci_repo_name = get_plugin_registry_name(plugin)

    if args.registry_project:
        registry_path = f"{args.registry}/{args.registry_project}/{oci_repo_name}"
    else:
        registry_path = f"{args.registry}/{oci_repo_name}"

    print("=" * 80)
    print("DRY RUN - No changes will be made to the registry")
    print("=" * 80)
    print()

    print("Plugin:")
    print(f"  Name:     {plugin.name}")
    print(f"  Type:     {plugin.type}")
    print(f"  Subtype:  {plugin.subtype}")
    print(f"  Version:  {plugin.version}")
    print()

    print("Registry:")
    print(f"  Path:     {registry_path}")
    print(f"  Tags:     {args.channel}, {plugin.version}")
    print()

    overrides_applied = get_applied_overrides(args)
    if overrides_applied:
        print("Overrides:")
        for field, value in overrides_applied:
            print(f"  {field}: {value}")
        print()

    print("Metadata:")
    formatted_json = json.dumps(oci_metadata, indent=2, ensure_ascii=False)
    print(formatted_json)
    print()

    print("=" * 80)
    print("To publish, run without --dry-run")
    print("=" * 80)


def get_plugin_metadata_from_plugin(plugin: PluginType) -> dict:
    """Extract plugin metadata including JSON schema for settings."""
    oci_metadata = plugin.model_dump()
    if isinstance(plugin.settings, dict):
        oci_metadata["settings"] = plugin.settings
    else:
        oci_metadata["settings"] = generate_json_schema(plugin.settings)
    return oci_metadata


def get_plugin_metadata(args) -> dict:
    """Load plugin from args and extract its metadata."""
    plugin = get_plugin(args.plugin_path)
    return get_plugin_metadata_from_plugin(plugin)


def test_action(args) -> None:
    """Test that a plugin manifest is valid and can be serialized."""
    get_plugin_metadata(args)
    metadata = get_plugin_metadata(args)
    orjson.dumps(metadata)
    print("Plugin defined correctly")
    format_plugin(metadata)


def publish_action(args) -> None:
    """Publish a plugin manifest to the registry."""
    overrides = build_overrides(args)

    base_plugin = get_plugin(args.plugin_path)
    plugin = apply_metadata_overrides(base_plugin, overrides) if overrides else base_plugin

    oci_metadata = get_plugin_metadata_from_plugin(plugin)

    if args.dry_run:
        display_dry_run_publish(plugin, oci_metadata, args)
        return

    update_plugin_index_with_plugin(args, plugin)

    oci_repo_name = get_plugin_registry_name(plugin)
    oci_metadata_json = orjson.dumps(oci_metadata)

    print(f"Publishing {plugin.name} to {args.channel} channel")
    registry = OCIRegistry(args)
    registry.upload_object(oci_repo_name, oci_metadata_json, [args.channel, plugin.version])


def list_action(args) -> None:
    """List all tags for a plugin in the registry."""
    plugin = get_plugin(args.plugin_path)
    oci_repo_name = get_plugin_registry_name(plugin)

    registry = OCIRegistry(args)
    tags = registry.list_tags(oci_repo_name)
    print("Found tags:")
    for tag in tags:
        print(f" - {tag}")


def get_action(args) -> None:
    """Get and display plugin metadata from all channels in the registry."""
    plugin = get_plugin(args.plugin_path)
    oci_repo_name = get_plugin_registry_name(plugin)
    registry = OCIRegistry(args)
    tags = registry.list_tags(oci_repo_name)

    for tag in tags:
        if "." in tag:
            continue
        metadata = registry.get_data(oci_repo_name, tag)
        if metadata is not None:
            tag_name = f"Tag: {tag}"
            print(tag_name)
            print("=" * len(tag_name))
            format_plugin(metadata)


def version_action(args) -> None:
    """Print the version of a plugin from its manifest."""
    plugin = get_plugin(args.plugin_path)
    print(plugin.version)


def promote_action(args) -> None:
    """Promote a plugin from one channel to another (e.g., dev -> staging)."""
    plugin = get_plugin(args.plugin_path)
    registry = OCIRegistry(args)
    oci_repo_name = get_plugin_registry_name(plugin)
    registry.copy_tag(oci_repo_name, args.from_channel, args.channel)
    print(f"Promoted {args.from_channel} -> {args.channel}")


def delete_action(args) -> None:
    """Delete a plugin from the global plugin index."""
    plugin = get_plugin(args.plugin_path)
    registry = OCIRegistry(args)
    oci_repo_name = get_plugin_registry_name(plugin)

    if input("Are you sure you want to delete this plugin? (y/n): ") != "y":
        return

    metadata = registry.get_data(METADATA_INDEX_KEY, "latest")
    if oci_repo_name in metadata["plugins"]:
        del metadata["plugins"][oci_repo_name]
    else:
        return

    raw_metadata = orjson.dumps(metadata)
    registry.upload_object(METADATA_INDEX_KEY, raw_metadata, ["latest"])


def new_action(args) -> None:
    """Create a new plugin from the cookiecutter template."""
    if not shutil.which("cookiecutter"):
        print("Please install cookiecutter to use this command: `pip install cookiecutter`")
        return

    from cookiecutter.main import cookiecutter

    path = os.path.join(os.path.dirname(__file__), "plugin_cookiecutter")
    cookiecutter(path)


def main() -> None:
    args = parser.parse_args()

    if args.dry_run and args.cli_action != "publish":
        print("Error: --dry-run flag can only be used with 'publish' action")
        print(f"Got: {args.cli_action}")
        parser.exit(1)

    if args.cli_action == "new":
        new_action(args)
    elif args.cli_action == "publish":
        publish_action(args)
    elif args.cli_action == "list":
        list_action(args)
    elif args.cli_action == "get":
        get_action(args)
    elif args.cli_action == "test":
        test_action(args)
    elif args.cli_action == "version":
        version_action(args)
    elif args.cli_action == "promote":
        promote_action(args)
    elif args.cli_action == "delete":
        delete_action(args)
    else:
        print("Invalid action")


if __name__ == "__main__":
    main()
