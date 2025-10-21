# Ooga Booga Encryption

A Python module that encrypts any Python data (including scripts) into a sequence of 'ooga', 'booga', 'oga', and 'boga' words and supports decryption and execution.

## Installation
```bash
pip install ooga-booga

#USAGE
from ooga_booga import encrypt, decrypt, encrypt_script_file, execute_encrypted_script

# Encrypt data
data = {"message": "Hello, world!"}
encrypted = encrypt(data)
print(encrypted)

# Decrypt data
decrypted = decrypt(encrypted)
print(decrypted)

# Encrypt a script file
encrypt_script_file("script.py", "encrypted.ooga")

# Execute an encrypted script
with open("encrypted.ooga", "r") as f:
    enc_str = f.read()
result = execute_encrypted_script(enc_str, safe_mode=True)
print(result)