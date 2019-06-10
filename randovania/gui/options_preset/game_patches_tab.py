from PySide2.QtWidgets import QComboBox, QWidget, QCheckBox, QDoubleSpinBox

from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options import Options
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.patcher_configuration import PickupModelStyle, PickupModelDataSource


class GamePatchesTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor

        # Item Data
        for i, value in enumerate(PickupModelStyle):
            self.editor.pickup_model_combo.setItemData(i, value)

        for i, value in enumerate(PickupModelDataSource):
            self.editor.pickup_data_source_combo.setItemData(i, value)

        # TODO: implement the LOCATION data source
        self.editor.pickup_data_source_combo.removeItem(
            self.editor.pickup_data_source_combo.findData(PickupModelDataSource.LOCATION))

        # Signals
        self._persist_checkbox(self.editor.warp_to_start_check, "warp_to_start")
        self._persist_checkbox(self.editor.include_menu_mod_check, "menu_mod")
        self._persist_spin_box(self.editor.varia_suit_spin_box, "varia_suit_damage")
        self._persist_spin_box(self.editor.dark_suit_spin_box, "dark_suit_damage")
        self._persist_combo(self.editor.pickup_model_combo, "pickup_model_style")
        self._persist_combo(self.editor.pickup_data_source_combo, "pickup_model_data_source")

    def _persist_bool(self, attribute_name: str):
        def persist(value: int):
            with self.editor as editor:
                editor.set_patcher_field(attribute_name, bool(value))

        return persist

    def _persist_checkbox(self, check_box: QCheckBox, attribute_name: str):
        check_box.stateChanged.connect(self._persist_bool(attribute_name))

    def _persist_float(self, attribute_name: str):
        def persist(value: float):
            with self.editor as editor:
                editor.set_patcher_field(attribute_name, value)

        return persist

    def _persist_spin_box(self, spin_box: QDoubleSpinBox, attribute_name: str):
        spin_box.valueChanged.connect(self._persist_float(attribute_name))

    def _persist_combo(self, combo: QComboBox, attribute_name: str):
        def persist(index: int):
            with self.editor as editor:
                editor.set_patcher_field(attribute_name, combo.itemData(index))

        combo.currentIndexChanged.connect(persist)

    def on_preset_changed(self, preset: OptionsPreset):
        patcher = preset.patcher

        self.editor.warp_to_start_check.setChecked(patcher.warp_to_start)
        self.editor.include_menu_mod_check.setChecked(patcher.menu_mod)

        self.editor.varia_suit_spin_box.setValue(patcher.varia_suit_damage)
        self.editor.dark_suit_spin_box.setValue(patcher.dark_suit_damage)

        set_combo_with_value(self.editor.pickup_model_combo, patcher.pickup_model_style)
        set_combo_with_value(self.editor.pickup_data_source_combo, patcher.pickup_model_data_source)
        self.editor.pickup_data_source_combo.setEnabled(
            patcher.pickup_model_style != PickupModelStyle.ALL_VISIBLE)
