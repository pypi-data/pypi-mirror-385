# tests/test_core.py

import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from src.filesmith.core import copy_files


class TestCopyFiles(unittest.TestCase):

    def setUp(self):
        # Create temporary directories for origin and destination
        self.origin = tempfile.mkdtemp()
        self.destination = tempfile.mkdtemp()

        # Create test files in the origin directory
        self.files = ["test1.txt", "test2.log", "example.txt", "readme.md"]
        for file_name in self.files:
            with open(os.path.join(self.origin, file_name), "w") as f:
                f.write("Sample content")

        # Modify the mtime for some files
        self.old_file = os.path.join(self.origin, "test1.txt")
        old_mtime = datetime.now() - timedelta(days=2)
        os.utime(self.old_file, (old_mtime.timestamp(), old_mtime.timestamp()))

        self.new_file = os.path.join(self.origin, "example.txt")
        new_mtime = datetime.now() - timedelta(hours=1)
        os.utime(self.new_file, (new_mtime.timestamp(), new_mtime.timestamp()))

    def tearDown(self):
        # Remove temporary directories and files
        shutil.rmtree(self.origin)
        shutil.rmtree(self.destination)

    def test_copy_matching_files(self):
        # Test copying files matching a regex pattern
        copy_files(self.origin, self.destination, r"\.txt$")
        copied_files = set(os.listdir(self.destination))
        expected_files = {"test1.txt", "example.txt"}
        self.assertEqual(expected_files, copied_files)

    def test_does_not_copy_non_matching_files(self):
        # Test that files not matching the regex are not copied
        copy_files(self.origin, self.destination, r"\.log$")
        copied_files = set(os.listdir(self.destination))
        expected_files = {"test2.log"}
        self.assertEqual(expected_files, copied_files)

    def test_dry_run(self):
        # Test the dry-run mode does not copy files
        copy_files(self.origin, self.destination, r"\.txt$", dry_run=True)
        copied_files = set(os.listdir(self.destination))
        self.assertEqual(set(), copied_files)

    def test_copy_with_newermt_date(self):
        # Test copying only files newer than a given ISO date
        iso_date = (datetime.now() - timedelta(days=1)).isoformat()
        copy_files(self.origin, self.destination, r".*", newermt=iso_date)
        copied_files = set(os.listdir(self.destination))
        expected_files = {"example.txt"}
        self.assertEqual(expected_files, copied_files)

    def test_invalid_newermt_value(self):
        # Test handling of an invalid newermt value
        with self.assertLogs() as log:
            copy_files(self.origin, self.destination, r".*", newermt="invalid-date")
        self.assertIn("Error: --newermt value is not a valid file or ISO date/datetime: invalid-date", log.output[0])

    def test_quiet_mode(self):
        # Test that quiet mode suppresses output
        with self.assertLogs() as log:
            copy_files(self.origin, self.destination, r"\.txt$", quiet=True)
        self.assertEqual(len(log.output), 0)

    def test_ensure_destination_exists(self):
        # Test that the destination directory is created if it does not exist
        non_existing_destination = os.path.join(tempfile.gettempdir(), "non_existing_dir")
        try:
            copy_files(self.origin, non_existing_destination, r".*")
            self.assertTrue(os.path.isdir(non_existing_destination))
        finally:
            if os.path.exists(non_existing_destination):
                shutil.rmtree(non_existing_destination)
