import dataclasses

from PySide2 import QtCore

from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.hint_configuration import SkyTempleKeyHintMode


class HintTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor

        # Update with Options
        self.setup_hint_elements()

        # Alignment
        self.editor.hint_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Hints
        set_combo_with_value(self.editor.hint_sky_temple_key_combo,
                             preset.layout.hints.sky_temple_keys)

    # Hints
    def setup_hint_elements(self):
        for i, stk_hint_mode in enumerate(SkyTempleKeyHintMode):
            self.editor.hint_sky_temple_key_combo.setItemData(i, stk_hint_mode)

        self.editor.hint_sky_temple_key_combo.currentIndexChanged.connect(self._on_stk_combo_changed)

    def _on_stk_combo_changed(self, new_index: int):
        with self.editor as editor:
            editor.set_layout_field(
                "hints",
                dataclasses.replace(editor.layout_configuration.hints,
                                    sky_temple_keys=self.editor.hint_sky_temple_key_combo.currentData()))
