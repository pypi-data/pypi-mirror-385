"""Tests for catalog module."""
from io import UnsupportedOperation
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd
import requests

from skylab2iai import Skylab2iaiCatalog


class TestSkylab2iaiCatalog:
    """Test suite for Skylab2iaiCatalog class."""
    
    def setup_method(self):
        """Reset singleton instance before each test."""
        Skylab2iaiCatalog._instance = None
    
    def test_singleton_pattern(self):
        """Test that Skylab2iaiCatalog implements singleton pattern correctly."""
        catalog1 = Skylab2iaiCatalog()
        catalog2 = Skylab2iaiCatalog()
        assert catalog1 is catalog2, "Should return the same instance"
    
    def test_repository_initialized(self):
        """Test that repository is initialized on first instantiation."""
        catalog = Skylab2iaiCatalog()
        assert catalog._repository is not None, "Repository should be initialized"
    
    def test_get_plate_frames(self):
        """Test get_plate_frames method."""
        catalog = Skylab2iaiCatalog()
        result = catalog.get_plate_frames()
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) > 0, "Should return non-empty DataFrame"
    
    def test_get_plate_frame(self):
        """Test get_plate_frame method."""
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            result = catalog.get_plate_frame(test_name)
            assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
            assert len(result) > 0, "Should return results"
    
    def test_get_plate_frames_by_plate(self):
        """Test get_plate_frames_by_plate method."""
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        if len(all_frames) > 0 and 'PLATE_ID' in all_frames.columns:
            test_plate_id = all_frames.iloc[0]['PLATE_ID']
            result = catalog.get_plate_frames_by_plate(test_plate_id)
            assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
    
    def test_get_plate_frames_by_query(self):
        """Test get_plate_frames_by_query method."""
        catalog = Skylab2iaiCatalog()
        query = "SELECT * FROM plate_frame LIMIT 5"
        result = catalog.get_plate_frames_by_query(query)
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) <= 5, "Should return at most 5 rows"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_plate_frames_success(self, mock_get):
        """Test successful FITS file download."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            
            # Use a temporary directory
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                result_df, downloaded_files = catalog.download_fits_plate_frames(
                    plate_names=(test_name,),
                    output_dir=tmpdir
                )
                
                assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
                assert isinstance(downloaded_files, list), "Should return a list of files"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_plate_frames_nonexistent(self, mock_get):
        """Test downloading non-existent plate frame."""
        catalog = Skylab2iaiCatalog()
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result_df, downloaded_files = catalog.download_fits_plate_frames(
                plate_names=("NONEXISTENT_PLATE_12345",),
                output_dir=tmpdir
            )
            
            assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
            assert len(result_df) == 0, "Should return empty DataFrame"
            assert len(downloaded_files) == 0, "Should not download any files"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_plate_frames_default_dir(self, mock_get):
        """Test download with default output directory."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            
            # Clean up default directory if it exists
            import shutil
            default_dir = Path('./fits_downloads')
            if default_dir.exists():
                shutil.rmtree(default_dir)
            
            try:
                result_df, downloaded_files = catalog.download_fits_plate_frames(
                    plate_names=(test_name,)
                )
                
                assert default_dir.exists(), "Default directory should be created"
                assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
            finally:
                # Clean up
                if default_dir.exists():
                    shutil.rmtree(default_dir)
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_plate_frames_http_error(self, mock_get):
        """Test handling of HTTP errors during download."""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        
        if len(all_frames) > 0:
            test_name = all_frames.iloc[0]['NAME']
            
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                result_df, downloaded_files = catalog.download_fits_plate_frames(
                    plate_names=(test_name,),
                    output_dir=tmpdir
                )
                
                # Should handle error gracefully
                assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
                assert len(downloaded_files) == 0, "Should not have downloaded files"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_multiple_frames(self, mock_get):
        """Test downloading multiple FITS files."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        all_frames = catalog.get_plate_frames()
        
        if len(all_frames) >= 2:
            test_names = (all_frames.iloc[0]['NAME'], all_frames.iloc[1]['NAME'])
            
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                result_df, downloaded_files = catalog.download_fits_plate_frames(
                    plate_names=test_names,
                    output_dir=tmpdir
                )
                
                assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
                assert len(result_df) >= 1, "Should have results"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_from_custom_query_success(self, mock_get):
        """Test downloading FITS files from custom query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        query = "SELECT * FROM plate_frame LIMIT 1"
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result_df, downloaded_files = catalog.download_fits_plate_frames_from_custom_query(
                query=query,
                output_dir=tmpdir
            )
            
            assert isinstance(result_df, pd.DataFrame), "Should return a DataFrame"
            assert isinstance(downloaded_files, list), "Should return a list"
    
    def test_download_fits_from_custom_query_no_results(self):
        """Test downloading from query with no results."""
        catalog = Skylab2iaiCatalog()
        query = "SELECT * FROM plate_frame WHERE NAME = 'NONEXISTENT_12345'"
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(UnsupportedOperation, match="No plate frames found"):
                catalog.download_fits_plate_frames_from_custom_query(
                    query=query,
                    output_dir=tmpdir
                )
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_fits_from_custom_query_default_dir(self, mock_get):
        """Test download from custom query with default directory."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        query = "SELECT * FROM plate_frame LIMIT 1"
        
        import shutil
        default_dir = Path('./fits_downloads')
        if default_dir.exists():
            shutil.rmtree(default_dir)
        
        try:
            result_df, downloaded_files = catalog.download_fits_plate_frames_from_custom_query(
                query=query
            )
            
            assert default_dir.exists(), "Default directory should be created"
        finally:
            if default_dir.exists():
                shutil.rmtree(default_dir)
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_single_file_success(self, mock_get):
        """Test _download_single_file helper method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data chunk'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog = Skylab2iaiCatalog()
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            result = catalog._download_single_file(
                url="http://example.com/test.fits",
                output_dir=output_path,
                file_prefix="test_plate"
            )
            
            assert result is not None, "Should return file path"
            assert "test_plate.fits" in result, "Should contain correct filename"
    
    @patch('skylab2iai.catalog.catalog.requests.get')
    def test_download_single_file_error(self, mock_get):
        """Test _download_single_file with error."""
        mock_get.side_effect = Exception("Network error")
        
        catalog = Skylab2iaiCatalog()
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            result = catalog._download_single_file(
                url="http://example.com/test.fits",
                output_dir=output_path,
                file_prefix="test_plate"
            )
            
            assert result is None, "Should return None on error"
    
    def test_catalog_import_from_module(self):
        """Test that catalog can be imported from skylab2iai.catalog."""
        from skylab2iai.catalog import Skylab2iaiCatalog as CatalogFromModule
        assert CatalogFromModule is Skylab2iaiCatalog, "Should be the same class"
