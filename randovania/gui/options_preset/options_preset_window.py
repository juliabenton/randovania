import random
from typing import List

from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QMainWindow, QMessageBox, QWidget

from randovania.gui.common_qt_lib import set_default_window_icon
from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.gui.generated.permalink_window_ui import Ui_PermalinkWindow
from randovania.gui.lib.background_task_mixin import BackgroundTaskMixin
from randovania.gui.lib.tab_service import TabService
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
from randovania.interface_common.options import Options
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.permalink import Permalink


class OptionsPresetWindow(QMainWindow, OptionsPresetEditor):
    tabs: List[OptionsPresetBaseTab]

    def __init__(self, main_window: MainWindow):
        super().__init__()
        set_default_window_icon(self)
        self.setupUi(self)

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

        self.on_changes = self.on_preset_changed

    @property
    def parent(self) -> QWidget:
        raise self

    def on_preset_changed(self):
        for tab in self.tabs:
            tab.on_preset_changed(self.options_preset)
