import argparse
import os
import re
import shutil
import datetime


def _get_mtime_threshold(newermt_value):
    """
    Retrieves a modification time (mtime) threshold based on the provided input.

    The function attempts to derive an mtime threshold based on a given value.
    It first checks if the input is empty and returns 0. If a value is provided,
    it tries to interpret the value as a file path to retrieve its last modification
    time using os.path.getmtime(). If the file does not exist, it then attempts to
    parse the value as an ISO 8601 date/datetime string and converts it to a
    Unix timestamp. If both interpretations fail, it raises a ValueError.

    Parameters:
        newermt_value (str): The input value to derive the mtime threshold. This may
        represent either a file path or an ISO 8601 date/datetime string.

    Returns:
        float: The derived modification time as a Unix timestamp. Returns 0 if
        no value is provided.

    Raises:
        ValueError: If the input is neither a valid file path with a retrievable mtime
        nor a valid ISO 8601 date/datetime string.
    """
    if not newermt_value:
        return 0
    try:
        return os.path.getmtime(newermt_value)
    except FileNotFoundError:
        try:
            return datetime.datetime.fromisoformat(newermt_value).timestamp()
        except ValueError:
            raise ValueError(
                f"Error: --newermt value is not a valid file or ISO date/datetime: {newermt_value}"
            )


def _ensure_destination_exists(destination, dry_run):
    """Creates the destination directory if it doesn't exist."""
    if os.path.isdir(destination):
        return
    if dry_run:
        print(f"(Dry Run) Would create destination directory: {destination}")
    else:
        os.makedirs(destination)


def _copy_file_action(source_path, destination_path, dry_run, quiet):
    """Copies a single file, handling dry-run and quiet modes."""
    if dry_run:
        print(f"(Dry Run) Would copy: {source_path} to {destination_path}")
        return
    try:
        shutil.copy2(source_path, destination_path)
        if not quiet:
            print(f"Copied: {source_path}")
    except FileNotFoundError:
        # File might have been accessed by another process
        pass


def copy_files(origin, destination, pattern, newermt=None, dry_run=False, quiet=False):
    """
    Copies files from origin to destination based on a regex pattern.
    """
    _ensure_destination_exists(destination, dry_run)
    try:
        mtime_threshold = _get_mtime_threshold(newermt)
    except ValueError as e:
        print(e)
        return

    for dirpath, _, filenames in os.walk(origin):
        for filename in filenames:
            if not re.search(pattern, filename):
                continue

            source_path = os.path.join(dirpath, filename)
            if mtime_threshold and os.path.getmtime(source_path) <= mtime_threshold:
                continue

            destination_path = os.path.join(destination, filename)
            _copy_file_action(source_path, destination_path, dry_run, quiet)


def main():
    """
    Main function to parse arguments and call the copy_files function.
    """
    parser = argparse.ArgumentParser(
        description="Copies files based on filename pattern."
    )
    parser.add_argument("origin", help="Origin directory")
    parser.add_argument("destination", help="Destination directory")
    parser.add_argument("pattern", help="Regex pattern for filenames")
    parser.add_argument(
        "--newermt",
        help="Copy only files newer than the specified file's modification time or a given ISO date/datetime.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what files would be copied without actually copying them.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress output of successfully copied files. Useful for cron jobs.",
    )
    args = parser.parse_args()
    copy_files(
        args.origin,
        args.destination,
        args.pattern,
        args.newermt,
        args.dry_run,
        args.quiet,
    )


if __name__ == "__main__":
    main()
