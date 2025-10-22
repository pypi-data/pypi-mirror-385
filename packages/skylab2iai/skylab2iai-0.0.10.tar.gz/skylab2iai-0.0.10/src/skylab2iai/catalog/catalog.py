from concurrent.futures import ThreadPoolExecutor, as_completed
from io import UnsupportedOperation
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


class Skylab2iaiCatalog:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Skylab2iaiCatalog, cls).__new__(cls)
            cls._instance._repository = None
        return cls._instance

    def __init__(self):
        if self._repository is None:
            from ..storage.plate_frame import _SkylabPlateStorage
            self._repository = _SkylabPlateStorage()

    @property
    def __repository(self):
        return self._repository

    def get_plate_frame(self, plate_frame_name: str):
        return self.__repository.get_plate_frame(plate_frame_name)

    def get_plate_frames(self):
        return self.__repository.get_plate_frames()

    def get_plate_frames_by_plate(self, plate_name: str):
        return self.__repository.get_plate_frames_by_plate(plate_name)

    def get_plate_frames_by_query(self, query: str):
        return self._repository.get_from_custom_query(query)

    def download_fits_plate_frames(self, plate_names: tuple, output_dir: Optional[str] = None, max_workers: Optional[int] = None):
        """
        Download FITS files for the specified plate frames using parallel processing.
        
        Args:
            plate_names: A tuple of plate frame names to download
            output_dir: Directory to save downloaded files (default: './fits_downloads')
            max_workers: Maximum number of parallel downloads (default: min(32, cpu_count + 4))
            
        Returns:
            A tuple containing (DataFrame of plate frames, list of downloaded file paths)
        """
        # Setup output directory
        if output_dir is None:
            output_dir = './fits_downloads'

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Initialize result containers
        result_frames_list = []
        downloaded_files = []

        # Prepare download tasks
        download_tasks = []
        for plate_name in plate_names:
            try:
                plate_frame = self.__repository.get_plate_frame(plate_name)

                if plate_frame.empty:
                    print(f"Warning: Plate frame '{plate_name}' not found in database")
                    continue

                # Add this frame to our results
                result_frames_list.append(plate_frame)

                # Get the FITS link
                if 'LINK_FTS' not in plate_frame.columns:
                    print(f"Warning: No LINK_FTS column for plate frame '{plate_name}'")
                    continue

                link_fits = plate_frame.iloc[0]['LINK_FTS']
                if not link_fits:
                    print(f"Warning: Empty LINK_FTS for plate frame '{plate_name}'")
                    continue

                download_tasks.append((link_fits, output_path, plate_name))

            except Exception as e:
                print(f"Error processing plate frame '{plate_name}': {str(e)}")

        # Download files in parallel using ThreadPoolExecutor
        if download_tasks:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all download tasks
                future_to_plate = {
                    executor.submit(self._download_single_file, url, output_dir, plate_name): plate_name
                    for url, output_dir, plate_name in download_tasks
                }

                # Collect results as they complete
                for future in as_completed(future_to_plate):
                    plate_name = future_to_plate[future]
                    try:
                        file_path = future.result()
                        if file_path:
                            downloaded_files.append(file_path)
                    except Exception as e:
                        print(f"Error downloading file for '{plate_name}': {str(e)}")

        # Combine all frames into a single DataFrame
        result_df = pd.DataFrame()
        if result_frames_list:
            # If we have only one frame, just return it directly
            if len(result_frames_list) == 1:
                result_df = result_frames_list[0]
            else:
                # Otherwise try to concatenate
                try:
                    result_df = pd.concat(result_frames_list, ignore_index=True)
                except Exception as concat_error:
                    print(f"Error combining DataFrames: {str(concat_error)}")
                    # If concat fails, return the first frame
                    result_df = result_frames_list[0]

        return result_df, downloaded_files

    def _download_single_file(self, url, output_dir, file_prefix):
        """
        Helper method to download a single file from a URL
        
        Args:
            url: The URL to download from
            output_dir: Directory to save the file
            file_prefix: Prefix for the filename
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        try:
            print(f"Downloading FITS file from {url}")

            # Make the HTTP request
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Prepare the output file path
            file_name = f"{file_prefix}.fits"
            file_path = output_dir / file_name

            # Write the file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Successfully downloaded: {file_path}")
            return str(file_path)

        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None

    def download_fits_plate_frames_from_custom_query(self, query: str, output_dir: Optional[str] = None, max_workers: Optional[int] = None):
        """
        Download FITS files from a custom query using parallel processing.
        
        Args:
            query: SQL query to retrieve plate frames
            output_dir: Directory to save downloaded files (default: './fits_downloads')
            max_workers: Maximum number of parallel downloads (default: min(32, cpu_count + 4))
            
        Returns:
            A tuple containing (DataFrame of plate frames, list of downloaded file paths)
        """
        if output_dir is None:
            output_dir = './fits_downloads'

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        plate_frames = self._repository.get_from_custom_query(query)

        if plate_frames.empty:
            raise UnsupportedOperation(f"Warning: No plate frames found for query '{query}'")

        # Prepare download tasks
        download_tasks = []
        for index, row in plate_frames.iterrows():
            plate_frame_name = row["NAME"]
            link_fit = row["LINK_FTS"]
            download_tasks.append((link_fit, output_path, plate_frame_name))

        # Download files in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_plate = {
                executor.submit(self._download_single_file, url, output_dir, plate_name): plate_name
                for url, output_dir, plate_name in download_tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_plate):
                plate_name = future_to_plate[future]
                try:
                    file_path = future.result()
                    if file_path:
                        downloaded_files.append(file_path)
                except Exception as e:
                    print(f"Error downloading FITS file for '{plate_name}': {str(e)}")

        return plate_frames, downloaded_files

    def df_by_query(self, query: str):
        return self._repository.get_from_custom_query(query)