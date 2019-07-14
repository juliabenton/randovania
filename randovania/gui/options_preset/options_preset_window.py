from typing import List, Tuple

from PySide2 import QtWidgets
from PySide2.QtWidgets import QMainWindow, QWidget

from randovania.gui.common_qt_lib import set_default_window_icon
from randovania.gui.main_window import MainWindow
from randovania.gui.options_preset.elevator_tab import ElevatorTab
from randovania.gui.options_preset.game_patches_tab import GamePatchesTab
from randovania.gui.options_preset.goal_tab import GoalTab
from randovania.gui.options_preset.hint_tab import HintTab
from randovania.gui.options_preset.item_pool_tab import ItemPoolTab
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.gui.options_preset.starting_location_tab import StartingLocationTab
from randovania.gui.options_preset.translator_gate_tab import TranslatorGateTab
from randovania.gui.options_preset.trick_level_tab import TrickLevelTab
from randovania.interface_common.options_preset import OptionsPreset


class OptionsPresetWindow(QMainWindow, OptionsPresetEditor):
    tabs: List[OptionsPresetBaseTab]
    _original_preset: OptionsPreset

    def __init__(self, main_window: MainWindow):
        super().__init__()
        OptionsPresetEditor.__init__(self)

        set_default_window_icon(self)
        self.setupUi(self)

        self._original_preset = None

        self.tabs = [
            ItemPoolTab(self),
            TrickLevelTab(self, main_window),
            ElevatorTab(self),
            GoalTab(self),
            StartingLocationTab(self),
            TranslatorGateTab(self),
            HintTab(self),
            GamePatchesTab(self),
        ]

        self.button_box.clicked.connect(self.button_box_clicked)
        the_buttons: Tuple[QtWidgets.QAbstractButton, ...] = self.button_box.buttons()
        self.save_button, self.close_button, self.reset_button = the_buttons

        self.on_changes = self.on_preset_changed

    @property
    def parent(self) -> QWidget:
        raise self

    def on_preset_changed(self):
        if self._original_preset is None:
            self._original_preset = self.options_preset

        for tab in self.tabs:
            tab.on_preset_changed(self.options_preset)

        self.reset_button.setEnabled(self.has_unsaved_changes)
        self.save_button.setEnabled(self.has_unsaved_changes)

        self.preset_title_edit.setText(self.options_preset.name)
        self.preset_description_edit.setText(self.options_preset.description)
        self.preset_reference_value_label.setText(self.options_preset.reference.name
                                                  if self.options_preset.reference is not None
                                                  else "<Default Preset>")

    def button_box_clicked(self, button: QtWidgets.QAbstractButton):
        if button == self.close_button:
            self.close()

        elif button == self.save_button:
            self.save_modifications()

        elif button == self.reset_button:
            with self as editor:
                editor.change_preset(self._original_preset)

    @property
    def has_unsaved_changes(self) -> bool:
        return self.options_preset != self._original_preset

    def closeEvent(self, event):
        if self.has_unsaved_changes:
            response = QtWidgets.QMessageBox.question(self,
                                                      "Discard changes?",
                                                      "You have unsaved changes. Do you want to close anyway?")
            if response != QtWidgets.QMessageBox.Yes:
                event.ignore()
                return

        super().closeEvent(event)

    def save_modifications(self):
        if self.options_preset.reference is None:
            raise RuntimeError("Attempting to save a default options preset.")