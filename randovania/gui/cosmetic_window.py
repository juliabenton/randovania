import dataclasses

from PySide2.QtWidgets import QMainWindow

from randovania.gui.generated.cosmetic_window_ui import Ui_CosmeticWindow
from randovania.gui.lib.background_task_mixin import BackgroundTaskMixin
from randovania.gui.lib.tab_service import TabService
from randovania.gui.main_window_base_tab import MainWindowBaseTab


class CosmeticWindow(QMainWindow, Ui_CosmeticWindow, MainWindowBaseTab):
    def __init__(self, tab_service: TabService, background_processor: BackgroundTaskMixin):
        super().__init__()
        self.setupUi(self)

        # Signals
        self.remove_hud_popup_check.stateChanged.connect(self._persist_option_then_notify("disable_hud_popup"))
        self.faster_credits_check.stateChanged.connect(self._persist_option_then_notify("speed_up_credits"))
        self.open_map_check.stateChanged.connect(self._persist_option_then_notify("open_map"))
        self.pickup_markers_check.stateChanged.connect(self._persist_option_then_notify("pickup_markers"))

    def _persist_option_then_notify(self, attribute_name: str):
        def persist(value: int):
            with self.user_preferences as user_preferences:
                user_preferences.cosmetic_patches = dataclasses.replace(
                    user_preferences.cosmetic_patches, **{attribute_name: bool(value)}
                )

        return persist

    def on_user_preferences_changed(self):
        patches = self.user_preferences.cosmetic_patches
        self.remove_hud_popup_check.setChecked(patches.disable_hud_popup)
        self.faster_credits_check.setChecked(patches.speed_up_credits)
        self.open_map_check.setChecked(patches.open_map)
        self.pickup_markers_check.setChecked(patches.pickup_markers)
