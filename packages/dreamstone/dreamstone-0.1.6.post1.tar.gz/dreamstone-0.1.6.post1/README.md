# Dreamstone

**Dreamstone** is a Python library and CLI tool for secure hybrid encryption, combining RSA (asymmetric) and AES-GCM (symmetric). It is designed to facilitate secure key generation, encryption, and decryption of files or base64 data, providing structured JSON payloads for easy integration in applications or pipelines. Dreamstone can be used both as a library and via CLI commands.

## Features

* Hybrid encryption: RSA + AES-GCM
* RSA key pair generation with optional password protection
* Encrypt/decrypt files or base64-encoded strings
* Structured JSON output for encrypted payloads
* CLI with long and short aliases for scripting and automation
* Fully embeddable in Python projects

## Installation

Install via Poetry (development environment):

```bash
poetry install
poetry run dreamstone --help
```

Install via PyPI (production):

```bash
pip install dreamstone
```

## CLI Overview

Each command supports a long and short alias:

| Command   | Alias | Description                       |
| --------- | ----- | --------------------------------- |
| `genkey`  | `gk`  | Generate an RSA key pair          |
| `encrypt` | `enc` | Encrypt a file or base64 string   |
| `decrypt` | `dec` | Decrypt an encrypted JSON payload |

Logging can be adjusted using `--log-level` (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`).

## RSA Key Generation (`genkey` / `gk`)

Generate an RSA key pair with optional password protection for the private key.

### Example

```bash
dreamstone genkey \
  --private-key private.pem \
  --public-key public.pem \
  --password "mypassword" \
  --password-path secret.key
```

### Arguments

| Argument             | Alias   | Required | Description                                                     |
| -------------------- | ------- | -------- | --------------------------------------------------------------- |
| `--private-key`      | `-pv`   | true     | Path to save private key                                        |
| `--public-key`       | `-pb`   | true     | Path to save public key                                         |
| `--password`         | `-p`    | false    | Password to encrypt the private key (auto-generated if omitted) |
| `--no-show-password` | `-nsp`  | false    | Do not show auto-generated password in terminal                 |
| `--password-path`    | `-pp`   | false    | File path to save auto-generated password                       |
| `--overwrite`        | `-f`    | false    | Overwrite existing keys without asking                          |
| `--log-level`        | `-ll`   | false    | Logging level (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`) |

**Notes:**

* If no password is provided, a strong password will be generated automatically.
* Passwords can be saved to a file for later use.

## Encryption (`encrypt` / `enc`)

Encrypt data from a file or directly from a base64 string using a public key. If no public key is provided, a new RSA key pair is generated.

### Encrypting a File with an Existing Public Key

```bash
dreamstone encrypt \
  secret.txt \
  --out encrypted.json \
  --public-key public.pem
```

### Encrypting Base64 Data

```bash
dreamstone encrypt \
  "SGVsbG8gd29ybGQ=" \
  --base64 \
  --out encrypted.json
```

### Encrypting Without Providing Keys

```bash
dreamstone encrypt \
  secret.txt \
  --out encrypted.json \
  --password-path secrets/secret.key
```

This will generate a new RSA key pair and save it in the default directory.

### Arguments

| Argument             | Alias  | Required | Description                                     |
| -------------------- | ------ | -------- | ----------------------------------------------- |
| `input`              | -      | true     | Input string or path to file to encrypt         |
| `--out`              | `-o`   | true     | Path to save encrypted JSON payload             |
| `--base64`           | `-b64` | false    | Indicates input is base64-encoded               |
| `--public-key`       | `-pv`  | false    | Public key PEM file (auto-generated if omitted) |
| `--private-key`      | `-pb`  | false    | Path to private key PEM (used or to be created) |
| `--password`         | `-p`   | false    | Password for generated private key              |
| `--password-path`    | `-pp`  | false    | File path to save password                      |
| `--no-show-password` | `-nsp` | false    | Do not show auto-generated password             |
| `--log-level`        | `-ll`  | false    | Logging level                                   |

