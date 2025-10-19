import os
from typing import List, Optional, Union
from .formarts import AudioFormarts
from .utils.log.loger import get_logger
from .slicer_exceptions import SlicerException

logger = get_logger()


class DirBuster:
    def __init__(self, input_obj: Optional[Union[str, list[str], os.PathLike]]):
        self.input_obj = input_obj

    def get_dir_files(self):
        """
        Get file path list given dir/folder

        -------
        Args:
            path: path to the directory/folder
        Returns:
        -------
            list
        """
        files = [
            os.path.join(self.input_obj, f)
            for f in os.listdir(self.input_obj)
            if os.path.isfile(os.path.join(self.input_obj, f))
            and self._is_supported_file(f)
        ]
        if not files:  # Check for empty directory *after* filtering
            raise SlicerException(f"No supported file files found in: {self.input_obj}")
        return files

    def _is_supported_file(self, filename: str) -> bool:
        """Checks if a file has a supported extension."""
        return filename.lower().endswith(tuple(AudioFormarts().surpoted))

    def _get_files(self, files: list = None) -> List[str]:
        """
        Identifies files to process, handling both single files and directories.

        Returns:
            A list of paths to files.  Raises FileNotFoundError if no
            valid files are found.
        """
        files = self.input_obj if not files else files

        if isinstance(files, (str, os.PathLike)):
            if os.path.isfile(files):
                return [files]
            else:
                return self.get_dir_files(files)

        files_to_process = []
        for obj in files:
            if os.path.isfile(obj):
                if self._is_supported_file(obj):
                    files_to_process.append(obj)
                else:
                    logger.warning(f"Skipping unsupported file: {obj}")

            elif os.path.isdir(obj):
                files = self.get_dir_files(obj)
                if not files:  # Check for empty directory *after* filtering
                    raise SlicerException(f"No supported files found in: {obj}")
                files_to_process.extend(files)
            else:
                raise SlicerException(f"Input is not a valid file or directory: {obj}")
        return files_to_process

    def run(self):
        supported_files = self._get_files(self.input_obj)
        return supported_files
