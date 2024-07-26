from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
import bcrypt

class Hash:
    @staticmethod
    def password_hash(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


class Encrypt:
    @staticmethod
    def encrypt_data(plantext: str, chiper_key: str) -> str:
        chiper_iv = "# Add Your Secret Salt #"

        key = hashlib.sha256(chiper_key.encode()).digest()

        iv = hashlib.sha256(chiper_iv.encode()).digest()[:16]

        encryptor = Cipher(
            algorithms.AES(key), modes.CBC(iv), backend=default_backend()
        ).encryptor()

        plaintext = plantext.encode("utf-8")

        pad_length = 16 - len(plaintext) % 16
        padded_plaintext = plaintext + bytes([pad_length] * pad_length)

        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        ciphertext_base64 = base64.urlsafe_b64encode(ciphertext).rstrip(b"=")

        return ciphertext_base64.decode()

    @staticmethod
    def decrypt_data(chiper_text: str, chiper_key: str) -> str | bool:
        try:
            plaintext_iv = "# Add Your Secret Salt #"

            key = hashlib.sha256(chiper_key.encode()).digest()

            iv = hashlib.sha256(plaintext_iv.encode()).digest()[:16]

            decryptor = Cipher(
                algorithms.AES(key), modes.CBC(iv), backend=default_backend()
            ).decryptor()

            padding_needed = 4 - (len(chiper_text) % 4)
            if padding_needed:
                chiper_text += "=" * padding_needed
            chiper_text = chiper_text.encode()
            decoded_ciphertext = base64.urlsafe_b64decode(chiper_text)

            decrypted_padded_plaintext = (
                decryptor.update(decoded_ciphertext) + decryptor.finalize()
            )

            pad_length = decrypted_padded_plaintext[-1]
            decrypted_plaintext = decrypted_padded_plaintext[:-pad_length]

            return decrypted_plaintext.decode()
        except Exception as _:
            return False