**Behavior:**

* If input is a directory, the command fails.
* Encrypted output is stored in JSON format with fields for `encrypted_key`, `nonce`, `ciphertext`, and metadata.

## Decryption (`decrypt` / `dec`)

Decrypt a JSON payload using a private key. Passwords can be provided inline or via a file.

### Example Using Inline Password

```bash
dreamstone decrypt \
  encrypted.json \
  --private-key private.pem \
  --password "mypassword" \
  --out decrypted.txt
```

### Example Using Password File

```bash
dreamstone decrypt \
  encrypted.json \
  --private-key private.pem \
  --password-path secret.key \
  --out decrypted.txt
```

### Arguments

| Argument          | Alias  | Required | Description                     |
| ----------------- | ------ | -------- | ------------------------------- |
| `payload`         | -      | true     | Path to the encrypted JSON file |
| `--private-key`   | `-pv`  | true     | Private key PEM file            |
| `--password`      | `-p`   | false    | Password to decrypt private key |
| `--password-path` | `-pp`  | false    | File containing password        |
| `--out`           | `-o`   | false    | File to save decrypted output   |

**Behavior:**

* If `--out` is omitted, decrypted data is printed to stdout.
* Automatically handles both text and binary outputs.

## Encrypted JSON Payload Format

All encrypted outputs follow a structured JSON format:

```json
{
  "encrypted_key": "<base64-encoded AES key encrypted with RSA>",
  "nonce": "<base64-encoded AES-GCM nonce>",
  "ciphertext": "<base64-encoded ciphertext>",
  "algorithm": "AES-GCM",
  "key_type": "RSA"
}
```

## Python Library Usage

### Generate Keys

```python
from dreamstone.core.keys import generate_rsa_keypair

private_key, public_key = generate_rsa_keypair()
```

### Encrypt Data

```python
from dreamstone.core.encryption import encrypt
from dreamstone.models.payload import EncryptedPayload

payload_dict = encrypt(b"secret data", public_key)
payload = EncryptedPayload(**payload_dict)
```

### Decrypt Data

```python
from dreamstone.core.decryption import decrypt

decrypted = decrypt(
    encrypted_key=payload.encrypted_key,
    nonce=payload.nonce,
    ciphertext=payload.ciphertext,
    private_key=private_key
)

print(decrypted.decode())
```

### Encrypt/Decrypt Base64 Strings

```python
import base64

data = base64.b64decode("SGVsbG8gd29ybGQ=")
payload_dict = encrypt(data, public_key)
decrypted = decrypt(
    encrypted_key=payload_dict["encrypted_key"],
    nonce=payload_dict["nonce"],
    ciphertext=payload_dict["ciphertext"],
    private_key=private_key
)
```

## Example CLI Flow

1. **Generate keys with password saved to file:**

```bash
poetry run dreamstone genkey \
  --private-key secrets/private.pem \
  --public-key secrets/public.pem \
  --password-path secrets/secret.key
```

2. **Encrypt a file:**

```bash
poetry run dreamstone encrypt \
  .env \
  --out env.enc.json \
  --private-key secrets/private.pem \
  --public-key secrets/public.pem \
  --password-path secrets/secret.key
```

3. **Decrypt the file:**

```bash
poetry run dreamstone decrypt \
  env.enc.json \
  --private-key secrets/private.pem \
  --password-path secrets/secret.key \
  --out .env
```

## Logging

* Default logging level is `WARNING`.
* Can be adjusted with `--log-level` to `DEBUG`, `INFO`, `ERROR`, or `CRITICAL`.
* Rich formatting with traceback support is included for better CLI experience.

## Security Notes

* Always store generated passwords securely.
* AES-GCM ensures confidentiality and integrity of encrypted data.
* RSA keys are generated with strong default parameters for modern security standards.
* Do not share private keys or passwords publicly.

## License

MIT License

## Author

Renks
