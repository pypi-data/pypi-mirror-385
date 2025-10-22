"""Tests for plate frame storage module."""
from io import UnsupportedOperation
import pytest
import pandas as pd

from skylab2iai.storage.plate_frame import _SkylabPlateStorage


class TestSkylabPlateStorage:
    """Test suite for _SkylabPlateStorage class."""
    
    def setup_method(self):
        """Reset singleton instance before each test."""
        _SkylabPlateStorage._instance = None
    
    def test_singleton_pattern(self):
        """Test that _SkylabPlateStorage implements singleton pattern correctly."""
        storage1 = _SkylabPlateStorage()
        storage2 = _SkylabPlateStorage()
        assert storage1 is storage2, "Should return the same instance"
    
    def test_get_plate_frames_returns_dataframe(self):
        """Test that get_plate_frames returns a pandas DataFrame."""
        storage = _SkylabPlateStorage()
        result = storage.get_plate_frames()
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) > 0, "Should return non-empty DataFrame"
    
    def test_get_plate_frame_by_name(self):
        """Test retrieving a specific plate frame by name."""
        storage = _SkylabPlateStorage()
        # First get all frames to find a valid name
        all_frames = storage.get_plate_frames()
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            result = storage.get_plate_frame(test_name)
            assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
            assert len(result) == 1, "Should return exactly one frame"
            assert result.iloc[0]['NAME'] == test_name, "Should return the correct frame"
    
    def test_get_plate_frame_nonexistent(self):
        """Test retrieving a non-existent plate frame."""
        storage = _SkylabPlateStorage()
        result = storage.get_plate_frame("NONEXISTENT_PLATE_FRAME_12345")
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) == 0, "Should return empty DataFrame for non-existent frame"
    
    def test_get_plate_frames_by_plate(self):
        """Test retrieving plate frames by plate ID."""
        storage = _SkylabPlateStorage()
        # Get a valid plate ID from existing data
        all_frames = storage.get_plate_frames()
        if len(all_frames) > 0 and 'PLATE_ID' in all_frames.columns:
            test_plate_id = all_frames.iloc[0]['PLATE_ID']
            result = storage.get_plate_frames_by_plate(test_plate_id)
            assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
            assert len(result) > 0, "Should return at least one frame"
            assert all(result['PLATE_ID'] == test_plate_id), "All frames should have the same PLATE_ID"
    
    def test_get_plate_frames_by_plate_nonexistent(self):
        """Test retrieving frames for a non-existent plate."""
        storage = _SkylabPlateStorage()
        result = storage.get_plate_frames_by_plate("NONEXISTENT_PLATE_12345")
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) == 0, "Should return empty DataFrame for non-existent plate"
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are blocked."""
        storage = _SkylabPlateStorage()
        query = "SELECT * FROM plate_frame WHERE name = 'test' --"
        with pytest.raises(UnsupportedOperation, match="SQL injection is not allowed"):
            storage.get_from_custom_query(query)
    
    def test_delete_operation_blocked(self):
        """Test that DELETE operations are blocked."""
        storage = _SkylabPlateStorage()
        query = "DELETE FROM plate_frame WHERE name = 'test'"
        with pytest.raises(UnsupportedOperation, match="Delete operation is not allowed"):
            storage.get_from_custom_query(query)
    
    def test_update_operation_blocked(self):
        """Test that UPDATE operations are blocked."""
        storage = _SkylabPlateStorage()
        query = "UPDATE plate_frame SET name = 'test' WHERE name = 'other'"
        with pytest.raises(UnsupportedOperation, match="Update operation is not allowed"):
            storage.get_from_custom_query(query)
    
    def test_insert_operation_blocked(self):
        """Test that INSERT operations are blocked."""
        storage = _SkylabPlateStorage()
        query = "INSERT INTO plate_frame (name) VALUES ('test')"
        with pytest.raises(UnsupportedOperation, match="Insert operation is not allowed"):
            storage.get_from_custom_query(query)
    
    def test_custom_query_select_allowed(self):
        """Test that SELECT queries are allowed in custom queries."""
        storage = _SkylabPlateStorage()
        query = "SELECT * FROM plate_frame LIMIT 5"
        result = storage.get_from_custom_query(query)
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) <= 5, "Should return at most 5 rows"
    
    def test_custom_query_with_params(self):
        """Test custom query with parameters."""
        storage = _SkylabPlateStorage()
        all_frames = storage.get_plate_frames()
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            query = "SELECT * FROM plate_frame WHERE NAME = ?"
            result = storage.get_from_custom_query(query, params=(test_name,))
            assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
            assert len(result) > 0, "Should return results"
    
    def test_custom_query_with_where_clause(self):
        """Test custom query with WHERE clause."""
        storage = _SkylabPlateStorage()
        query = "SELECT COUNT(*) as count FROM plate_frame"
        result = storage.get_from_custom_query(query)
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert 'count' in result.columns, "Should have count column"
        assert result.iloc[0]['count'] > 0, "Should have some records"
