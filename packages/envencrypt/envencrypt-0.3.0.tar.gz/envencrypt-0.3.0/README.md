[![Release](https://github.com/Dyve-dev/py-envencrypt/actions/workflows/release.yml/badge.svg)](https://github.com/Dyve-dev/py-envencrypt/actions/workflows/release.yml)

# EnvEncrypt

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Windows 10/11](https://img.shields.io/badge/platform-Windows%2010%2F11-blue.svg)](https://www.microsoft.com/windows/)

A secure environment variable management library for Windows that extends python-dotenv with automatic encryption capabilities using Windows DPAPI (Data Protection API).

## Features

- 🔒 **Automatic Encryption**: Seamlessly encrypts environment variables using Windows DPAPI
- 🔄 **Drop-in Replacement**: Compatible with python-dotenv API
- 📁 **Dual File Support**: Works with both `.env` and `.env.enc` files
- 🚀 **Background Processing**: Non-blocking encryption operations
- 💬 **Comment Preservation**: Maintains comments and formatting in encrypted files
- 🔐 **User-Specific Security**: Encryption tied to Windows user account
- ⚡ **Lazy Loading**: Automatic decryption when environment variables are accessed

## Installation

```bash
pip install envencrypt
```

**Requirements:**
- Windows 10 or Windows 11
- Python 3.11+
- pywin32 (automatically installed)

## Quick Start

### Basic Usage

Replace your existing `dotenv` import:

```python
# Instead of: from dotenv import load_dotenv
from envencrypt import load_dotenve

# Load and automatically encrypt values in your `.env.enc` file
load_dotenve()
```

### Working with Encrypted Files

```python
from envencrypt import EnvEncrypt

# Manually encrypt a .env file to .env.enc
EnvEncrypt.encrypt_env(".env", save=True)

# Decrypt and load variables from .env.enc
decrypted_vars = EnvEncrypt.decrypt_env(".env.enc")
```

## How It Works

1. **Standard .env Loading**: Loads your regular `.env` file using python-dotenv
2. **Encrypted .env.enc Loading**: Loads your `.env.enc` file. In the background, encrypts sensitive values and saves them to `.env.enc`
3. **Secure Storage**: Uses Windows DPAPI to encrypt values, tied to your user account
4. **Seamless Access**: Environment variables are automatically decrypted when accessed

### Encryption Format

Encrypted values in `.env.enc` files are prefixed with `enc:` followed by hex-encoded encrypted data:

```bash
# Original .env
DATABASE_PASSWORD=supersecret123
API_KEY=abc-def-ghi

# Encrypted .env.enc
DATABASE_PASSWORD=enc:01000000d08c9ddf0115d1118c7a00c04fc297eb...
API_KEY=enc:01000000d08c9ddf0115d1118c7a00c04fc297eb...
```

## API Reference

### `load_dotenve()`

Enhanced version of python-dotenv's `load_dotenv()` with encryption support.

```python
load_dotenve(
    dotenv_path=None,              # Path to .env file (default: .env)
    encrypted_dotenv_path=None,    # Path to .env.enc file (default: .env.enc)
    verbose=False,                 # Enable verbose output (default: False)
    override=False,                # Override existing env vars from .env (default: False)
    encrypt_override=True,         # Override existing env vars from .env.enc (default: True)
    interpolate=True,              # Enable variable interpolation only for .env (default: True)
    encoding="utf-8",              # File encoding (default: utf-8)
    encrypt_in_background=True     # Encrypt .env file asynchronously (default: True)
)
```

> [!NOTE]
> When `encrypt_in_background=False`, you must manually encrypt your .env file using the `EnvEncrypt` class methods shown below.


### `EnvEncrypt` Class

Core class for encryption operations.

```python
# Initialize
env_encrypt = EnvEncrypt(
    encrypted_dotenv_path=".env.enc",  # Path to encrypted file (default: .env.enc)
    verbose=False,                     # Enable verbose logging
    encoding="utf-8",                  # File encoding
    override=True                      # Override existing env vars
)

# Static methods
EnvEncrypt.encrypt_env(file_path, save=True)            # Encrypt a .env file and save back to same file
EnvEncrypt.encrypt_env(file_path, save=".\.env.encrypted")    # Encrypt a .env file and save to `.\.env.enc`
EnvEncrypt.decrypt_env(file_path)                       # Decrypt a .env.enc file
```

## Security Considerations

### Windows DPAPI Protection

- **User-Specific**: Encrypted data can only be decrypted by the same Windows user account
- **Machine-Bound**: Encryption is tied to the specific Windows machine
- **No Password Required**: Uses Windows authentication, no additional passwords needed

### Best Practices

1. **Exclude .env from Version Control**: Add `.env` to `.gitignore`
2. **Regular Key Rotation**: Periodically update sensitive credentials
3. **Access Control**: Ensure proper file permissions on encrypted files

### Limitations

- **Windows Only**: DPAPI is Windows-specific
- **User Account Dependency**: Cannot decrypt across different user accounts
- **Machine Dependency**: Encrypted data cannot be moved to different machines
- **Backup Considerations**: System restores may affect decryption capability

## File Structure Examples

### Development Workflow

```
project/
├── .env                 # Local development (git-ignored)
├── .env.enc            # Encrypted version 
├── .env.example        # Template file (git-tracked)
└── .gitignore          # Contains .env
```

### Sample .env File

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=developer
DB_PASSWORD=secretpassword123

# API Keys
STRIPE_SECRET_KEY=sk_test_abcdef123456
JWT_SECRET=my-super-secret-jwt-key

# Optional: Empty values and comments are preserved
OPTIONAL_SETTING=
# This is a comment that will be preserved
```

## Advanced Usage

### Custom Encryption Paths

```python
from envencrypt import load_dotenve

# Use custom paths for both files
load_dotenve(
    dotenv_path="config/.env",
    encrypted_dotenv_path="config/.env.encrypted"
)
```

### Manual Encryption Control

```python
from envencrypt import EnvEncrypt

# Disable background encryption
load_dotenve(encrypt_in_background=False)

# Manually encrypt when needed
EnvEncrypt.encrypt_env(".env", save=True)
```

### Programmatic Variable Access

```python
from envencrypt import EnvEncrypt
import os

# Load encrypted variables
load_dotenve()

# Access via os.environ (automatically decrypted)
database_password = os.environ.get("DATABASE_PASSWORD")

# Or manually decrypt specific files
decrypted_vars = EnvEncrypt.decrypt_env(".env.enc")
api_key = decrypted_vars.get("API_KEY")
```

## Troubleshooting

### Common Issues

**Decryption Fails After System Changes**
- Cause: Major system changes or user account modifications
- Solution: Re-encrypt the `.env` file with `EnvEncrypt.encrypt_env()`

**Variables Not Loading**
- Check file paths and permissions
- Verify Windows user account access
- Enable verbose mode for debugging: `load_dotenve(verbose=True)`

**Performance Concerns**
- Use background encryption: `encrypt_in_background=True` (default)
- Consider encrypting only sensitive files manually

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from envencrypt import load_dotenve
load_dotenve(verbose=True)
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and ensure all tests pass.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

