# FTP/SFTP Sub-Package

**DealerTower Python Framework** — A unified FTP/SFTP client built on `ftplib` and `paramiko` to provide a consistent interface for file transfers.

## Overview

The `ftp` sub-package exposes the `FTPClient`, a high-level helper class for uploading, downloading, and managing files on both FTP and SFTP servers. It abstracts away the differences between the two protocols, providing a single, consistent API that is managed through a context-aware connection.

Key features include:

- **Protocol Agnostic**: Write code once that works for both FTP and SFTP.
- **Context-Managed Connections**: The client handles opening and closing connections automatically.
- **Common File Operations**: Simplified methods for listing directories, checking file existence, uploading, downloading, deleting, and renaming files.
- **Error Handling**: Consistent error reporting through the framework's standard `RequestException`.

## Installation

To use the FTP/SFTP utilities, install `dtpyfw` with the `ftp` extra:

```bash
pip install dtpyfw[ftp]
```

---

## `client.py` — The `FTPClient` Class

The `FTPClient` is the all-in-one solution for remote file management.

### Initialization

```python
from dtpyfw.ftp.client import FTPClient

# For an SFTP server
sftp_client = FTPClient(
    server="sftp.example.com",
    port=22,
    username="myuser",
    password="mypassword",
    is_sftp=True,
)

# For a standard FTP server
ftp_client = FTPClient(
    server="ftp.example.com",
    port=21,
    username="myuser",
    password="mypassword",
    is_sftp=False,
)

# Auto-detect protocol based on port (22 for SFTP, otherwise FTP)
auto_client = FTPClient(
    server="ftp.example.com",
    port=21,
    username="myuser",
    password="mypassword",
)
```

| Parameter  | Type   | Description                                                                    |
| ---------- | ------ | ------------------------------------------------------------------------------ |
| `server`   | `str`  | The hostname or IP address of the server.                                      |
| `port`     | `int`  | The server port (e.g., 21 for FTP, 22 for SFTP).                               |
| `username` | `str`  | The login username.                                                            |
| `password` | `str`  | The login password.                                                            |
| `timeout`  | `int`  | The connection and operation timeout in seconds (default: 20).                 |
| `is_sftp`  | `bool` | Explicitly set the protocol. If `None`, it auto-detects based on the port.       |

### Methods

All methods automatically handle the connection lifecycle.

#### `content(file_path: str) -> dict`

Reads the content of a remote file and returns it along with its last modified timestamp.

```python
file_data = client.content("remote/path/to/file.txt")
print(f"Content: {file_data['content']}")
print(f"Last Modified: {file_data['last_modified']}")
```

#### `get_last_modified(file_path: str) -> dict`

Retrieves only the last modified timestamp of a remote file.

```python
file_info = client.get_last_modified("config.ini")
```

#### `get_folder_list(folder_path: str = "") -> list[str]`

Returns a list of filenames in a remote directory.

```python
files = client.get_folder_list("/data/incoming")
```

#### `upload_file(local_path: str, file_path: str, ...) -> bool`

Uploads a local file to a remote path.

```python
client.upload_file("/path/to/local/report.csv", "/remote/uploads/report.csv")
```

#### `download_file(local_path: str, file_path: str, ...) -> bool`

Downloads a remote file to a local path. By default, it creates the local directory if it doesn't exist and removes any existing file at the destination.

```python
client.download_file("/downloads/archive.zip", "/remote/backups/archive.zip")
```

#### `delete_file(file_path: str) -> bool`

Deletes a file from the remote server.

```python
client.delete_file("/remote/temp/old_file.tmp")
```

#### `rename_file(old_path: str, new_path: str) -> bool`

Renames or moves a file on the remote server.

```python
client.rename_file("/uploads/file.tmp", "/processed/file.done")
```

#### `file_exists(file_path: str) -> bool`

Checks if a file exists at the specified remote path.

```python
if client.file_exists("/remote/path/to/check.txt"):
    print("File found!")
```

#### `create_directory(directory: str) -> bool`

Creates a new directory on the remote server. It will not raise an error if the directory already exists.

```python
client.create_directory("/data/new_folder")
```

---

## Error Handling

All methods in `FTPClient` are designed to catch common FTP/SFTP errors (e.g., connection failures, authentication errors, file not found) and re-raise them as a `RequestException` from `dtpyfw.core`. This provides a consistent error handling mechanism across the entire framework.

```python
from dtpyfw.core.exception import RequestException

try:
    client.download_file("local.txt", "non_existent_remote.txt")
except RequestException as e:
    print(f"FTP operation failed: {e.message} (Status: {e.status_code})")
```

---

*This documentation covers the `ftp` sub-package of the DealerTower Python Framework. Ensure the `ftp` extra is installed to use these features.*
