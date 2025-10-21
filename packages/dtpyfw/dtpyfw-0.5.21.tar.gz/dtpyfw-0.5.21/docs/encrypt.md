# Encryption Sub-Package

**DealerTower Python Framework** — Simplifies password hashing and JSON Web Token (JWT) handling with easy-to-use, secure helpers.

## Overview

The `encryption` sub-package provides robust solutions for two critical security tasks:

- **Password Hashing**: A `Hash` class that uses `passlib` with modern algorithms like Argon2 and bcrypt to securely hash and verify passwords. It also supports automatic rehashing of outdated passwords.
- **JWT Management**: `jwt_encrypt` and `jwt_decrypt` functions that leverage `python-jose` for creating, signing, and verifying JWTs, ensuring secure and stateless authentication.

This sub-package abstracts away the complexities of cryptographic operations, allowing developers to implement security best practices with minimal boilerplate.

## Installation

To use the encryption utilities, install `dtpyfw` with the `encrypt` extra:

```bash
pip install dtpyfw[encrypt]
```

---

## `hashing.py` — Password Hashing

The `Hash` class provides static methods for all password-related operations. It is configured to use `argon2` as the primary hashing scheme and `bcrypt` as a deprecated fallback, enabling seamless migration of old password hashes.

### `Hash.crypt(password: str) -> str`

Hashes a plaintext password using the default scheme (Argon2).

```python
from dtpyfw.encrypt.hashing import Hash

hashed_password = Hash.crypt("my-very-secure-password-123")
# Result is an Argon2 hash string
```

### `Hash.verify(plain_password: str, hashed_password: str) -> bool`

Verifies a plaintext password against a stored hash. It works for both Argon2 and bcrypt hashes.

```python
is_valid = Hash.verify("my-very-secure-password-123", stored_hashed_password)
```

### `Hash.needs_update(hashed_password: str) -> bool`

Checks if a given hash uses a deprecated scheme (e.g., bcrypt). This is useful for identifying passwords that should be rehashed upon the user's next login.

```python
# Assume old_hash is a bcrypt hash
if Hash.needs_update(old_hash):
    # Rehash the password and update the database
    new_hash = Hash.crypt(user_provided_password)
    update_user_password_hash(user_id, new_hash)
```

---

## `encryption.py` — JSON Web Tokens (JWT)

These functions provide a straightforward way to create and validate JWTs for stateless authentication and authorization.

### `jwt_encrypt(...) -> str`

Creates and signs a JWT.

```python
from datetime import timedelta
from dtpyfw.encrypt.encryption import jwt_encrypt

# Define the token payload
claims = {"user_id": 123, "roles": ["admin", "editor"]}
subject = "user-auth"

# Create the token
token = jwt_encrypt(
    tokens_secret_key="your-super-secret-key",
    encryption_algorithm="HS256",
    subject=subject,
    claims=claims,
    expiration_timedelta=timedelta(hours=1),
)
```

**Parameters:**

- `tokens_secret_key`: The secret key used for signing the token.
- `encryption_algorithm`: The signing algorithm (e.g., `HS256`).
- `subject`: A required string identifying the purpose or principal of the token.
- `claims`: A dictionary of custom data to include in the token payload.
- `expiration_timedelta`: A `timedelta` object specifying the token's lifespan. If omitted, the token will not expire.

### `jwt_decrypt(...) -> dict`

Verifies a JWT's signature, expiration, and subject, then returns its decoded payload.

```python
from dtpyfw.encrypt.encryption import jwt_decrypt

try:
    payload = jwt_decrypt(
        tokens_secret_key="your-super-secret-key",
        encryption_algorithm="HS256",
        token=received_token,
        subject="user-auth",  # Must match the subject used during encryption
    )
    print(f"Token is valid. User ID: {payload['user_id']}")
except Exception as e:
    print(f"Token validation failed: {e}")
```

**Parameters:**

- `token`: The JWT string to decode.
- `subject`: The expected subject. The function will raise an exception if the token's subject does not match.
- `check_exp`: A boolean (default `True`) to control whether to validate the token's expiration time.

**Raises:**

- `Exception("wrong_token_subject")`: If the token's subject does not match the expected one.
- `jose.exceptions.ExpiredSignatureError`: If the token has expired.
- Other `jose` exceptions for various validation failures (e.g., invalid signature).

---

*This documentation covers the `encrypt` sub-package of the DealerTower Python Framework.*
