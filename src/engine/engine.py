import importlib.util
import json
import sys
from pathlib import Path

from .request import NovaRequest
from .response import NovaResponse


MODULE_FOLDER_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "module"
)


class NovaEngine:

    def __init__(self):
        pass

    def process(self, request: NovaRequest) -> NovaResponse | None:
        module = self.load_module(request)

        if module is None:
            return None

        result = self.execute_module(module, request)

        return self.generate_response(result)

    def load_module(self, request: NovaRequest):

        module_path = MODULE_FOLDER_PATH / request.module

        if not module_path.exists():
            print(f"Module does not exist: {module_path}")
            return None

        version_path = self.load_version(
            module_path,
            request.version
        )

        if version_path is None:
            return None

        module_json = version_path / "module.json"

        try:
            with open(module_json, "r") as file:
                module_data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Failed to read module.json: {error}")
            return None

        module_entry = version_path / module_data["entry"]

        if not module_entry.exists():
            print(f"Module entry does not exist: {module_entry}")
            return None

        module_name = (
            f"nova_module_{request.module}_{request.version}"
        )

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_entry
        )

        if spec is None or spec.loader is None:
            print(f"Could not load module: {module_entry}")
            return None

        loaded_module = importlib.util.module_from_spec(spec)

        if str(version_path) not in sys.path:
            sys.path.insert(0, str(version_path))

        spec.loader.exec_module(loaded_module)

        return loaded_module

    def load_version(self, module: Path, version: str) -> Path | None:

        version_path = module / version

        if not version_path.exists():
            print(f"Version {version} is not available")
            return None

        if not version_path.is_dir():
            print(f"Version path is not a directory: {version_path}")
            return None

        module_json = version_path / "module.json"

        if not module_json.exists():
            print(f"module.json not found: {module_json}")
            return None

        try:
            with open(module_json, "r") as file:
                module_data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Failed to read module.json: {error}")
            return None

        module_version = module_data.get("version")

        if module_version != version:
            print(
                f"Version mismatch: requested {version}, "
                f"found {module_version}"
            )
            return None

        return version_path

    def execute_module(
        self,
        module,
        request: NovaRequest
    ):
        if not hasattr(module, "generate"):
            print(
                "Loaded module does not have a "
                "'generate' function."
            )
            return None

        module_context = request.create_module_context()

        return module.generate(module_context)

    def generate_response(
        self,
        result
    ) -> NovaResponse | None:

        if result is None:
            return None

        return NovaResponse(result.response)

    def stream(self, request: NovaRequest):
        module = self.load_module(request)

        if module is None:
            return

        if not hasattr(module, "generate_stream"):
            print(
                "Loaded module does not have a "
                "'generate_stream' function."
            )
            return

        module_context = request.create_module_context()

        yield from module.generate_stream(module_context)
