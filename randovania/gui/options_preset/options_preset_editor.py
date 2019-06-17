import dataclasses

from PySide2.QtWidgets import QWidget

from randovania.gui.generated.options_preset_window_ui import Ui_OptionsPresetWindow
from randovania.interface_common.editable_object import EditableObject
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.layout_configuration import LayoutConfiguration
from randovania.layout.patcher_configuration import PatcherConfiguration


class OptionsPresetEditor(EditableObject, Ui_OptionsPresetWindow):
    _options_preset: OptionsPreset

    def __init__(self):
        self._options_preset = None

    @property
    def parent(self) -> QWidget:
        raise NotImplementedError()

    @property
    def options_preset(self) -> OptionsPreset:
        return self._options_preset

    def change_preset(self, preset: OptionsPreset):
        self.edit_field("options_preset", preset)

    def set_layout_field(self, field_name: str, value):
        self.change_preset(
            dataclasses.replace(
                self.options_preset,
                layout=dataclasses.replace(self.layout_configuration, **{field_name: value})
            ))

    def set_patcher_field(self, field_name: str, value):
        self.change_preset(
            dataclasses.replace(
                self.options_preset,
                patcher=dataclasses.replace(self.patcher, **{field_name: value})
            ))

    # Proxy

    @property
    def layout_configuration(self) -> LayoutConfiguration:
        return self.options_preset.layout

    @property
    def patcher(self) -> PatcherConfiguration:
        return self.options_preset.patcher
