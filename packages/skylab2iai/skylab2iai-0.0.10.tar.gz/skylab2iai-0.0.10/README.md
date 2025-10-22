# Skylab2IAI

A Python library for accessing and analyzing Skylab mission data from astronomical plate archives.

## Overview

Skylab2IAI provides a simple interface to query and download astronomical plate frame data from the Skylab mission. The library includes an embedded SQLite database containing metadata for thousands of plate frames and provides convenient methods to search, filter, and download FITS files.

## Installation

### From GitHub (for Google Colab or local use)

```bash
pip install git+https://github.com/tferrer/skylab2iai.git
```

### For local development

```bash
git clone https://github.com/tferrer/skylab2iai.git
cd skylab2iai
pip install -e .
```

## Quick Start

```python
from skylab2iai import Skylab2iaiCatalog

# Create a catalog instance
catalog = Skylab2iaiCatalog()

# Get all plate frames
all_frames = catalog.get_plate_frames()
print(f"Total plate frames: {len(all_frames)}")

# Get a specific plate frame by name
frame = catalog.get_plate_frame("plate_frame_name")
print(frame)

# Get all frames for a specific plate
plate_frames = catalog.get_plate_frames_by_plate("plate_id")
print(f"Frames for this plate: {len(plate_frames)}")
```

## Features

### Data Retrieval

- **`get_plate_frames()`**: Retrieve all plate frames from the database
- **`get_plate_frame(plate_frame_name)`**: Get a specific plate frame by name
- **`get_plate_frames_by_plate(plate_name)`**: Get all frames for a specific plate ID
- **`get_plate_frames_by_query(query)`**: Execute custom SQL queries (SELECT only, with SQL injection protection)

### FITS File Downloads

Download FITS files directly from the archive:

```python
# Download FITS files for specific plates
result_df, downloaded_files = catalog.download_fits_plate_frames(
    plate_names=("plate1", "plate2", "plate3"),
    output_dir="./fits_data"  # Optional, defaults to './fits_downloads'
)

print(f"Downloaded {len(downloaded_files)} files:")
for file_path in downloaded_files:
    print(f"  - {file_path}")
```

### Custom Queries

Execute custom SQL queries with built-in safety features:

```python
# Custom query example
query = "SELECT * FROM plate_frame WHERE PLATE_ID LIKE 'SKY%' LIMIT 10"
results = catalog.get_plate_frames_by_query(query)
print(results)

# Download FITS files from custom query
result_df, files = catalog.download_fits_plate_frames_from_custom_query(
    query="SELECT * FROM plate_frame WHERE PLATE_ID = 'specific_plate'",
    output_dir="./custom_downloads"
)
```

**Note**: Custom queries are restricted to SELECT statements only. DELETE, UPDATE, and INSERT operations are blocked for data integrity.

## Architecture

The library follows a layered architecture:

```
skylab2iai/
├── catalog/
│   └── catalog.py          # Main API (Skylab2iaiCatalog)
└── storage/
    ├── sql_connection.py   # SQLite connection manager (singleton)
    ├── plate_frame.py      # Plate frame data access layer
    ├── plate.py            # Plate data access layer
    └── skylab-data.db      # Embedded SQLite database (~1.8MB, 6408 frames)
```

### Key Components

1. **Skylab2iaiCatalog**: Main public API class providing high-level methods for data access and FITS downloads
2. **_SqlStorage**: Singleton connection manager for the embedded SQLite database
3. **_SkylabPlateStorage**: Data access layer with SQL injection protection

### Design Patterns

- **Singleton Pattern**: Database connection and storage classes use singleton pattern to ensure single instance
- **Repository Pattern**: Separation of data access logic from business logic
- **Immutability**: Storage classes are marked as `@final` to prevent inheritance

## Requirements

- Python >= 3.10
- pandas >= 2.0.0
- requests >= 2.31.0

## Database Schema

The embedded SQLite database contains a `plate_frame` table with the following key columns:

- `NAME`: Unique plate frame identifier
- `PLATE_ID`: Associated plate identifier
- `LINK_FTS`: URL to download the FITS file
- Additional metadata columns for astronomical observations

## Usage Examples

### Example 1: Explore the catalog

```python
from skylab2iai import Skylab2iaiCatalog

catalog = Skylab2iaiCatalog()

# Get all frames
frames = catalog.get_plate_frames()
print(f"Total frames: {len(frames)}")
print(frames.head())

# Check available columns
print(frames.columns.tolist())
```

### Example 2: Download specific plates

```python
from skylab2iai import Skylab2iaiCatalog

catalog = Skylab2iaiCatalog()

# Download FITS files for specific plates
plates_to_download = ("plate_001", "plate_002", "plate_003")
df, files = catalog.download_fits_plate_frames(
    plate_names=plates_to_download,
    output_dir="./my_fits_data"
)

print(f"Successfully downloaded {len(files)} FITS files")
```

### Example 3: Custom query with download

```python
from skylab2iai import Skylab2iaiCatalog

catalog = Skylab2iaiCatalog()

# Find frames matching specific criteria
query = """
    SELECT * FROM plate_frame 
    WHERE PLATE_ID LIKE 'SKY%' 
    LIMIT 5
"""

# Get the data
results = catalog.get_plate_frames_by_query(query)
print(results)

# Download FITS files for these results
df, files = catalog.download_fits_plate_frames_from_custom_query(
    query=query,
    output_dir="./skylab_subset"
)
```

## Troubleshooting

### Google Colab: "unable to open database file" or "no such table"

If you encounter database errors in Google Colab:

1. **Restart the runtime** and reinstall: 
   ```python
   # In Google Colab: Runtime > Restart runtime
   !pip install --force-reinstall git+https://github.com/tferrer/skylab2iai.git
   ```

2. **Clear pip cache** before installing:
   ```python
   !pip cache purge
   !pip install git+https://github.com/tferrer/skylab2iai.git
   ```

3. **Verify the installation**:
   ```python
   from skylab2iai import Skylab2iaiCatalog
   catalog = Skylab2iaiCatalog()
   frames = catalog.get_plate_frames()
   print(f"Loaded {len(frames)} plate frames")
   ```

The library includes a ~1.8MB SQLite database with 6408 plate frames. If you see this count, everything is working correctly!

### Import Errors

If you encounter import errors, ensure you're using the correct import:

```python
# Correct
from skylab2iai import Skylab2iaiCatalog

# Not PlateFrameService or other names
```

## Development

### Running Tests

The library includes a comprehensive test suite with 100% code coverage.

#### Install development dependencies
```bash
pip install -e ".[dev]"
```

#### Run tests
```bash
# Unix/macOS
./run_tests.sh

# Windows
run_tests.bat

# Or use pytest directly
pytest --cov=skylab2iai --cov-report=term-missing
```

#### Test coverage
The test suite covers:
- Unit tests for all modules
- Integration tests for complete workflows
- SQL injection prevention
- Error handling
- Singleton pattern implementation
- Mock tests for HTTP requests

See `test/README.md` for detailed testing documentation.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

When contributing:
1. Write tests for new features
2. Ensure all tests pass
3. Maintain 100% code coverage
4. Follow existing code style

## License

MIT License - see LICENSE file for details

## Author

Tiago Ferrer (ferrertiago@gmail.com)

