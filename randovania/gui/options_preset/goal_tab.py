from PySide2 import QtCore
from PySide2.QtWidgets import QWidget

from randovania.game_description.world_list import WorldList
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.interface_common.options import Options
from randovania.layout.layout_configuration import LayoutSkyTempleKeyMode


class GoalTab:
    parent: QWidget
    presets_window: Ui_OptionsPresetWindow
    _options: Options

    world_list: WorldList

    def __init__(self, parent: QWidget, presets_window: Ui_OptionsPresetWindow, options: Options):
        self.parent = parent
        self.presets_window = presets_window
        self._options = options

        # Update with Options
        self.setup_sky_temple_elements()

        # Alignment
        self.presets_window.goal_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_options_changed(self, options: Options):
        # Sky Temple Keys
        keys = options.layout_configuration_sky_temple_keys
        if isinstance(keys.value, int):
            self.presets_window.skytemple_slider.setValue(keys.value)
            data = int
        else:
            data = keys
        set_combo_with_value(self.presets_window.skytemple_combo, data)

    # Sky Temple Key
    def setup_sky_temple_elements(self):
        self.presets_window.skytemple_combo.setItemData(0, LayoutSkyTempleKeyMode.ALL_BOSSES)
        self.presets_window.skytemple_combo.setItemData(1, LayoutSkyTempleKeyMode.ALL_GUARDIANS)
        self.presets_window.skytemple_combo.setItemData(2, int)

        self.presets_window.skytemple_combo.options_field_name = "layout_configuration_sky_temple_keys"
        self.presets_window.skytemple_combo.currentIndexChanged.connect(self._on_sky_temple_key_combo_changed)
        self.presets_window.skytemple_slider.valueChanged.connect(self._on_sky_temple_key_combo_slider_changed)

    def _on_sky_temple_key_combo_changed(self):
        combo_enum = self.presets_window.skytemple_combo.currentData()
        with self._options:
            if combo_enum is int:
                self.presets_window.skytemple_slider.setEnabled(True)
                self._options.layout_configuration_sky_temple_keys = LayoutSkyTempleKeyMode(
                    self.presets_window.skytemple_slider.value())
            else:
                self.presets_window.skytemple_slider.setEnabled(False)
                self._options.layout_configuration_sky_temple_keys = combo_enum

    def _on_sky_temple_key_combo_slider_changed(self):
        self.presets_window.skytemple_slider_label.setText(str(self.presets_window.skytemple_slider.value()))
        self._on_sky_temple_key_combo_changed()
