"""Tests for SQL connection module."""
import sqlite3
from pathlib import Path
import pytest

from skylab2iai.storage.sql_connection import _SqlStorage


class TestSqlStorage:
    """Test suite for _SqlStorage singleton class."""
    
    def setup_method(self):
        """Reset singleton instance before each test."""
        _SqlStorage._instance = None
    
    def test_singleton_pattern(self):
        """Test that _SqlStorage implements singleton pattern correctly."""
        storage1 = _SqlStorage()
        storage2 = _SqlStorage()
        assert storage1 is storage2, "Should return the same instance"
    
    def test_database_connection_initialized(self):
        """Test that database connection is properly initialized."""
        storage = _SqlStorage()
        assert storage.db is not None, "Database connection should be initialized"
        assert isinstance(storage.db, sqlite3.Connection), "Should be a sqlite3 Connection"
    
    def test_database_file_exists(self):
        """Test that the database file exists."""
        storage = _SqlStorage()
        db_path = Path(__file__).parent.parent / 'src' / 'skylab2iai' / 'storage' / 'skylab-data.db'
        assert db_path.exists(), f"Database file should exist at {db_path}"
    
    def test_cursor_method(self):
        """Test that cursor method returns a valid cursor."""
        storage = _SqlStorage()
        cursor = storage.cursor()
        assert cursor is not None, "Cursor should not be None"
        assert isinstance(cursor, sqlite3.Cursor), "Should return a sqlite3 Cursor"
    
    def test_database_has_plate_frame_table(self):
        """Test that database contains the plate_frame table."""
        storage = _SqlStorage()
        cursor = storage.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PLATE_FRAME'")
        result = cursor.fetchone()
        assert result is not None, "plate_frame table should exist"
    
    def test_multiple_instantiation_same_db(self):
        """Test that multiple instantiations use the same database connection."""
        storage1 = _SqlStorage()
        db1 = storage1.db
        storage2 = _SqlStorage()
        db2 = storage2.db
        assert db1 is db2, "Should use the same database connection"
