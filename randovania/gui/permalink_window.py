import random

from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QMainWindow, QMessageBox

from randovania.gui.background_task_mixin import BackgroundTaskMixin
from randovania.gui.permalink_window_ui import Ui_PermalinkWindow
from randovania.gui.tab_service import TabService
from randovania.interface_common.options import Options
from randovania.layout.permalink import Permalink


class PermalinkWindow(QMainWindow, Ui_PermalinkWindow):
    tab_service: TabService
    _options: Options

    def __init__(self, tab_service: TabService, background_processor: BackgroundTaskMixin, options: Options):
        super().__init__()
        self.setupUi(self)

        self._options = options

        # Seed/Permalink
        self.seed_number_edit.setValidator(QIntValidator(0, 2 ** 31 - 1))
        self.seed_number_edit.textChanged.connect(self._on_new_seed_number)
        self.seed_number_button.clicked.connect(self._generate_new_seed_number)

        self.permalink_edit.textChanged.connect(self._on_permalink_changed)
        self.permalink_import_button.clicked.connect(self._import_permalink_from_field)
        self.create_spoiler_check.stateChanged.connect(self._persist_option_then_notify("create_spoiler"))

        self.reset_settings_button.clicked.connect(self._reset_settings)

    def _persist_option_then_notify(self, attribute_name: str):
        def persist(value: int):
            with self._options as options:
                setattr(options, attribute_name, bool(value))

        return persist

    def on_options_changed(self, options: Options):
        seed_number = options.seed_number
        if seed_number is not None:
            self.seed_number_edit.setText(str(seed_number))
        else:
            self.seed_number_edit.setText("")

        self.create_spoiler_check.setChecked(options.create_spoiler)

        permalink = options.permalink
        if permalink is not None:
            self.permalink_edit.setText(permalink.as_str)
        else:
            self.permalink_edit.setText("")

    # Seed Number / Permalink
    def _on_new_seed_number(self, value: str):
        try:
            seed = int(value)
        except ValueError:
            seed = None

        with self._options as options:
            options.seed_number = seed

    def _generate_new_seed_number(self):
        self.seed_number_edit.setText(str(random.randint(0, 2 ** 31)))

    def _get_permalink_from_field(self) -> Permalink:
        return Permalink.from_str(self.permalink_edit.text())

    def _on_permalink_changed(self, value: str):
        self.permalink_edit.setStyleSheet("")
        try:
            self._get_permalink_from_field()
            # Ignoring return value: we only want to know if it's valid
        except ValueError:
            self.permalink_edit.setStyleSheet("border: 1px solid red")

    def _import_permalink_from_field(self):
        try:
            permalink = self._get_permalink_from_field()
            with self._options as options:
                options.permalink = permalink

        except ValueError as e:
            QMessageBox.warning(self,
                                "Invalid permalink",
                                str(e))

    def _reset_settings(self):
        with self._options as options:
            options.reset_to_defaults()
