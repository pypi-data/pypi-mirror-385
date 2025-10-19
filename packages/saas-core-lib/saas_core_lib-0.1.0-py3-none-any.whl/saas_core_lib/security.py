
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional, Dict, Any
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import get_settings, Settings

class SecurityManager:
    """
    Provides a suite of security-related services including password hashing,
    JWT management, API key handling, and one-time token generation.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        
        # Password Hashing with explicit bcrypt configuration
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12  # Explicit rounds setting to avoid version issues
        )

        # JWT Settings
        self.SECRET_KEY = self.settings.JWT_SECRET
        self.ALGORITHM = self.settings.JWT_ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_DAYS = self.settings.JWT_EXPIRE_DAYS
        self.REFRESH_TOKEN_EXPIRE_MINUTES = self.settings.REFRESH_TOKEN_EXPIRE_MINUTES
        self.JWT_AUDIENCE = self.settings.JWT_AUDIENCE
        self.JWT_ISSUER = self.settings.JWT_ISSUER

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Düz metin şifreyi, hashlenmiş versiyonu ile doğrular."""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except (ValueError, TypeError):
            return False

    def get_password_hash(self, password: str) -> str:
        """Düz metin şifreyi hashler."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Yeni bir JWT access token oluşturur.
        'sub' (subject) alanı genellikle kullanıcı ID'sini içerir.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": self.JWT_ISSUER,
            "aud": self.JWT_AUDIENCE,
            "token_type": "access",
        })
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Yeni bir JWT refresh token oluşturur."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": self.JWT_ISSUER,
            "aud": self.JWT_AUDIENCE,
            "token_type": "refresh",
        })
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Bir JWT token'ını çözer ve payload'u döndürür.
        Doğrulama başarısız olursa None döner.
        """
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],
                audience=self.JWT_AUDIENCE,
                issuer=self.JWT_ISSUER,
                options={"verify_exp": True, "verify_aud": True, "verify_iss": True},
            )
            return payload
        except JWTError:
            return None

    def generate_api_key(self, length: int = 32) -> str:
        """Güvenli ve URL-safe bir API anahtarı üretir."""
        return secrets.token_urlsafe(length)

    def get_api_key_hash(self, api_key: str) -> str:
        """
        Bir API anahtarını, şifrelerle aynı güvenli yöntemle hashler.
        Bu, API anahtarlarının veritabanında güvenli bir şekilde saklanmasını sağlar.
        """
        return self.pwd_context.hash(api_key)

    def verify_api_key(self, plain_key: str, hashed_key: str) -> bool:
        """Düz metin API anahtarını, hashlenmiş versiyonu ile doğrular."""
        try:
            return self.pwd_context.verify(plain_key, hashed_key)
        except (ValueError, TypeError):
            return False

    def generate_verification_token(
        self, 
        subject: str, 
        token_type: str,
        expires_minutes: int = 60
    ) -> str:
        """
        E-posta doğrulama veya şifre sıfırlama gibi işlemler için kısa ömürlü,
        tek amaçlı bir token üretir.
        
        :param subject: Token'ın kiminle ilgili olduğu (örn. user_id veya email).
        :param token_type: Token'ın amacı (örn. 'email_verify', 'password_reset').
        :param expires_minutes: Token'ın geçerlilik süresi (dakika).
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        to_encode = {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": self.JWT_ISSUER,
            "aud": f"{self.JWT_AUDIENCE}:{token_type}",
            "sub": subject,
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_verification_token(self, token: str, expected_token_type: str) -> Optional[str]:
        """
        Tek kullanımlık bir token'ı doğrular ve konusunu (subject) döndürür.
        Token geçersizse veya beklenen türde değilse None döner.
        """
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],
                audience=f"{self.JWT_AUDIENCE}:{expected_token_type}",
                issuer=self.JWT_ISSUER,
            )
            return payload.get("sub")
        except JWTError:
            return None

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Kullanıcı kimlik doğrulaması yapar.
        Bu basit bir mock implementasyon - gerçek uygulamada veritabanından kullanıcı bilgilerini alır.
        """
        # Mock user data - gerçek uygulamada veritabanından gelecek
        mock_users = {
            "admin@hashub.dev": {
                "id": "admin_user_id",
                "email": "admin@hashub.dev",
                "password_hash": self.get_password_hash("admin123"),
                "type": "saas_user",
                "is_super_admin": True,
                "status": "active"
            },
            "test@example.com": {
                "id": "test_user_id",
                "email": "test@example.com",
                "password_hash": self.get_password_hash("test123"),
                "type": "saas_user",
                "is_super_admin": False,
                "status": "active"
            }
        }
        
        # Username olarak email kullanılıyor
        user = mock_users.get(username)
        if not user:
            return None
            
        # Şifre doğrulama
        if not self.verify_password(password, user["password_hash"]):
            return None
            
        # Kullanıcı aktif mi kontrol et
        if user.get("status") != "active":
            return None
            
        # Password hash'i çıkar (güvenlik için)
        user_data = user.copy()
        del user_data["password_hash"]
        
        return user_data

# Global security manager instance

@lru_cache()
def get_security_manager() -> SecurityManager:
    """Get cached security manager instance"""
    return SecurityManager()

# Convenience functions for direct access
def hash_password(password: str) -> str:
    """Hash a password"""
    return get_security_manager().get_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return get_security_manager().verify_password(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    return get_security_manager().create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    return get_security_manager().verify_token(token)
