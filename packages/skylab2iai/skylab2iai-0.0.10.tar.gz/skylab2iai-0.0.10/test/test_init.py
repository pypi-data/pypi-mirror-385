"""Tests for package initialization."""
import skylab2iai

from skylab2iai import Skylab2iaiCatalog


class TestPackageInit:
    """Test suite for package __init__.py."""
    
    def test_version_exists(self):
        """Test that __version__ is defined."""
        assert hasattr(skylab2iai, '__version__'), "Package should have __version__"
        assert isinstance(skylab2iai.__version__, str), "__version__ should be a string"
    
    def test_version_format(self):
        """Test that version follows semantic versioning."""
        version = skylab2iai.__version__
        parts = version.split('.')
        assert len(parts) == 3, "Version should have 3 parts (major.minor.patch)"
        assert all(part.isdigit() for part in parts), "All version parts should be numeric"
    
    def test_catalog_exported(self):
        """Test that Skylab2iaiCatalog is exported."""
        assert 'Skylab2iaiCatalog' in skylab2iai.__all__, "Skylab2iaiCatalog should be in __all__"
    
    def test_catalog_importable(self):
        """Test that Skylab2iaiCatalog can be imported."""
        from skylab2iai import Skylab2iaiCatalog
        assert Skylab2iaiCatalog is not None, "Should be able to import Skylab2iaiCatalog"
    
    def test_catalog_instantiable(self):
        """Test that Skylab2iaiCatalog can be instantiated."""
        catalog = Skylab2iaiCatalog()
        assert catalog is not None, "Should be able to create catalog instance"
    
    def test_all_exports_valid(self):
        """Test that all items in __all__ are actually exported."""
        for item in skylab2iai.__all__:
            assert hasattr(skylab2iai, item), f"{item} should be accessible from package"
