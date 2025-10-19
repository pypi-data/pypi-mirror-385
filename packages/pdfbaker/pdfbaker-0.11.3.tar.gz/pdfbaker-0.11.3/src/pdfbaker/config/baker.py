"""Baker configuration for pdfbaker."""

import tempfile
from pathlib import Path
from typing import Any

from pydantic import model_validator
from ruamel.yaml import YAML

from . import BaseConfig, PathSpec

DEFAULT_DIRECTORIES = {
    "build": None,
    "dist": "dist",
    "documents": ".",
    "pages": "pages",
    "templates": "templates",
    "images": "images",
}


class BakerConfig(BaseConfig):
    """Baker configuration.

    Lazy-loads document configs.
    """

    config_file: Path
    documents: list[PathSpec]

    @model_validator(mode="before")
    @classmethod
    def load_config(cls, data: Any) -> Any:
        """Load main configuration from YAML file."""
        if isinstance(data, dict) and "config_file" in data:
            if isinstance(data["config_file"], str):
                data["config_file"] = Path(data["config_file"])
            if isinstance(data["config_file"], Path):
                data["config_file"] = data["config_file"].resolve()

            config_data = YAML().load(data["config_file"].read_text())
            data = BaseConfig.deep_merge_dicts(data, config_data)

            # Set default directories
            if "directories" not in data:
                data["directories"] = {}
            directories = data["directories"]
            directories.setdefault("base", data["config_file"].parent)
            for key, default in DEFAULT_DIRECTORIES.items():
                directories.setdefault(key, default)

            # If build dir is not set, use a temp dir
            if not directories.get("build"):
                directories["build"] = tempfile.mkdtemp(prefix="pdfbaker-")

            if "documents" not in data:
                raise ValueError(
                    'Key "documents" missing - is this the main configuration file?'
                )

        return data

    @model_validator(mode="after")
    def resolve_paths(self) -> "BakerConfig":
        """Resolve relative paths."""
        self.directories.documents = self.resolve_path(self.directories.documents)
        self.directories.build = self.resolve_path(self.directories.build)
        self.directories.dist = self.resolve_path(self.directories.dist)
        self.documents = [
            doc.resolve_relative_to(self.directories.documents)
            for doc in self.documents
        ]

        return self

    @property
    def document_settings(self) -> dict[str, Any]:
        """All configuration settings relevant for a document."""
        return self.model_dump(exclude={"config_file", "documents"})
