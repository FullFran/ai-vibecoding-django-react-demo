from django.http import Http404
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Wraps all DRF error responses in the standard envelope:
    {"error": {"code": str, "message": str, "details": dict|None}}

    This handler does NOT add business logic — it only reshapes.
    """
    # Convert Django's Http404 to DRF NotFound so exc has the right attributes
    if isinstance(exc, Http404):
        from rest_framework.exceptions import NotFound
        exc = NotFound(detail=str(exc) or None)

    response = exception_handler(exc, context)
    if response is None:
        return None

    # Determine error code
    code = getattr(exc, "default_code", "error")
    if hasattr(exc, "detail"):
        detail = exc.detail
    else:
        detail = str(exc)

    # Build envelope
    if isinstance(detail, dict):
        # Field-level errors from ValidationError
        message = "Validation failed."
        details = {
            field: (msgs if isinstance(msgs, list) else [str(msgs)])
            for field, msgs in detail.items()
        }
        # Check for custom code in the ValidationError
        if hasattr(exc, "get_codes"):
            codes = exc.get_codes()
            if isinstance(codes, dict):
                for field_codes in codes.values():
                    if isinstance(field_codes, list):
                        for c in field_codes:
                            if c == "invalid_transition":
                                code = "invalid_transition"
                                break
    elif isinstance(detail, list):
        message = " ".join(str(item) for item in detail)
        details = None
    else:
        message = str(detail)
        details = None

    # Map DRF default codes to our API codes
    code_map = {
        "not_found": "not_found",
        "invalid": "validation_error",
        "required": "validation_error",
        "parse_error": "validation_error",
    }
    if code not in ("invalid_transition",):
        code = code_map.get(code, "validation_error")

    envelope = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        envelope["error"]["details"] = details

    response.data = envelope
    return response
