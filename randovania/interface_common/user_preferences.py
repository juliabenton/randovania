from distutils.version import StrictVersion
from pathlib import Path
from typing import Optional, Tuple

from randovania.interface_common import update_checker
from randovania.interface_common.cosmetic_patches import CosmeticPatches
from randovania.interface_common.editable_object import EditableObject
from randovania.interface_common.serializer import identity, Serializer, return_with_default

_SERIALIZER_FOR_FIELD = {
    "last_changelog_displayed": Serializer(identity, str),
    "advanced_validate_seed_after": Serializer(identity, bool),
    "advanced_timeout_during_generation": Serializer(identity, bool),
    "create_spoiler": Serializer(identity, bool),
    "output_directory": Serializer(str, Path),
    "cosmetic_patches": Serializer(lambda p: p.as_json, CosmeticPatches.from_json_dict),
    "selected_preset_is_custom": Serializer(identity, bool),
    "custom_options_preset": Serializer(identity, tuple),
}


class UserPreferences(EditableObject):
    _last_changelog_displayed: str
    _output_directory: Optional[Path] = None

    _advanced_validate_seed_after: Optional[bool] = None
    _advanced_timeout_during_generation: Optional[bool] = None
    _seed_number: Optional[int] = None
    _create_spoiler: Optional[bool] = None
    _cosmetic_patches: Optional[CosmeticPatches] = None
    _selected_options_preset: Optional[str] = None
    _selected_preset_is_custom: bool = False
    _custom_options_preset: Optional[Tuple[str, ...]] = None

    def __init__(self):
        self._last_changelog_displayed = str(update_checker.strict_current_version())

    # Reset
    def reset_to_defaults(self):
        self._advanced_validate_seed_after = None
        self._advanced_timeout_during_generation = None
        self._create_spoiler = None
        self._cosmetic_patches = None
        self._selected_options_preset = None
        self._selected_preset_is_custom = False
        self._custom_options_preset = None

    # Access to Direct fields
    @property
    def last_changelog_displayed(self) -> StrictVersion:
        return StrictVersion(self._last_changelog_displayed)

    @last_changelog_displayed.setter
    def last_changelog_displayed(self, value: StrictVersion):
        if value != self.last_changelog_displayed:
            self._check_editable_and_mark_dirty()
            self._last_changelog_displayed = str(value)

    @property
    def seed_number(self) -> Optional[int]:
        return self._seed_number

    @seed_number.setter
    def seed_number(self, value: Optional[int]):
        self.edit_field("seed_number", value)

    @property
    def create_spoiler(self) -> bool:
        return return_with_default(self._create_spoiler, lambda: True)

    @create_spoiler.setter
    def create_spoiler(self, value: bool):
        self.edit_field("create_spoiler", value)

    @property
    def output_directory(self) -> Optional[Path]:
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value: Optional[Path]):
        self.edit_field("output_directory", value)

    @property
    def cosmetic_patches(self) -> CosmeticPatches:
        return return_with_default(self._cosmetic_patches, CosmeticPatches.default)

    @cosmetic_patches.setter
    def cosmetic_patches(self, value: CosmeticPatches):
        self.edit_field("cosmetic_patches", value)

    # Advanced

    @property
    def advanced_validate_seed_after(self) -> bool:
        return return_with_default(self._advanced_validate_seed_after, lambda: True)

    @advanced_validate_seed_after.setter
    def advanced_validate_seed_after(self, value: bool):
        self.edit_field("advanced_validate_seed_after", value)

    @property
    def advanced_timeout_during_generation(self) -> bool:
        return return_with_default(self._advanced_timeout_during_generation, lambda: True)

    @advanced_timeout_during_generation.setter
    def advanced_timeout_during_generation(self, value: bool):
        self.edit_field("advanced_timeout_during_generation", value)
