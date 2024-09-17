import base64
from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class Crypto:
    def generate_key(password, salt):
        kdf = pbkdf2_hmac(
            algorithm=hashes.SHA256(),
            iterations=100000,
            salt=salt,
            length=32,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def decrypt_data(self, encrypted_data, key):
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return decrypted_data

    def encrypt_data(self, data, key):
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data.encode())
        return encrypted_data