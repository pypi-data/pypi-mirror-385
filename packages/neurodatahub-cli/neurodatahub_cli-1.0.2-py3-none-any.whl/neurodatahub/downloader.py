"""Download functionality with multiple backends."""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from rich.console import Console
from rich.progress import (
    BarColumn, 
    DownloadColumn, 
    Progress, 
    TaskID, 
    TextColumn, 
    TimeRemainingColumn,
    TransferSpeedColumn
)
from tqdm import tqdm

from .utils import (
    check_dependency, 
    display_error, 
    display_success, 
    display_info, 
    display_warning,
    run_command,
    validate_path,
    check_available_space
)

console = Console()


class DownloadError(Exception):
    """Custom exception for download errors."""
    pass


class BaseDownloader:
    """Base class for all downloaders."""

    def __init__(self, dataset: Dict, target_path: str):
        self.dataset = dataset
        self.target_path = Path(target_path)
        self.dataset_name = dataset.get('name', 'Unknown Dataset')
        self.dataset_size = dataset.get('size', 'Unknown')

        # Create subdirectories for organized storage
        self.anat_path = self.target_path / "anat"
        self.metadata_path = self.target_path / "metadata"

    def _create_folder_structure(self) -> bool:
        """Create anat/ and metadata/ subdirectories."""
        try:
            self.anat_path.mkdir(parents=True, exist_ok=True)
            self.metadata_path.mkdir(parents=True, exist_ok=True)
            display_info(f"Created folder structure:")
            display_info(f"  - {self.anat_path} (anatomical images)")
            display_info(f"  - {self.metadata_path} (dataset metadata)")
            return True
        except Exception as e:
            display_error(f"Failed to create folder structure: {e}")
            return False

    def _download_metadata_from_urls(self, metadata_urls: List[str]) -> bool:
        """Download metadata files from URLs using requests."""
        if not metadata_urls:
            return True

        display_info("Downloading metadata files...")
        success_count = 0

        for url in metadata_urls:
            try:
                filename = url.split('/')[-1]
                filepath = self.metadata_path / filename

                display_info(f"Downloading {filename}...")
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))

                with open(filepath, 'wb') as f:
                    if total_size > 0:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                display_success(f"  ✓ {filename} downloaded to metadata/")
                success_count += 1

            except Exception as e:
                display_warning(f"  Could not download {url.split('/')[-1]}: {e}")

        if success_count > 0:
            display_success(f"Downloaded {success_count}/{len(metadata_urls)} metadata files")
            return True
        return False

    def prepare(self) -> bool:
        """Prepare for download (validate paths, check dependencies, etc.)."""
        # Validate target path
        if not validate_path(str(self.target_path)):
            return False

        # Check available disk space
        if not check_available_space(str(self.target_path), self.dataset_size):
            return False

        # Create organized folder structure
        if not self._create_folder_structure():
            return False

        return True
    
    def download(self, dry_run: bool = False) -> bool:
        """Execute the download. Should be implemented by subclasses."""
        raise NotImplementedError
    
    def cleanup(self):
        """Cleanup after download (optional)."""
        pass


