from pathlib import Path

from randovania.interface_common import persistence


class DataPaths:
    _data_dir: Path

    def __init__(self, data_dir: Path):
        self._data_dir = data_dir

    @property
    def backup_files_path(self) -> Path:
        return self._data_dir.joinpath("backup")

    @property
    def game_files_path(self) -> Path:
        return self._data_dir.joinpath("extracted_game")

    @property
    def tracker_files_path(self) -> Path:
        return self._data_dir.joinpath("tracker")


def get_default_paths() -> DataPaths:
    return DataPaths(persistence.user_data_dir())