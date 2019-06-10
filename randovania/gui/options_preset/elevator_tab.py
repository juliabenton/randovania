from PySide2 import QtCore

from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.layout_configuration import LayoutElevators


class ElevatorTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    def __init__(self, editor: OptionsPresetEditor):
        self.editor = editor

        # Update with Options
        self.setup_elevator_elements()

        # Alignment
        self.editor.elevator_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Elevator
        set_combo_with_value(self.editor.elevators_combo, preset.layout.elevators)

    # Elevator
    def setup_elevator_elements(self):
        self.editor.elevators_combo.setItemData(0, LayoutElevators.VANILLA)
        self.editor.elevators_combo.setItemData(1, LayoutElevators.RANDOMIZED)
        self.editor.elevators_combo.currentIndexChanged.connect(self._on_update_elevators)

    def _on_update_elevators(self, new_index: int):
        with self.editor as editor:
            editor.set_layout_field("elevators", self.editor.elevators_combo.currentData())