class AwsS3Downloader(BaseDownloader):
    """Downloader for AWS S3 datasets (INDI, OpenNeuro)."""

    def __init__(self, dataset: Dict, target_path: str):
        super().__init__(dataset, target_path)
        self.base_command = dataset.get('base_command', '')
        self.requires_credentials = dataset.get('download_method') == 'aws_credentials'
        self.category = dataset.get('category', '').lower()
        self.is_openneuro = self.category == 'openneuro' or 'openneuro.org' in self.base_command
    
    def prepare(self) -> bool:
        if not super().prepare():
            return False
        
        # Check if AWS CLI is available
        if not check_dependency('aws'):
            display_error(
                "AWS CLI is not installed",
                "Install with: pip install awscli  OR  conda install -c conda-forge awscli"
            )
            return False
        
        # Check AWS credentials if required
        if self.requires_credentials:
            result = run_command('aws configure list', capture_output=True)
            if result[0] != 0:
                display_error(
                    "AWS credentials not configured",
                    "Run 'aws configure' to set up your credentials"
                )
                return False
        
        return True
    
    def download(self, dry_run: bool = False) -> bool:
        if not self.base_command:
            display_error("No download command configured for this dataset")
            return False

        # Replace placeholder in command with anat/ folder for anatomical images
        command = self.base_command.replace(' .', f' "{self.anat_path}"')

        if dry_run:
            display_info(f"Would run: {command}")
            display_info(f"Anatomical images would be downloaded to: {self.anat_path}")
            return True

        display_info(f"Starting download of {self.dataset_name}")
        display_info(f"Anatomical images will be saved to: {self.anat_path}")
        display_info(f"Command: {command}")

        # Run the AWS command
        start_time = time.time()
        returncode, stdout, stderr = run_command(command, capture_output=False)

        if returncode == 0:
            elapsed = time.time() - start_time
            display_success(f"Download completed in {elapsed:.1f} seconds")

            # Download metadata if specified (e.g., for NKI, other INDI datasets)
            metadata_urls = self.dataset.get('metadata_urls', [])
            if metadata_urls:
                self._download_metadata_from_urls(metadata_urls)

            # Download OpenNeuro BIDS metadata using metadata_command
            metadata_command = self.dataset.get('metadata_command')
            if metadata_command:
                self._download_metadata_with_command(metadata_command)

            return True
        else:
            display_error(f"Download failed with exit code {returncode}")
            if stderr:
                console.print(f"[red]Error output:[/red] {stderr}")
            return False

    def _download_metadata_with_command(self, metadata_command: str) -> bool:
        """Download metadata files using AWS command (for OpenNeuro BIDS datasets)."""
        display_info("Downloading BIDS metadata files...")

        # Replace the destination path to download to metadata/ folder
        # The command template is: aws s3 sync --no-sign-request s3://... . --exclude "*" --include "*.tsv" --include "*.json"
        # We need to replace the '.' with our metadata_path
        command = metadata_command.replace(' . ', f' "{self.metadata_path}" ')

        display_info(f"Fetching .tsv and .json files from OpenNeuro...")

        returncode, stdout, stderr = run_command(command, capture_output=False)

        if returncode == 0:
            display_success("✓ BIDS metadata files downloaded to metadata/")
            return True
        else:
            display_warning("Could not download some metadata files (this is normal if they don't exist)")
            return False


class Aria2cDownloader(BaseDownloader):
    """Downloader using aria2c for fast parallel downloads."""
    
    def __init__(self, dataset: Dict, target_path: str):
        super().__init__(dataset, target_path)
        self.base_command = dataset.get('base_command', '')
    
    def prepare(self) -> bool:
        if not super().prepare():
            return False
        
        # Check if aria2c is available
        if not check_dependency('aria2c'):
            display_error(
                "aria2c is not installed",
                "Install with: brew install aria2  OR  apt-get install aria2  OR  conda install -c conda-forge aria2"
            )
            return False
        
        return True
    
    def download(self, dry_run: bool = False) -> bool:
        if not self.base_command:
            display_error("No download command configured for this dataset")
            return False

        if self.base_command == "multiple_aria2c_downloads":
            return self._download_multiple_files(dry_run)

        # Single file download to anat/ folder
        command = f"{self.base_command} --dir=\"{self.anat_path}\""

        if dry_run:
            display_info(f"Would run: {command}")
            display_info(f"Files would be downloaded to: {self.anat_path}")
            return True

        display_info(f"Starting download of {self.dataset_name}")
        display_info(f"Files will be saved to: {self.anat_path}")

        start_time = time.time()
        returncode, stdout, stderr = run_command(command, capture_output=False)

        if returncode == 0:
            elapsed = time.time() - start_time
            display_success(f"Download completed in {elapsed:.1f} seconds")

            # Download metadata if specified (e.g., for OASIS datasets)
            metadata_urls = self.dataset.get('metadata_urls', [])
            if metadata_urls:
                self._download_metadata_from_urls(metadata_urls)

            return True
        else:
            display_error(f"Download failed with exit code {returncode}")
            if stderr:
                console.print(f"[red]Error output:[/red] {stderr}")
            return False
    
    def _download_multiple_files(self, dry_run: bool = False) -> bool:
        """Handle datasets that require multiple aria2c downloads (like OASIS)."""
        # Get dataset name or ID
        dataset_name = self.dataset.get('name', 'UNKNOWN')

        if "OASIS1" in dataset_name:
            urls = [
                "https://www.oasis-brains.org/files/oasis_cross-sectional.tar.gz",
                "https://www.oasis-brains.org/files/oasis_longitudinal.tar.gz"
            ]
        elif "OASIS2" in dataset_name:
            urls = [
                "https://www.oasis-brains.org/files/oasis_longitudinal.tar.gz"
            ]
        else:
            display_error("Multiple download configuration not found for this dataset")
            return False

        if dry_run:
            for url in urls:
                display_info(f"Would download: {url}")
            display_info(f"Files would be saved to: {self.anat_path}")
            return True

        success = True
        for i, url in enumerate(urls, 1):
            display_info(f"Downloading file {i}/{len(urls)}: {url}")
            command = f"aria2c -x 10 -j 10 -s 10 \"{url}\" --dir=\"{self.anat_path}\""

            returncode, stdout, stderr = run_command(command, capture_output=False)
            if returncode != 0:
                display_error(f"Failed to download {url}")
                success = False

        # Download metadata if the download was successful
        if success:
            metadata_urls = self.dataset.get('metadata_urls', [])
            if metadata_urls:
                self._download_metadata_from_urls(metadata_urls)

        return success


