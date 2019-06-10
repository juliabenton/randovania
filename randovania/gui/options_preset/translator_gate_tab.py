import dataclasses
import functools
from typing import Dict

from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox, QLabel

from randovania.game_description.resources.translator_gate import TranslatorGate
from randovania.game_description.world_list import WorldList
from randovania.games.prime import default_data
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.translator_configuration import LayoutTranslatorRequirement, TranslatorConfiguration


class TranslatorGateTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    _combo_for_gate: Dict[TranslatorGate, QComboBox]
    world_list: WorldList

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor

        # Update with Options
        self.setup_translators_elements()

        # Alignment
        self.editor.translators_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Translator Gates
        translator_configuration = preset.layout.translator_configuration
        self.editor.always_up_gfmc_compound_check.setChecked(translator_configuration.fixed_gfmc_compound)
        self.editor.always_up_torvus_temple_check.setChecked(translator_configuration.fixed_torvus_temple)
        self.editor.always_up_great_temple_check.setChecked(translator_configuration.fixed_great_temple)
        for gate, combo in self._combo_for_gate.items():
            set_combo_with_value(combo, translator_configuration.translator_requirement[gate])

    # Translator Gates
    def setup_translators_elements(self):
        randomizer_data = default_data.decode_randomizer_data()

        self.editor.always_up_gfmc_compound_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_gfmc_compound"))
        self.editor.always_up_torvus_temple_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_torvus_temple"))
        self.editor.always_up_great_temple_check.stateChanged.connect(
            functools.partial(self._on_always_up_check_changed, "fixed_great_temple"))

        self.editor.translator_randomize_all_button.clicked.connect(self._on_randomize_all_gates_pressed)
        self.editor.translator_vanilla_actual_button.clicked.connect(self._on_vanilla_actual_gates_pressed)
        self.editor.translator_vanilla_colors_button.clicked.connect(self._on_vanilla_colors_gates_pressed)

        self._combo_for_gate = {}

        for i, gate in enumerate(randomizer_data["TranslatorLocationData"]):
            label = QLabel(self.editor.translators_scroll_contents)
            label.setText(gate["Name"])
            self.editor.translators_layout.addWidget(label, 3 + i, 0, 1, 1)

            combo = QComboBox(self.editor.translators_scroll_contents)
            combo.gate = TranslatorGate(gate["Index"])
            for item in LayoutTranslatorRequirement:
                combo.addItem(item.long_name, item)
            combo.currentIndexChanged.connect(functools.partial(self._on_gate_combo_box_changed, combo))

            self.editor.translators_layout.addWidget(combo, 3 + i, 1, 1, 2)
            self._combo_for_gate[combo.gate] = combo

    def _set_translator_configuration(self, configuration: TranslatorConfiguration):
        with self.editor as editor:
            editor.set_layout_field("translator_configuration", configuration)

    def _on_always_up_check_changed(self, field_name: str, new_value: int):
        self._set_translator_configuration(dataclasses.replace(self.editor.layout_configuration.translator_configuration,
                                                               **{field_name: bool(new_value)}))

    def _on_randomize_all_gates_pressed(self):
        self._set_translator_configuration(self.editor.layout_configuration.translator_configuration.with_full_random())

    def _on_vanilla_actual_gates_pressed(self):
        self._set_translator_configuration(self.editor.layout_configuration.translator_configuration.with_vanilla_actual())

    def _on_vanilla_colors_gates_pressed(self):
        self._set_translator_configuration(self.editor.layout_configuration.translator_configuration.with_vanilla_colors())

    def _on_gate_combo_box_changed(self, combo: QComboBox, new_index: int):
        self._set_translator_configuration(
            self.editor.layout_configuration.translator_configuration.replace_requirement_for_gate(
                combo.gate, combo.currentData()))
