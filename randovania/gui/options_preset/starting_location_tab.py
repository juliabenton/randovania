from typing import Optional

from PySide2 import QtCore

from randovania.game_description import default_database
from randovania.game_description.area_location import AreaLocation
from randovania.game_description.world_list import WorldList
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.starting_location import StartingLocationConfiguration, StartingLocation


class StartingLocationTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor
    world_list: WorldList

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor
        self.game_description = default_database.default_prime2_game_description()
        self.world_list = self.game_description.world_list

        # Update with Options
        self.setup_starting_area_elements()

        # Alignment
        self.editor.starting_area_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Starting Area
        starting_location = preset.layout.starting_location
        set_combo_with_value(self.editor.startingarea_combo, starting_location.configuration)

        if starting_location.configuration == StartingLocationConfiguration.CUSTOM:
            area_location = starting_location.custom_location
            world = self.world_list.world_by_asset_id(area_location.world_asset_id)

            set_combo_with_value(self.editor.specific_starting_world_combo, world)
            set_combo_with_value(self.editor.specific_starting_area_combo,
                                 world.area_by_asset_id(area_location.area_asset_id))

    # Starting Area
    def setup_starting_area_elements(self):
        self.editor.startingarea_combo.setItemData(0, StartingLocationConfiguration.SHIP)
        self.editor.startingarea_combo.setItemData(1, StartingLocationConfiguration.RANDOM_SAVE_STATION)
        self.editor.startingarea_combo.setItemData(2, StartingLocationConfiguration.CUSTOM)

        for world in sorted(self.world_list.worlds, key=lambda x: x.name):
            self.editor.specific_starting_world_combo.addItem(world.name, userData=world)

        self.editor.specific_starting_world_combo.currentIndexChanged.connect(self._on_select_world)
        self.editor.specific_starting_area_combo.currentIndexChanged.connect(self._on_select_area)
        self.editor.startingarea_combo.currentIndexChanged.connect(self._on_starting_area_configuration_changed)

    def _on_starting_area_configuration_changed(self):
        specific_enabled = self.editor.startingarea_combo.currentData() == StartingLocationConfiguration.CUSTOM
        self.editor.specific_starting_world_combo.setEnabled(specific_enabled)
        self.editor.specific_starting_area_combo.setEnabled(specific_enabled)
        self._on_select_world()
        self._update_starting_location()

    def _on_select_world(self):
        self.editor.specific_starting_area_combo.clear()
        for area in sorted(self.editor.specific_starting_world_combo.currentData().areas, key=lambda x: x.name):
            self.editor.specific_starting_area_combo.addItem(area.name, userData=area)

    def _on_select_area(self):
        if self.editor.specific_starting_area_combo.currentData() is not None:
            self._update_starting_location()

    def _update_starting_location(self):
        if self._has_valid_starting_location():
            with self.editor as editor:
                editor.set_layout_field(
                    "starting_location",
                    StartingLocation(self.editor.startingarea_combo.currentData(),
                                     self.current_starting_area_location))

    @property
    def current_starting_area_location(self) -> Optional[AreaLocation]:
        if self.editor.specific_starting_world_combo.isEnabled():
            return AreaLocation(
                self.editor.specific_starting_world_combo.currentData().world_asset_id,
                self.editor.specific_starting_area_combo.currentData().area_asset_id,
            )
        else:
            return None

    def _has_valid_starting_location(self):
        current_config = self.editor.startingarea_combo.currentData()
        if current_config == StartingLocationConfiguration.CUSTOM:
            return self.editor.specific_starting_area_combo.currentData() is not None
        else:
            return True
