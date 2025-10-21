# Bucket Sub-Package

**DealerTower Python Framework** — Simplified S3-compatible storage operations through the `Bucket` class, which wraps `boto3` to reduce boilerplate and standardize file management across microservices.

## Overview

The `bucket` sub-package provides an easy-to-use interface for interacting with AWS S3 or any other S3-compatible object storage service. Its features include:

- **Simplified Configuration**: Automatic client setup with credentials, endpoint URLs, and region settings.
- **URL Generation**: Easily generate public URLs for stored objects.
- **Common File Operations**: High-level methods for uploading, downloading, duplicating, and deleting files.
- **Flexible Uploads**: Supports uploading raw bytes from memory or streaming files directly from disk.
- **Consistent Error Handling**: All methods raise a standardized `RequestException` for clear and predictable error management.

## Installation

To use the bucket utilities, install `dtpyfw` with the `bucket` extra, which includes `boto3`.

```bash
pip install dtpyfw[bucket]
```

---

## `bucket.py` — The `Bucket` Class

The `Bucket` class is the main entry point for all object storage operations.

### Initialization

```python
from dtpyfw.bucket.bucket import Bucket

# For an S3-compatible service (like MinIO or DigitalOcean Spaces)
s3_compatible_bucket = Bucket(
    name="my-bucket-name",
    s3_mode=False,
    endpoint_url="https://my-s3-service.com",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
)

# For AWS S3
aws_s3_bucket = Bucket(
    name="my-aws-s3-bucket",
    s3_mode=True,
    endpoint_url="https://s3.us-east-1.amazonaws.com", # The public-facing URL for generating links
    access_key="YOUR_AWS_ACCESS_KEY",
    secret_key="YOUR_AWS_SECRET_KEY",
    region_name="us-east-1",
)
```

| Parameter      | Type   | Description                                                                                             |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| `name`         | `str`  | The name of the bucket to interact with.                                                                |
| `s3_mode`      | `bool` | Set to `True` for AWS S3, which requires `region_name`. If `False`, it's treated as a compatible service. |
| `endpoint_url` | `str`  | The base URL for generating object links. For AWS S3, this is the public S3 endpoint.                     |
| `access_key`   | `str`  | Your access key ID.                                                                                     |
| `secret_key`   | `str`  | Your secret access key.                                                                                 |
| `region_name`  | `str`  | The AWS region (e.g., `us-east-1`), required only when `s3_mode` is `True`.                               |

### Methods

#### `url_generator(key: str) -> str`

Returns the full public URL for an object, given its key.

```python
file_url = bucket.url_generator("documents/invoices/invoice-123.pdf")
# Returns: https://my-s3-service.com/my-bucket-name/documents/invoices/invoice-123.pdf
```

#### `upload(file: bytes, key: str, content_type: str, cache_control: str = 'no-cache') -> str`

Uploads a `bytes` object to the specified key and returns its public URL.

```python
image_data = b"..."  # Your image data in bytes
url = bucket.upload(image_data, "images/new-image.jpg", "image/jpeg")
```

#### `upload_by_path(file_path: str, key: str, ...) -> str`

Reads a local file and uploads its content to the specified key.

```python
url = bucket.upload_by_path(
    "/path/to/local/file.txt",
    "remote/path/file.txt",
    content_type="text/plain"
)
```

#### `download(key: str, filepath: str) -> bool`

Downloads an object from the bucket to a local file path.

```python
success = bucket.download("reports/q1-report.csv", "/tmp/q1-report.csv")
```

#### `download_fileobj(key: str, file_obj) -> bool`

Downloads an object into a file-like object (e.g., an in-memory buffer).

```python
from io import BytesIO

buffer = BytesIO()
bucket.download_fileobj("archive.zip", buffer)
buffer.seek(0)  # Reset buffer position to the beginning to read its content
zip_data = buffer.read()
```

#### `check_file_exists(key: str) -> bool`

Checks if an object exists at the given key.

```python
if bucket.check_file_exists("config.json"):
    print("Configuration file found.")
```

#### `duplicate(source_key: str, destination_key: str, ...) -> str`

Copies an object from a source key to a destination key within the same bucket.

```python
new_url = bucket.duplicate("images/profile.png", "images/profile_backup.png")
```

#### `safe_duplicate(source_key: str, ...) -> str`

Duplicates an object but automatically renames the destination key if it already exists to avoid overwriting. For example, `file.txt` would be copied to `file-2.txt`, `file-3.txt`, and so on.

```python
# If 'archive.zip' exists, this might create 'archive-2.zip'
new_url = bucket.safe_duplicate("archive.zip")
```

#### `delete(key: str) -> bool`

Removes an object from the bucket.

```python
was_deleted = bucket.delete("temporary/file-to-remove.tmp")
```

#### `get_s3() -> BaseClient`

Returns the underlying `boto3` client instance for advanced use cases that are not covered by the wrapper.

```python
s3_client = bucket.get_s3()
# Now you can use the full power of boto3
response = s3_client.list_objects_v2(Bucket=bucket.get_bucket_name())
```

---

## Error Handling

All methods are wrapped to catch `boto3` exceptions and re-raise them as a `RequestException` from `dtpyfw.core`. This ensures that S3-related failures are handled consistently with other exceptions in the framework.

```python
from dtpyfw.core.exception import RequestException

try:
    bucket.upload(b"some data", "my-key", "text/plain")
except RequestException as e:
    # This could be due to invalid credentials, network issues, or permissions errors.
    print(f"Failed to upload file: {e.message} (Status: {e.status_code})")
```

---

*This documentation covers the `bucket` sub-package of the DealerTower Python Framework.*