class DataladDownloader(BaseDownloader):
    """Downloader for DataLad/Git-based datasets (RBC and OpenNeuro BIDS)."""

    def __init__(self, dataset: Dict, target_path: str):
        super().__init__(dataset, target_path)
        self.base_command = dataset.get('base_command', '')
        self.repository = dataset.get('repository', '')
        self.category = dataset.get('category', '').lower()
        self.is_openneuro = self.category == 'openneuro' or 'openneuro' in self.repository.lower()

    def prepare(self) -> bool:
        if not super().prepare():
            return False

        # Check dependencies
        missing_deps = []
        if not check_dependency('git'):
            missing_deps.append('git')
        if not check_dependency('datalad'):
            missing_deps.append('datalad')

        if missing_deps:
            display_error(
                f"Missing dependencies: {', '.join(missing_deps)}",
                "Install git from https://git-scm.com/ and datalad with: pip install datalad"
            )
            return False

        return True
    
    def download(self, dry_run: bool = False) -> bool:
        if not self.repository:
            display_error("No repository URL configured for this dataset")
            return False

        # Parse the commands from base_command
        commands = self.base_command.split(' && ')

        if dry_run:
            display_info("Would execute the following commands:")
            for cmd in commands:
                display_info(f"  {cmd}")
            if self.is_openneuro:
                display_info("Would download BIDS metadata files to metadata/ folder")
            return True

        display_info(f"Starting DataLad download of {self.dataset_name}")
        display_info(f"Repository: {self.repository}")
        display_info(f"Target location: {self.target_path}")

        # Change to target directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.target_path)

            # Execute main download commands
            for i, cmd in enumerate(commands, 1):
                display_info(f"Executing step {i}/{len(commands)}: {cmd}")
                returncode, stdout, stderr = run_command(cmd, capture_output=False)

                if returncode != 0:
                    display_error(f"Command failed: {cmd}")
                    if stderr:
                        console.print(f"[red]Error output:[/red] {stderr}")
                    return False

            # For OpenNeuro/BIDS datasets, download metadata files
            if self.is_openneuro:
                if not self._download_bids_metadata():
                    display_warning("Failed to download some BIDS metadata files, but continuing...")

            # For RBC datasets with specific metadata files
            metadata_files = self.dataset.get('metadata_files', [])
            if metadata_files:
                if not self._download_rbc_metadata(metadata_files):
                    display_warning("Failed to download some RBC metadata files, but continuing...")

            display_success("DataLad download completed successfully")
            return True

        except Exception as e:
            display_error(f"Download failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)

    def _download_bids_metadata(self) -> bool:
        """Download BIDS metadata files to metadata/ folder."""
        display_info("Downloading BIDS metadata files...")

        # List of BIDS metadata files to download
        metadata_files = [
            'dataset_description.json',
            'participants.json',
            'participants.tsv',
        ]

        success = True
        for metadata_file in metadata_files:
            # Use datalad get to fetch the specific file
            get_cmd = f"datalad get {metadata_file}"
            display_info(f"Fetching {metadata_file}...")

            returncode, stdout, stderr = run_command(get_cmd, capture_output=True)

            if returncode == 0:
                # Move the file to metadata/ folder
                source_file = Path(metadata_file)
                if source_file.exists():
                    import shutil
                    dest_file = self.metadata_path / source_file.name
                    try:
                        shutil.move(str(source_file), str(dest_file))
                        display_success(f"  ✓ {metadata_file} saved to metadata/")
                    except Exception as e:
                        display_warning(f"  Could not move {metadata_file}: {e}")
                        success = False
                else:
                    display_warning(f"  {metadata_file} not found in dataset (may not exist)")
            else:
                display_warning(f"  {metadata_file} not available (may not exist in this dataset)")

        return success

    def _download_rbc_metadata(self, metadata_files: List[str]) -> bool:
        """Download RBC-specific metadata files to metadata/ folder."""
        display_info("Downloading RBC metadata files...")

        success = True
        for metadata_file in metadata_files:
            # Use datalad get to fetch the specific file
            get_cmd = f"datalad get {metadata_file}"
            display_info(f"Fetching {metadata_file}...")

            returncode, stdout, stderr = run_command(get_cmd, capture_output=True)

            if returncode == 0:
                # Move the file to metadata/ folder
                source_file = Path(metadata_file)
                if source_file.exists():
                    import shutil
                    dest_file = self.metadata_path / source_file.name
                    try:
                        shutil.move(str(source_file), str(dest_file))
                        display_success(f"  ✓ {metadata_file} saved to metadata/")
                    except Exception as e:
                        display_warning(f"  Could not move {metadata_file}: {e}")
                        success = False
                else:
                    display_warning(f"  {metadata_file} not found in dataset (may not exist)")
            else:
                display_warning(f"  {metadata_file} not available (may not exist in this dataset)")

        return success


class RequestsDownloader(BaseDownloader):
    """Fallback downloader using Python requests."""
    
    def __init__(self, dataset: Dict, target_path: str, url: str):
        super().__init__(dataset, target_path)
        self.url = url
    
    def download(self, dry_run: bool = False) -> bool:
        if dry_run:
            display_info(f"Would download from: {self.url}")
            display_info(f"Would save to: {self.anat_path}")
            return True

        try:
            display_info(f"Downloading {self.dataset_name} from {self.url}")

            response = requests.get(self.url, stream=True)
            response.raise_for_status()

            # Get filename from URL or use default
            filename = self.url.split('/')[-1] or f"{self.dataset_name.lower()}.tar.gz"
            filepath = self.anat_path / filename

            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))

            with open(filepath, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            display_success(f"Downloaded to {filepath}")
            return True

        except Exception as e:
            display_error(f"Download failed: {e}")
            return False


class DownloadManager:
    """Manages the download process for different dataset types."""
    
    def __init__(self):
        self.downloaders = {
            'aws_s3': AwsS3Downloader,
            'aws_credentials': AwsS3Downloader,
            'aria2c': Aria2cDownloader,
            'datalad': DataladDownloader,
        }
    
    def get_downloader(self, dataset: Dict, target_path: str) -> Optional[BaseDownloader]:
        """Get the appropriate downloader for a dataset."""
        download_method = dataset.get('download_method', 'requests')
        
        if download_method in self.downloaders:
            return self.downloaders[download_method](dataset, target_path)
        elif download_method == 'ida_loni':
            # IDA-LONI downloads are handled separately
            display_error("IDA-LONI downloads require interactive authentication. Use 'neurodatahub pull' with the dataset ID.")
            return None
        elif download_method == 'special':
            display_error("This dataset requires a special download procedure. Please check the dataset documentation.")
            return None
        else:
            display_warning(f"Unknown download method '{download_method}', will try fallback methods")
            return None
    
    def download_dataset(self, dataset: Dict, target_path: str, dry_run: bool = False) -> bool:
        """Download a dataset using the appropriate method."""
        downloader = self.get_downloader(dataset, target_path)
        
        if not downloader:
            return self._try_fallback_download(dataset, target_path, dry_run)
        
        if not downloader.prepare():
            return False
        
        try:
            success = downloader.download(dry_run)
            downloader.cleanup()
            return success
        except Exception as e:
            display_error(f"Download failed: {e}")
            downloader.cleanup()
            return False
    
    def _try_fallback_download(self, dataset: Dict, target_path: str, dry_run: bool = False) -> bool:
        """Try fallback download methods when primary method fails."""
        display_info("Attempting fallback download methods...")
        
        # Try to extract a URL from the base command
        base_command = dataset.get('base_command', '')
        if 'http' in base_command:
            # Extract URL from command
            import re
            urls = re.findall(r'https?://[^\s]+', base_command)
            if urls:
                downloader = RequestsDownloader(dataset, target_path, urls[0])
                return downloader.download(dry_run)
        
        display_error("No suitable download method available for this dataset")
        return False


# Global download manager instance
download_manager = DownloadManager()