from PySide2 import QtCore

from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.layout_configuration import LayoutSkyTempleKeyMode


class GoalTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor

        # Update with Options
        self.setup_sky_temple_elements()

        # Alignment
        self.editor.goal_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Sky Temple Keys
        keys = preset.layout.sky_temple_keys
        if isinstance(keys.value, int):
            self.editor.skytemple_slider.setValue(keys.value)
            data = int
        else:
            data = keys
        set_combo_with_value(self.editor.skytemple_combo, data)

    # Sky Temple Key
    def setup_sky_temple_elements(self):
        self.editor.skytemple_combo.setItemData(0, LayoutSkyTempleKeyMode.ALL_BOSSES)
        self.editor.skytemple_combo.setItemData(1, LayoutSkyTempleKeyMode.ALL_GUARDIANS)
        self.editor.skytemple_combo.setItemData(2, int)

        self.editor.skytemple_combo.options_field_name = "layout_configuration_sky_temple_keys"
        self.editor.skytemple_combo.currentIndexChanged.connect(self._on_sky_temple_key_combo_changed)
        self.editor.skytemple_slider.valueChanged.connect(self._on_sky_temple_key_combo_slider_changed)

    def _on_sky_temple_key_combo_changed(self):
        combo_enum = self.editor.skytemple_combo.currentData()
        with self.editor as editor:
            if combo_enum is int:
                self.editor.skytemple_slider.setEnabled(True)
                editor.set_layout_field("sky_temple_keys",
                                        LayoutSkyTempleKeyMode(self.editor.skytemple_slider.value()))
            else:
                self.editor.skytemple_slider.setEnabled(False)
                editor.set_layout_field("sky_temple_keys", combo_enum)

    def _on_sky_temple_key_combo_slider_changed(self):
        self.editor.skytemple_slider_label.setText(str(self.editor.skytemple_slider.value()))
        self._on_sky_temple_key_combo_changed()
