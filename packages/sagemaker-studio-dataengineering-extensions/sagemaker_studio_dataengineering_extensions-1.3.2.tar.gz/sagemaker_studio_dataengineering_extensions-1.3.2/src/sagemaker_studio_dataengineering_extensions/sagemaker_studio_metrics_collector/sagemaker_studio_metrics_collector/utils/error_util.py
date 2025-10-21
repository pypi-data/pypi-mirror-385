ACCESS_DENIED_CODE_PATTERNS = ("AccessDenied", "Access denied", "permission", "Unauthorized", "ValidationException")
UX_ERRORS_BUT_NOT_FAULTS = ("ResourceLimitExceeded", "S3RegionMismatch", "ThrottlingException", "NoSuchBucket", "ResourceNotFound")
CONNECTION_ERROR_CODE_PATTERNS = ("ConnectionError", "ConnectTimeoutError", "EndpointConnectionError", "ProxyConnectionError", "ReadTimeoutError")

class ErrorMatcher:
    def is_fault(self, error_code: str) -> bool:
        """Determine if an error code represents a fault.

        Args:
            error_code: The error code to check

        Returns:
            bool: True if the error is a fault, False otherwise
        """
        if error_code.startswith(ACCESS_DENIED_CODE_PATTERNS + UX_ERRORS_BUT_NOT_FAULTS):
            return False
        elif error_code.startswith(CONNECTION_ERROR_CODE_PATTERNS):
            # For VpcOnly setup we don't treat connection errors as faults
            from .internal_metadata_adapter import InternalMetadataAdapter
            network_access_type = InternalMetadataAdapter().get_app_network_access_type()
            if network_access_type == "VpcOnly":
                return False
        return True
