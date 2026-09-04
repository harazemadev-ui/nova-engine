from src.errors.error_codes import ErrorCode
from src.errors.nova_error import NovaError


error = NovaError(
    code=ErrorCode.PROVIDER_NOT_FOUND,
    message="Provider 'lumialit' was not found",
    source="provider_loader",
    status_code=404,
    details={
        "provider": "lumialit",
        "version": "1.0.0"
    }
)

print("ERROR:", error)
print("DICT:", error.to_dict())
