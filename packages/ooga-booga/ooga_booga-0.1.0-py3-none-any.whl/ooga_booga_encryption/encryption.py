import pickle

# Mapping for 2 bits to words
BIT_TO_WORD = {
    '00': 'ooga',
    '01': 'booga',
    '10': 'oga',
    '11': 'boga'
}

# Reverse mapping
WORD_TO_BIT = {v: k for k, v in BIT_TO_WORD.items()}

def encrypt(data):
    """
    Encrypts any Python data (including scripts) into a string of 'ooga booga' style words.

    Args:
        data: Any Python object (e.g., str, script content, etc.)

    Returns:
        str: Encrypted string with space-separated words.
    """
    try:
        # Serialize to bytes using pickle
        bytes_data = pickle.dumps(data)

        # Convert bytes to binary string
        binary_str = ''.join(f'{byte:08b}' for byte in bytes_data)

        # Group into 2-bit chunks and map to words
        words = []
        for i in range(0, len(binary_str), 2):
            bits = binary_str[i:i+2]
            if len(bits) == 2:  # Ensure 2-bit chunks
                words.append(BIT_TO_WORD[bits])

        return ' '.join(words)
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt(enc_str):
    """
    Decrypts a string of 'ooga booga' style words back to the original Python data.

    Args:
        enc_str: str - The encrypted string with space-separated words.

    Returns:
        The original Python data (e.g., script content).
    """
    try:
        # Split into words
        words = enc_str.split()

        # Map words back to bits
        binary_str = ''
        for word in words:
            if word in WORD_TO_BIT:
                binary_str += WORD_TO_BIT[word]
            else:
                raise ValueError(f"Invalid word '{word}' in encrypted string.")

        # Convert binary string to bytes
        bytes_data = bytearray()
        for i in range(0, len(binary_str), 8):
            byte_bits = binary_str[i:i+8]
            if len(byte_bits) == 8:
                bytes_data.append(int(byte_bits, 2))

        # Deserialize bytes to original data using pickle
        return pickle.loads(bytes_data)
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

def encrypt_script_file(input_file, output_file=None):
    """
    Encrypts a Python script file and saves or returns the encrypted text.

    Args:
        input_file: str - Path to the Python script file.
        output_file: str, optional - Path to save the encrypted text. If None, returns the text.

    Returns:
        str: Encrypted text if output_file is None.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        encrypted = encrypt(script_content)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(encrypted)
        return encrypted
    except Exception as e:
        raise ValueError(f"Failed to encrypt script file: {str(e)}")

def execute_encrypted_script(enc_str, safe_mode=True):
    """
    Decrypts and executes an encrypted Python script.

    Args:
        enc_str: str - The encrypted 'ooga booga' string.
        safe_mode: bool - If True, executes in a restricted environment.

    Returns:
        dict: Any local variables created during execution (if safe_mode=True).
    """
    try:
        # Decrypt the script
        script_content = decrypt(enc_str)
        if not isinstance(script_content, str):
            raise ValueError("Decrypted content is not a string (not a valid script).")

        if safe_mode:
            # Restricted environment: minimal globals
            restricted_globals = {'__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'int': int,
                'str': str,
                'list': list,
                'dict': dict,
            }}
            local_vars = {}
            exec(script_content, restricted_globals, local_vars)
            return local_vars
        else:
            # Full environment (less secure)
            exec(script_content)
            return {}
    except Exception as e:
        raise ValueError(f"Script execution failed: {str(e)}")