import functools

from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox, QWidget

from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.interface_common.options import Options
from randovania.layout.layout_configuration import LayoutElevators


def _update_options_by_value(options: Options, combo: QComboBox, new_index: int):
    with options:
        setattr(options, combo.options_field_name, combo.currentData())


class ElevatorTab:
    parent: QWidget
    presets_window: Ui_OptionsPresetWindow
    _options: Options

    def __init__(self, parent: QWidget, presets_window: Ui_OptionsPresetWindow, options: Options):
        self.parent = parent
        self.presets_window = presets_window
        self._options = options

        # Update with Options
        self.setup_elevator_elements()

        # Alignment
        self.presets_window.elevator_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_options_changed(self, options: Options):
        # Elevator
        set_combo_with_value(self.presets_window.elevators_combo, options.layout_configuration_elevators)

    # Elevator
    def setup_elevator_elements(self):
        self.presets_window.elevators_combo.setItemData(0, LayoutElevators.VANILLA)
        self.presets_window.elevators_combo.setItemData(1, LayoutElevators.RANDOMIZED)

        self.presets_window.elevators_combo.options_field_name = "layout_configuration_elevators"
        self.presets_window.elevators_combo.currentIndexChanged.connect(
            functools.partial(_update_options_by_value,
                              self._options,
                              self.presets_window.elevators_combo))
