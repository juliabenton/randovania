from randovania.interface_common.options_preset import OptionsPreset


class OptionsPresetBaseTab:

    def on_preset_changed(self, preset: OptionsPreset):
        raise NotImplementedError()
