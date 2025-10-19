"""
Standardized Response Handler
Modern response handling with enums and type safety
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ResponseStatus(Enum):
    """Response status enumeration"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ErrorCode(Enum):
    """Common error codes"""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    BAD_REQUEST = "bad_request"

class StandardResponse(BaseModel):
    """Standard response model"""
    status: ResponseStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    
    class Config:
        use_enum_values = True


class ResponseHandler:
    """Standardize edilmiş response handler"""
    
    def __init__(self):
        self._error_codes = self._load_json("error.json")
        self._success_codes = self._load_json("success.json")
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """JSON dosyasını yükler"""
        try:
            script_dir = Path(__file__).resolve().parent
            file_path = script_dir / filename
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return {}
    
    def get_error(self, category: str, error_code: str) -> Dict[str, Any]:
        """Error bilgisini getirir"""
        try:
            return self._error_codes[category][error_code]
        except KeyError:
            logger.warning(f"Error code not found: {category}.{error_code}")
            return {
                "status": 500,
                "message": "Beklenmedik sistem hatası"
            }
    
    def get_success(self, category: str, success_code: str) -> Dict[str, Any]:
        """Success bilgisini getirir"""
        try:
            return self._success_codes[category][success_code]
        except KeyError:
            logger.warning(f"Success code not found: {category}.{success_code}")
            return {
                "status": 200,
                "message": "İşlem başarıyla tamamlandı"
            }
    
    def raise_error(
        self, 
        category: str, 
        error_code: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Standardize edilmiş HTTP exception fırlatır"""
        error_info = self.get_error(category, error_code)
        
        detail = {
            "error_code": f"{category}.{error_code}",
            "message": error_info["message"]
        }
        
        if details:
            detail["details"] = details
        
        raise HTTPException(
            status_code=error_info["status"],
            detail=detail
        )
    
    def success_response(
        self,
        category: str,
        success_code: str,
        data: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Standardize edilmiş success response döndürür"""
        success_info = self.get_success(category, success_code)
        
        response_data = {
            "success": True,
            "message": success_info["message"],
            "code": f"{category}.{success_code}"
        }
        
        if data:
            response_data["data"] = data
        
        if extra:
            response_data.update(extra)
        
        return JSONResponse(
            status_code=success_info["status"],
            content=response_data
        )
    
    def error_response(
        self,
        category: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Standardize edilmiş error response döndürür"""
        error_info = self.get_error(category, error_code)
        
        response_data = {
            "success": False,
            "error_code": f"{category}.{error_code}",
            "message": error_info["message"]
        }
        
        if details:
            response_data["details"] = details
        
        return JSONResponse(
            status_code=error_info["status"],
            content=response_data
        )


# Global response handler instance
response_handler = ResponseHandler()


# Convenience functions for common error categories
class AuthErrors:
    """Authentication error helper"""
    
    @staticmethod
    def invalid_credentials(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_INVALID_CREDENTIALS", details)
    
    @staticmethod
    def token_missing(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_TOKEN_MISSING", details)
    
    @staticmethod
    def token_invalid(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_TOKEN_INVALID", details)
    
    @staticmethod
    def token_expired(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_TOKEN_EXPIRED", details)
    
    @staticmethod
    def unauthorized(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_UNAUTHORIZED", details)
    
    @staticmethod
    def provider_error(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_PROVIDER_ERROR", details)
    
    @staticmethod
    def recaptcha_failed(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_RECAPTCHA_FAILED", details)
    
    @staticmethod
    def email_not_verified(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("AUTH", "AUTH_EMAIL_NOT_VERIFIED", details)


class ApiKeyErrors:
    """API Key error helper"""
    
    @staticmethod
    def missing(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_MISSING", details)
    
    @staticmethod
    def invalid(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_INVALID", details)
    
    @staticmethod
    def revoked(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_REVOKED", details)
    
    @staticmethod
    def expired(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_EXPIRED", details)
    
    @staticmethod
    def scope_denied(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_SCOPE_DENIED", details)
    
    @staticmethod
    def tenant_mismatch(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("API_KEY", "API_KEY_TENANT_MISMATCH", details)


class TenantErrors:
    """Tenant error helper"""
    
    @staticmethod
    def not_found(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "TENANT_NOT_FOUND", details)
    
    @staticmethod
    def disabled(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "TENANT_DISABLED", details)
    
    @staticmethod
    def user_not_found(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "USER_NOT_FOUND", details)
    
    @staticmethod
    def user_already_exists(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "USER_ALREADY_EXISTS", details)
    
    @staticmethod
    def user_not_active(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "USER_NOT_ACTIVE", details)
    
    @staticmethod
    def permission_denied(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("TENANT", "USER_PERMISSION_DENIED", details)


class SecurityErrors:
    """Security error helper"""
    
    @staticmethod
    def rate_limit(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SECURITY", "SECURITY_RATE_LIMIT", details)
    
    @staticmethod
    def ip_blocked(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SECURITY", "SECURITY_IP_BLOCKED", details)
    
    @staticmethod
    def suspicious_activity(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SECURITY", "SECURITY_SUSPICIOUS_ACTIVITY", details)
    
    @staticmethod
    def forbidden(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SECURITY", "SECURITY_FORBIDDEN", details)


class ResourceErrors:
    """Resource error helper"""
    
    @staticmethod
    def not_found(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("RESOURCE", "RESOURCE_NOT_FOUND", details)
    
    @staticmethod
    def already_exists(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("RESOURCE", "RESOURCE_ALREADY_EXISTS", details)
    
    @staticmethod
    def locked(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("RESOURCE", "RESOURCE_LOCKED", details)
    
    @staticmethod
    def validation_error(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("RESOURCE", "RESOURCE_VALIDATION_ERROR", details)
    
    @staticmethod
    def quota_exceeded(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("RESOURCE", "RESOURCE_QUOTA_EXCEEDED", details)


class SystemErrors:
    """System error helper"""
    
    @staticmethod
    def maintenance(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SYSTEM", "SYSTEM_MAINTENANCE", details)
    
    @staticmethod
    def internal_error(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SYSTEM", "SYSTEM_ERROR", details)
    
    @staticmethod
    def dependency_error(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SYSTEM", "SYSTEM_DEPENDENCY_ERROR", details)
    
    @staticmethod
    def timeout(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SYSTEM", "SYSTEM_TIMEOUT", details)
    
    @staticmethod
    def not_implemented(details: Optional[Dict[str, Any]] = None):
        response_handler.raise_error("SYSTEM", "SYSTEM_NOT_IMPLEMENTED", details)


class SuccessResponses:
    """Success response helper"""
    
    @staticmethod
    def ok(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("GENERAL", "SUCCESS_OK", data, extra)
    
    @staticmethod
    def created(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("GENERAL", "SUCCESS_CREATED", data, extra)
    
    @staticmethod
    def accepted(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("GENERAL", "SUCCESS_ACCEPTED", data, extra)
    
    @staticmethod
    def no_content():
        return response_handler.success_response("GENERAL", "SUCCESS_NO_CONTENT")
    
    @staticmethod
    def login_success(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("USER", "SUCCESS_LOGIN", data, extra)
    
    @staticmethod
    def logout_success(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("USER", "SUCCESS_LOGOUT", data, extra)
    
    @staticmethod
    def user_updated(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("USER", "SUCCESS_UPDATED", data, extra)
    
    @staticmethod
    def user_deleted(data: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        return response_handler.success_response("USER", "SUCCESS_DELETED", data, extra)


# Test function
def _test_response_handler():
    """Test response handler functionality"""
    print("🧪 Testing Response Handler...")
    
    try:
        # Test error loading
        error_info = response_handler.get_error("AUTH", "AUTH_INVALID_CREDENTIALS")
        print(f"✅ Error loaded: {error_info}")
        
        # Test success loading
        success_info = response_handler.get_success("USER", "SUCCESS_LOGIN")
        print(f"✅ Success loaded: {success_info}")
        
        # Test error helpers
        try:
            AuthErrors.invalid_credentials({"email": "test@example.com"})
        except HTTPException as e:
            print(f"✅ Auth error raised: {e.status_code} - {e.detail}")
        
        # Test success response
        response = SuccessResponses.login_success(
            data={"user_id": "123", "token": "abc"},
            extra={"expires_in": 3600}
        )
        print(f"✅ Success response: {response.status_code}")
        
        print("✅ Response Handler Test Completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# Global response functions

def create_success_response(
    message: str = "Operation successful",
    data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized success response"""
    response = StandardResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        timestamp=datetime.utcnow().isoformat()
    )
    return JSONResponse(
        status_code=200,
        content=response.dict()
    )

def create_error_response(
    message: str,
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    status_code: int = 500,
    data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response"""
    response = StandardResponse(
        status=ResponseStatus.ERROR,
        message=message,
        error_code=error_code.value,
        data=data,
        timestamp=datetime.utcnow().isoformat()
    )
    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )

def create_validation_error_response(
    message: str = "Validation failed",
    errors: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized validation error response"""
    return create_error_response(
        message=message,
        error_code=ErrorCode.VALIDATION_ERROR,
        status_code=422,
        data={"errors": errors} if errors else None
    )

if __name__ == "__main__":
    _test_response_handler()
