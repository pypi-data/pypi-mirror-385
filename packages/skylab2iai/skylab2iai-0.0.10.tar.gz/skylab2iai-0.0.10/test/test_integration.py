"""Integration tests for the complete workflow."""
from pathlib import Path
from unittest.mock import patch, Mock
import pytest
import pandas as pd

from skylab2iai import Skylab2iaiCatalog


class TestIntegration:
    """Integration tests for end-to-end workflows."""
    
    def test_complete_workflow_query_and_retrieve(self):
        """Test complete workflow: instantiate, query, retrieve data."""
        # Create catalog
        catalog = Skylab2iaiCatalog()
        
        # Get all frames
        all_frames = catalog.get_plate_frames()
        assert isinstance(all_frames, pd.DataFrame), "Should return DataFrame"
        assert len(all_frames) > 0, "Should have data"
        
        # Get specific frame
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            specific_frame = catalog.get_plate_frame(test_name)
            assert len(specific_frame) > 0, "Should find the frame"
            
            # Get frames by plate
            if 'PLATE_ID' in all_frames.columns:
                plate_id = all_frames.iloc[0]['PLATE_ID']
                plate_frames = catalog.get_plate_frames_by_plate(plate_id)
                assert len(plate_frames) > 0, "Should find frames for plate"
    
    def test_custom_query_workflow(self):
        """Test workflow with custom queries."""
        catalog = Skylab2iaiCatalog()
        
        # Simple query
        query1 = "SELECT COUNT(*) as total FROM plate_frame"
        result1 = catalog.get_plate_frames_by_query(query1)
        assert 'total' in result1.columns, "Should have total column"
        assert result1.iloc[0]['total'] > 0, "Should have records"
        
        # Query with LIMIT
        query2 = "SELECT * FROM plate_frame LIMIT 10"
        result2 = catalog.get_plate_frames_by_query(query2)
        assert len(result2) <= 10, "Should respect LIMIT"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_workflow(self, mock_get):
        """Test complete download workflow."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'FITS data chunk'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Download single frame
                df, files = catalog.download_fits_plate_frames(
                    plate_names=(test_name,),
                    output_dir=tmpdir
                )
                
                assert isinstance(df, pd.DataFrame), "Should return DataFrame"
                assert isinstance(files, list), "Should return file list"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_query_and_download_workflow(self, mock_get):
        """Test workflow: custom query then download results."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'FITS data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        query = "SELECT * FROM plate_frame LIMIT 2"
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            df, files = catalog.download_fits_plate_frames_from_custom_query(
                query=query,
                output_dir=tmpdir
            )
            
            assert isinstance(df, pd.DataFrame), "Should return DataFrame"
            assert len(df) <= 2, "Should respect query LIMIT"
    
    def test_multiple_catalog_instances_share_data(self):
        """Test that multiple catalog instances share the same data (singleton)."""
        catalog1 = Skylab2iaiCatalog()
        catalog2 = Skylab2iaiCatalog()
        
        # Should be the same instance
        assert catalog1 is catalog2, "Should be singleton"
        
        # Should access the same data
        frames1 = catalog1.get_plate_frames()
        frames2 = catalog2.get_plate_frames()
        
        assert len(frames1) == len(frames2), "Should have same data"
    
    def test_error_handling_invalid_operations(self):
        """Test that invalid operations are properly rejected."""
        catalog = Skylab2iaiCatalog()
        
        from io import UnsupportedOperation
        
        # Test SQL injection prevention
        with pytest.raises(UnsupportedOperation):
            catalog.get_plate_frames_by_query("SELECT * FROM plate_frame --")
        
        # Test DELETE prevention
        with pytest.raises(UnsupportedOperation):
            catalog.get_plate_frames_by_query("DELETE FROM plate_frame")
        
        # Test UPDATE prevention
        with pytest.raises(UnsupportedOperation):
            catalog.get_plate_frames_by_query("UPDATE plate_frame SET name='test'")
        
        # Test INSERT prevention
        with pytest.raises(UnsupportedOperation):
            catalog.get_plate_frames_by_query("INSERT INTO plate_frame VALUES (1)")
    
    def test_data_consistency(self):
        """Test that data remains consistent across operations."""
        catalog = Skylab2iaiCatalog()
        
        # Get total count
        all_frames = catalog.get_plate_frames()
        total_count = len(all_frames)
        
        # Query for count
        count_query = "SELECT COUNT(*) as count FROM plate_frame"
        count_result = catalog.get_plate_frames_by_query(count_query)
        query_count = count_result.iloc[0]['count']
        
        assert total_count == query_count, "Counts should match"
    
    def test_database_readonly(self):
        """Test that database operations are read-only."""
        catalog = Skylab2iaiCatalog()
        
        # Get initial data
        initial_frames = catalog.get_plate_frames()
        initial_count = len(initial_frames)
        
        # Try to perform read operations
        catalog.get_plate_frames()
        catalog.get_plate_frames()
        
        # Verify data unchanged
        final_frames = catalog.get_plate_frames()
        final_count = len(final_frames)
        
        assert initial_count == final_count, "Data should remain unchanged"
