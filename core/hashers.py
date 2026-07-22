import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash

class PlainBCryptPasswordHasher(BasePasswordHasher):
    algorithm = "bcrypt_raw"

    def identify(self, encoded):
        if not encoded:
            return False
        return encoded.startswith('bcrypt_raw$')

    def verify(self, password, encoded):
        if not encoded:
            return False
        if encoded.startswith('bcrypt_raw$'):
            encoded = encoded[len('bcrypt_raw$'):]
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(encoded, str):
            encoded = encoded.encode('utf-8')
        try:
            return bcrypt.checkpw(password, encoded)
        except Exception as e:
            print("BCrypt verify exception:", e)
            return False

    def encode(self, password, salt):
        if isinstance(password, str):
            password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(12))
        return f"bcrypt_raw${hashed.decode('utf-8')}"

    def safe_summary(self, encoded):
        return {
            'algorithm': self.algorithm,
            'work factor': 12,
            'salt': mask_hash(encoded, 10),
            'hash': mask_hash(encoded, 15),
        }
