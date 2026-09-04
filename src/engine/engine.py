from importlib.util import module_from_spec, spec_from_file_location
import json
import sys
from pathlib import Path

from .request import NovaRequest
from .response import NovaResponse

from ..errors.nova_error import NovaError
from ..errors.error_codes import ErrorCode
from ..providerdata.providerresult import ProviderResult
from ..manager.context.context_manager import NovaContextManager


# ============================================================
# PROVIDER DIRECTORY
# ============================================================

PROVIDER_FOLDER_PATH = (
    Path(__file__).resolve()
    .parent.parent
    / "provider"
)


# ============================================================
# NOVA ENGINE
# ============================================================

class NovaEngine:

    def __init__(self):
        self.context_manager = NovaContextManager()
        self.memory_manager = self.context_manager.memory_manager

    # ========================================================
    # PROCESS REQUEST
    # ========================================================

    def process(
        self,
        request: NovaRequest
    ) -> NovaResponse | None:

        # --------------------------------------------------------
        # LOAD PRIMARY PROVIDER
        # --------------------------------------------------------

        provider = self.load_provider(request)

        try:

            result = self.execute_provider(
                provider,
                request
            )

        # --------------------------------------------------------
        # PRIMARY PROVIDER FAILED
        # --------------------------------------------------------

        except NovaError as primary_error:

            print(
                f"Primary provider '{request.provider}' failed:"
                f" {primary_error}"
            )

            # ----------------------------------------------------
            # LOAD FALLBACK PROVIDER
            # ----------------------------------------------------

            try:

                fallback_provider = self.load_provider(
                    request,
                    provider_name="openrouter"
                )

                result = self.execute_provider(
                    fallback_provider,
                    request
                )

            # ----------------------------------------------------
            # FALLBACK PROVIDER FAILED
            # ----------------------------------------------------

            except NovaError as fallback_error:

                print(
                    "Fallback provider 'openrouter' failed:"
                    f" {fallback_error}"
                )

                raise NovaError(
                    code=ErrorCode.PROVIDER_EXECUTION_FAILED,
                    message="All available AI providers failed.",
                    source="provider_manager",
                    status_code=503,
                    details={
                        "primary_provider": request.provider,
                        "fallback_provider": "openrouter"
                    }
                ) from fallback_error

        return self.generate_response(result)

    # ========================================================
    # LOAD PROVIDER
    # ========================================================

    def load_provider(
        self,
        request: NovaRequest,
        provider_name: str | None = None
    ):

        provider = (
            provider_name
            if provider_name is not None
            else request.provider
        )

        provider_path = (
            PROVIDER_FOLDER_PATH
            / provider
        )

        # ----------------------------------------------------
        # PROVIDER DOES NOT EXIST
        # ----------------------------------------------------

        if not provider_path.exists():

            raise NovaError(
                code=ErrorCode.PROVIDER_NOT_FOUND,
                message="Provider does not exist",
                source="provider_loader",
                status_code=404,
                details={
                    "provider": provider
                }
            )

        # ----------------------------------------------------
        # LOAD PROVIDER VERSION
        # ----------------------------------------------------

        version_path = self.load_version(
            provider_path,
            request.version
        )

        # ----------------------------------------------------
        # READ PROVIDER CONFIGURATION
        # ----------------------------------------------------

        provider_json = (
            version_path
            / "provider.json"
        )

        try:

            with open(
                provider_json,
                "r"
            ) as file:

                provider_data = json.load(file)

        except OSError as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="Failed to read provider.json",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider,
                    "version": request.version,
                    "error": str(error)
                }
            ) from error

        except json.JSONDecodeError as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="provider.json contains invalid JSON",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider,
                    "version": request.version,
                    "error": str(error)
                }
            ) from error

        # ----------------------------------------------------
        # GET PROVIDER ENTRY
        # ----------------------------------------------------

        try:

            provider_entry = (
                version_path
                / provider_data["entry"]
            )

        except KeyError as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="provider.json is missing the 'entry' field",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider,
                    "version": request.version,
                    "required_field": "entry"
                }
            ) from error

        # ----------------------------------------------------
        # PROVIDER ENTRY DOES NOT EXIST
        # ----------------------------------------------------

        if not provider_entry.exists():

            raise NovaError(
                code=ErrorCode.PROVIDER_ENTRY_NOT_FOUND,
                message="Provider entry does not exist",
                source="provider_loader",
                status_code=404,
                details={
                    "provider": provider,
                    "version": request.version,
                    "provider_entry": str(provider_entry)
                }
            )

        # ----------------------------------------------------
        # CREATE MODULE SPECIFICATION
        # ----------------------------------------------------

        module_name = (
            f"nova_provider_"
            f"{provider}_"
            f"{request.version}"
        )

        spec = spec_from_file_location(
            module_name,
            provider_entry
        )

        if (
            spec is None
            or spec.loader is None
        ):

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="Could not create provider module loader",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider,
                    "version": request.version,
                    "provider_entry": str(provider_entry)
                }
            )

        # ----------------------------------------------------
        # CREATE MODULE
        # ----------------------------------------------------

        loaded_provider = (
            module_from_spec(spec)
        )

        # ----------------------------------------------------
        # ADD PROVIDER VERSION TO PYTHON PATH
        # ----------------------------------------------------

        if str(version_path) not in sys.path:

            sys.path.insert(
                0,
                str(version_path)
            )

        # ----------------------------------------------------
        # EXECUTE PROVIDER MODULE
        # ----------------------------------------------------

        try:

            spec.loader.exec_module(
                loaded_provider
            )

        except Exception as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="Failed to load provider module",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider,
                    "version": request.version,
                    "provider_entry": str(provider_entry),
                    "error": str(error)
                }
            ) from error

        return loaded_provider

    # ========================================================
    # LOAD PROVIDER VERSION
    # ========================================================

    def load_version(
        self,
        provider: Path,
        version: str
    ) -> Path:

        version_path = (
            provider
            / version
        )

        # ----------------------------------------------------
        # VERSION DOES NOT EXIST
        # ----------------------------------------------------

        if not version_path.exists():

            raise NovaError(
                code=ErrorCode.PROVIDER_VERSION_NOT_FOUND,
                message=f"Provider version {version} is not available",
                source="provider_loader",
                status_code=404,
                details={
                    "provider": provider.name,
                    "version": version,
                    "version_path": str(version_path)
                }
            )

        # ----------------------------------------------------
        # VERSION PATH IS NOT A DIRECTORY
        # ----------------------------------------------------

        if not version_path.is_dir():

            raise NovaError(
                code=ErrorCode.PROVIDER_VERSION_IS_NOT_A_DIRECTORY,
                message="Provider version path is not a directory",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider.name,
                    "version": version,
                    "version_path": str(version_path)
                }
            )

        # ----------------------------------------------------
        # PROVIDER.JSON DOES NOT EXIST
        # ----------------------------------------------------

        provider_json = (
            version_path
            / "provider.json"
        )

        if not provider_json.exists():

            raise NovaError(
                code=ErrorCode.PROVIDER_VERSION_JSON_NOT_FOUND,
                message="provider.json was not found",
                source="provider_loader",
                status_code=404,
                details={
                    "provider": provider.name,
                    "version": version,
                    "provider_json": str(provider_json)
                }
            )

        # ----------------------------------------------------
        # READ PROVIDER.JSON
        # ----------------------------------------------------

        try:

            with open(
                provider_json,
                "r"
            ) as file:

                provider_data = json.load(file)

        except OSError as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="Failed to read provider.json",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider.name,
                    "version": version,
                    "provider_json": str(provider_json),
                    "error": str(error)
                }
            ) from error

        except json.JSONDecodeError as error:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="provider.json contains invalid JSON",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider.name,
                    "version": version,
                    "provider_json": str(provider_json),
                    "error": str(error)
                }
            ) from error

        # ----------------------------------------------------
        # CHECK VERSION
        # ----------------------------------------------------

        provider_version = (
            provider_data.get("version")
        )

        if provider_version != version:

            raise NovaError(
                code=ErrorCode.PROVIDER_LOAD_FAILED,
                message="Provider version does not match requested version",
                source="provider_loader",
                status_code=500,
                details={
                    "provider": provider.name,
                    "requested_version": version,
                    "found_version": provider_version
                }
            )

        return version_path

    # ========================================================
    # EXECUTE PROVIDER
    # ========================================================

    def execute_provider(
        self,
        provider,
        request: NovaRequest
    ) -> ProviderResult | None:

        # ----------------------------------------------------
        # CHECK GENERATE FUNCTION
        # ----------------------------------------------------

        if not hasattr(
            provider,
            "generate"
        ):

            raise NovaError(
                code=ErrorCode.PROVIDER_INVALID,
                message="Loaded provider does not have a 'generate' function",
                source="provider_executor",
                status_code=500,
                details={
                    "required_function": "generate"
                }
            )

        # ----------------------------------------------------
        # CREATE PROVIDER CONTEXT
        # ----------------------------------------------------

        provider_context = (
            self.context_manager.create_provider_context(
                message=request.message,
                userUID=request.userUID,
                chatUID=request.chatUID
            )
        )

        print(
            f"""provider context Data =
                   provider context chatUID = {provider_context.chatUID}
                   provider context userUID = {provider_context.userUID}
                   provider context message = {provider_context.message}
             """
        )

        # ----------------------------------------------------
        # GENERATE RESPONSE
        # ----------------------------------------------------

        result = provider.generate(
            provider_context
        )

        if result is None:
            return None

        # ----------------------------------------------------
        # PROCESS MEMORY ACTIONS
        # ----------------------------------------------------

        for action in result.memory_actions:

            action_type = action.get(
                "action"
            )

            # ------------------------------------------------
            # CREATE MEMORY
            # ------------------------------------------------

            if action_type == "create":

                self.memory_manager.create_memory(

                    user_uid=request.userUID,

                    chat_uid=action.get(
                        "chatUID"
                    ),

                    memory_type=action.get(
                        "type"
                    ),

                    key=action.get(
                        "key"
                    ),

                    content=action.get(
                        "content"
                    )
                )

                print(
                    f"Memory created: "
                    f"{action.get('key')}"
                )

            # ------------------------------------------------
            # UPDATE MEMORY
            # ------------------------------------------------

            elif action_type == "update":

                self.memory_manager.update_memory(

                    memory_uid=action.get(
                        "memoryUID"
                    ),

                    content=action.get(
                        "content"
                    ),

                    key=action.get(
                        "key"
                    ),

                    memory_type=action.get(
                        "type"
                    )
                )

                print(
                    f"Memory updated: "
                    f"{action.get('memoryUID')}"
                )

            # ------------------------------------------------
            # DELETE MEMORY
            # ------------------------------------------------

            elif action_type == "delete":

                self.memory_manager.delete_memory(
                    action.get(
                        "memoryUID"
                    )
                )

                print(
                    f"Memory deleted: "
                    f"{action.get('memoryUID')}"
                )

            # ------------------------------------------------
            # UNKNOWN ACTION
            # ------------------------------------------------

            else:

                print(
                    f"Unknown memory action: "
                    f"{action_type}"
                )

        return result

    # ========================================================
    # GENERATE NOVA RESPONSE
    # ========================================================

    def generate_response(
        self,
        result: ProviderResult | None
    ) -> NovaResponse | None:

        if result is None:
            return None

        return NovaResponse(
            result.response
        )
