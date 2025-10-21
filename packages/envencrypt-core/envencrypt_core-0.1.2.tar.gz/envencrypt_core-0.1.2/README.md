# envencrypt-core

Core encryption utilities for Python envencrypt - A collection of high-performance, secure encryption modules built with Rust and exposed to Python via PyO3.

## Overview

`envencrypt-core` provides platform-specific encryption capabilities for securing sensitive data like environment variables, passwords, and configuration files. The library leverages native OS security features to provide robust encryption with minimal performance overhead.

## Features

- **Cross-platform encryption**: Support for Windows DPAPI and system keyring
- **High performance**: Rust-based implementation for maximum speed and safety
- **Secure by default**: Uses OS-native security APIs and best practices
- **Python integration**: Seamless Python bindings with proper type hints
- **Zero-copy operations**: Efficient memory handling for large data

## Modules

### DPAPI (Windows)
Windows Data Protection API integration for secure data encryption:
- **User scope encryption**: Data encrypted for current user account
- **Machine scope encryption**: Data encrypted for the machine
- **Optional entropy**: Additional security layer with custom entropy
- **Automatic key management**: No manual key handling required

### Keyring (Cross-platform)
System keyring integration for password and secret storage:
- **Secure storage**: Platform-native credential storage
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Service-based organization**: Organize credentials by service name
- **Thread-safe**: Concurrent access support

## Installation

```bash
pip install envencrypt-core
```

**Note**: Platform-specific modules are automatically installed based on your operating system.

## Quick Start

### DPAPI (Windows only)

```python
from envencrypt_core.dpapi import dpapi_protect, dpapi_unprotect

# Basic encryption (user scope)
data = b"sensitive information"
encrypted = dpapi_protect(data)
decrypted = dpapi_unprotect(encrypted)

# With custom entropy for additional security
entropy = b"custom-entropy-string"
encrypted = dpapi_protect(data, entropy)
decrypted = dpapi_unprotect(encrypted, entropy)

# Machine scope (requires admin privileges)
encrypted = dpapi_protect(data, machine_scope=True)
decrypted = dpapi_unprotect(encrypted)
```

### Keyring (Cross-platform)

```python
from envencrypt_core.keyring import keyring_set, keyring_get, keyring_delete

# Store a password
keyring_set("myapp", "username", "secret-password")

# Retrieve a password
password = keyring_get("myapp", "username")

# Delete a password
keyring_delete("myapp", "username")
```

## API Reference

### DPAPI Functions

#### `dpapi_protect(data, optional_entropy=None, machine_scope=False)`
Encrypts data using Windows DPAPI.

**Parameters:**
- `data` (bytes): Data to encrypt
- `optional_entropy` (bytes, optional): Additional entropy for encryption
- `machine_scope` (bool, optional): Use machine scope instead of user scope

**Returns:** `bytes` - Encrypted data

#### `dpapi_unprotect(data, optional_entropy=None)`
Decrypts data encrypted with DPAPI.

**Parameters:**
- `data` (bytes): Encrypted data to decrypt
- `optional_entropy` (bytes, optional): Entropy used during encryption

**Returns:** `bytes` - Decrypted data

### Keyring Functions

#### `keyring_set(service, username, password)`
Stores a password in the system keyring.

#### `keyring_get(service, username)`
Retrieves a password from the system keyring.

#### `keyring_delete(service, username)`
Deletes a password from the system keyring.

## Security Considerations

- **DPAPI**: Data is tied to the user account or machine. Encrypted data cannot be decrypted by different users or on different machines (unless using machine scope).
- **Keyring**: Passwords are stored using the OS-native credential manager (Windows Credential Manager, macOS Keychain, Linux Secret Service).
- **Entropy**: When using DPAPI with custom entropy, ensure the entropy is stored securely and separately from the encrypted data.

## Development

### Prerequisites
- Rust 1.70+
- Python 3.11+
- Platform-specific development tools (Windows SDK, Linux development packages)

### Building from Source

```bash
# Clone the repository
git clone <repository-url>
cd envencrypt-core

# Build all modules
./build_all.ps1

# Or build individual modules
cd crates/dpapi && cargo build --release
cd crates/keyring && cargo build --release
```

### Testing

```bash
# Run Rust tests
cargo test

# Run Python integration tests
python -m pytest tests/
```

## Platform Support

| Platform | DPAPI | Keyring |
|----------|-------|---------|
| Windows  | ✅    | ✅      |
| macOS    | ❌    | ✅      |
| Linux    | ❌    | ✅      |

## License

This project is licensed under the GPL-3.0-or-later License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass and follow the existing code style.

## Authors

- **Dyve** - [dev@dyve.ch](mailto:dev@dyve.ch)
- **Igor Petrovic** - [758832+igorovic@users.noreply.github.com](mailto:758832+igorovic@users.noreply.github.com)
