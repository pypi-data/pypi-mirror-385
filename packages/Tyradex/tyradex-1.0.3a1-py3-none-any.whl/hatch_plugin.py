import json
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    """
    Metadata hook that injects project metadata from an external metadata.json file.

    This hook reads metadata such as name, version, description, and authors
    from a JSON file and applies them to the project configuration.
    """

    def update(self, metadata):
        """
        Update the metadata dictionary with the necessary fields from the metadata.json file.

        Args:
            metadata (dict): The metadata dictionary to update. It is typically the metadata passed during the build process.

        Raises:
            FileNotFoundError: If the metadata.json file is not found in the project root.
            ValueError: If any of the required fields ('name', 'version', 'description', 'authors') are missing in the metadata.json.
        """
        metadata_file = Path(self.root) / "metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError("Metadata file not found at: {metadata_file}".format(metadata_file=metadata_file))

        with metadata_file.open(encoding="utf-8") as f:
            meta = json.load(f)

        required_fields = ["name", "version", "description", "authors"]
        for field in required_fields:
            if field not in meta:
                raise ValueError("Missing required field '{field}' in metadata.json".format(field=field))

        metadata["name"] = meta["name"]
        metadata["version"] = meta["version"]
        metadata["description"] = meta["description"]
        metadata["authors"] = meta["authors"]


class CustomBuildHook(BuildHookInterface):
    """
    Build hook that copies metadata.json into the Tyradex package folder
    during the build process and removes it after build is complete.
    """

    def initialize(self, version, build_data):
        """
        Copy the metadata.json file into the Tyradex package before build.

        Args:
            version (str): The version of the package.
            build_data (dict[str, Any]): The metadata for the build process.
        """
        source_file = Path(self.root) / "metadata.json"
        destination_file = Path(self.root) / "Tyradex" / "metadata.json"

        if not source_file.exists():
            raise FileNotFoundError("metadata.json not found at: {source_file}".format(source_file=source_file))

        destination_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        self._copied_file = destination_file

    def finalize(self, version, build_data, artifact_path):
        """
        Clean the metadata.json file after the build process.

        Args:
            version (str): The version of the package.
            build_data (dict[str, Any]): The metadata for the build process.
            artifact_path (str): Path to the built artifact (tar.gz / wheel).
        """
        if hasattr(self, "_copied_file") and self._copied_file.exists():
            self._copied_file.unlink()
