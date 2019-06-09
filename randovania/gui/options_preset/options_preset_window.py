import random

from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QMainWindow, QMessageBox

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
from randovania.gui.options_preset.starting_location_tab import StartingLocationTab
from randovania.gui.options_preset.translator_gate_tab import TranslatorGateTab
from randovania.gui.options_preset.trick_level_tab import TrickLevelTab
from randovania.interface_common.options import Options
from randovania.layout.permalink import Permalink


class OptionsPresetWindow(QMainWindow, Ui_OptionsPresetWindow):
    tab_service: TabService
    _options: Options

    def __init__(self, main_window: MainWindow, options: Options):
        super().__init__()
        self.setupUi(self)

        self.tabs = []
        self.tabs.append(ItemPoolTab(self, self, options))
        self.tabs.append(TrickLevelTab(self, self, options, main_window))
        self.tabs.append(ElevatorTab(self, self, options))
        self.tabs.append(GoalTab(self, self, options))
        self.tabs.append(StartingLocationTab(self, self, options))
        self.tabs.append(TranslatorGateTab(self, self, options))
        self.tabs.append(HintTab(self, self, options))
        self.tabs.append(GamePatchesTab(self, self, options))

        self.on_options_changed(options)

    def on_options_changed(self, options: Options):
        for tab in self.tabs:
            tab.on_options_changed(options)
