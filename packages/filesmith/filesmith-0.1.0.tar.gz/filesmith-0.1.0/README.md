# Filesmith

A command-line utility for copying files based on pattern matching, with support for filtering by modification time.

## Overview

Filesmith is a Python utility that helps you copy files from one directory to another based on regular expression
patterns. It's particularly useful for selective file copying, backup operations, and automated file management tasks.

## Installation

You can install filesmith using pip:

```bash
pip install filesmith
```

## Usage

```bash
filesmith <origin> <destination> <pattern> [options]
```

### Arguments
- `origin`: The source directory.
- `destination`: The destination directory.
- `pattern`: The regex pattern to match filenames against.

### Options
- `--newermt <file_or_isodate>`: Only copy files newer than a reference file's modification time or a given ISO date/datetime.
- `-n`, `--dry-run`: Show which files would be copied without actually copying them.
- `-q`, `--quiet`: Suppress output for successfully copied files.

### Examples

1.  **Copy all .txt files from `source` to `dest`:**
    ```bash
    filesmith /path/to/source /path/to/dest ".*\.txt$"
    ```

2.  **Perform a dry run to see which .jpg files would be copied:**
    ```bash
    filesmith /path/to/source /path/to/dest ".*\.jpg$" --dry-run
    ```

3.  **Copy .log files newer than a specific date:**
    ```bash
    filesmith /path/to/logs /path/to/backup ".*\.log$" --newermt 2023-10-27T10:00:00
    ```

4.  **Copy .py files that are newer than `main.py`:**
    ```bash
    filesmith /path/to/src /path/to/old_src ".*\.py$" --newermt /path/to/src/main.py
    ```
