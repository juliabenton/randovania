import dataclasses
import functools
from typing import Dict

from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox, QLabel, QWidget

from randovania.game_description.resources.translator_gate import TranslatorGate
from randovania.game_description.world_list import WorldList
from randovania.games.prime import default_data
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.interface_common.options import Options
from randovania.layout.hint_configuration import SkyTempleKeyHintMode
from randovania.layout.translator_configuration import LayoutTranslatorRequirement


class TranslatorGateTab:
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
        self.setup_translators_elements()

        # Alignment
        self.presets_window.translators_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_options_changed(self, options: Options):
        # Translator Gates
        translator_configuration = options.layout_configuration.translator_configuration
        self.presets_window.always_up_gfmc_compound_check.setChecked(translator_configuration.fixed_gfmc_compound)
        self.presets_window.always_up_torvus_temple_check.setChecked(translator_configuration.fixed_torvus_temple)
        self.presets_window.always_up_great_temple_check.setChecked(translator_configuration.fixed_great_temple)
        for gate, combo in self._combo_for_gate.items():
            set_combo_with_value(combo, translator_configuration.translator_requirement[gate])

    # Translator Gates
    def setup_translators_elements(self):
        randomizer_data = default_data.decode_randomizer_data()

        self.presets_window.always_up_gfmc_compound_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_gfmc_compound"))
        self.presets_window.always_up_torvus_temple_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_torvus_temple"))
        self.presets_window.always_up_great_temple_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_great_temple"))

        self.presets_window.translator_randomize_all_button.clicked.connect(self._on_randomize_all_gates_pressed)
        self.presets_window.translator_vanilla_actual_button.clicked.connect(self._on_vanilla_actual_gates_pressed)
        self.presets_window.translator_vanilla_colors_button.clicked.connect(self._on_vanilla_colors_gates_pressed)

        self._combo_for_gate = {}

        for i, gate in enumerate(randomizer_data["TranslatorLocationData"]):
            label = QLabel(self.presets_window.translators_scroll_contents)
            label.setText(gate["Name"])
            self.presets_window.translators_layout.addWidget(label, 3 + i, 0, 1, 1)

            combo = QComboBox(self.presets_window.translators_scroll_contents)
            combo.gate = TranslatorGate(gate["Index"])
            for item in LayoutTranslatorRequirement:
                combo.addItem(item.long_name, item)
            combo.currentIndexChanged.connect(functools.partial(self._on_gate_combo_box_changed, combo))

            self.presets_window.translators_layout.addWidget(combo, 3 + i, 1, 1, 2)
            self._combo_for_gate[combo.gate] = combo

    def _on_always_up_check_changed(self, field_name: str, new_value: int):
        with self._options as options:
            options.set_layout_configuration_field(
                "translator_configuration",
                dataclasses.replace(options.layout_configuration.translator_configuration,
                                    **{field_name: bool(new_value)}))

    def _on_randomize_all_gates_pressed(self):
        with self._options as options:
            options.set_layout_configuration_field(
                "translator_configuration",
                options.layout_configuration.translator_configuration.with_full_random())

    def _on_vanilla_actual_gates_pressed(self):
        with self._options as options:
            options.set_layout_configuration_field(
                "translator_configuration",
                options.layout_configuration.translator_configuration.with_vanilla_actual())

    def _on_vanilla_colors_gates_pressed(self):
        with self._options as options:
            options.set_layout_configuration_field(
                "translator_configuration",
                options.layout_configuration.translator_configuration.with_vanilla_colors())

    def _on_gate_combo_box_changed(self, combo: QComboBox, new_index: int):
        with self._options as options:
            options.set_layout_configuration_field(
                "translator_configuration",
                options.layout_configuration.translator_configuration.replace_requirement_for_gate(
                    combo.gate, combo.currentData()))
