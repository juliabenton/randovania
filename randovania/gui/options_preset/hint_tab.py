import dataclasses
from typing import Dict

from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox, QWidget

from randovania.game_description.resources.translator_gate import TranslatorGate
from randovania.game_description.world_list import WorldList
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.interface_common.options import Options
from randovania.layout.hint_configuration import SkyTempleKeyHintMode


class HintTab:
    parent: QWidget
    presets_window: Ui_OptionsPresetWindow
    _options: Options

    _combo_for_gate: Dict[TranslatorGate, QComboBox]
    world_list: WorldList

    def __init__(self, parent: QWidget, presets_window: Ui_OptionsPresetWindow, options: Options):
        self.parent = parent
        self.presets_window = presets_window
        self._options = options

        # Update with Options
        self.setup_hint_elements()

        # Alignment
        self.presets_window.hint_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_options_changed(self, options: Options):
        # Hints
        set_combo_with_value(self.presets_window.hint_sky_temple_key_combo,
                             options.layout_configuration.hints.sky_temple_keys)

    # Hints
    def setup_hint_elements(self):
        for i, stk_hint_mode in enumerate(SkyTempleKeyHintMode):
            self.presets_window.hint_sky_temple_key_combo.setItemData(i, stk_hint_mode)

        self.presets_window.hint_sky_temple_key_combo.currentIndexChanged.connect(self._on_stk_combo_changed)

    def _on_stk_combo_changed(self, new_index: int):
        with self._options as options:
            options.set_layout_configuration_field(
                "hints",
                dataclasses.replace(options.layout_configuration.hints,
                                    sky_temple_keys=self.presets_window.hint_sky_temple_key_combo.currentData()))
