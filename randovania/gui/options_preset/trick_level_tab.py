import dataclasses
import functools
from typing import Dict

from PySide2 import QtCore, QtWidgets

from randovania.game_description import default_database
from randovania.game_description.resources.resource_type import ResourceType
from randovania.game_description.resources.simple_resource_info import SimpleResourceInfo
from randovania.game_description.world_list import WorldList
from randovania.gui.common_qt_lib import set_combo_with_value
from randovania.gui.options_preset.options_preset_base_tab import OptionsPresetBaseTab
from randovania.gui.options_preset.options_preset_editor import OptionsPresetEditor
from randovania.gui.trick_details_popup import TrickDetailsPopup
from randovania.interface_common.options_preset import OptionsPreset
from randovania.layout.trick_level import LayoutTrickLevel, TrickLevelConfiguration

_TRICK_LEVEL_DESCRIPTION = {
    LayoutTrickLevel.NO_TRICKS: [
        "This mode requires no knowledge about the game, nor does it require any abuse "
        "of game mechanics, making it ideal for casual and first time players."
    ],
    LayoutTrickLevel.TRIVIAL: [
        "This mode includes strategies that abuses oversights in the game, such as being able to activate the "
        "Hive Dynamo Works portal from the other side of the chasm and bomb jumping in Temple Assembly Site."
    ],
    LayoutTrickLevel.EASY: ["This mode assumes you can do simple tricks."],
    LayoutTrickLevel.NORMAL: ["This mode expands on the Easy mode, including more difficult to execute tricks."],
    LayoutTrickLevel.HARD: ["This mode expands on Normal with additional tricks, such as Grand Abyss scan dash."],
    LayoutTrickLevel.HYPERMODE: [
        "This mode considers every single trick and path known to Randovania as valid, "
        "such as Polluted Mire without Space Jump. No OOB is included."
    ],
    LayoutTrickLevel.MINIMAL_RESTRICTIONS: [
        "This mode only checks that Screw Attack, Dark Visor and Light Suit won't all be behind "
        "Ing Caches and Dark Water, removing the biggest reasons for a pure random layout to be impossible. "
        "There are no guarantees that a seed will be possible in this case."
    ],
}


def _difficulties_for_trick(world_list: WorldList, trick: SimpleResourceInfo):
    result = set()

    for area in world_list.all_areas:
        for _, _, requirements in area.all_connections:
            for individual in requirements.all_individual:
                if individual.resource == trick:
                    result.add(LayoutTrickLevel.from_number(individual.amount))

    return result


def _used_tricks(world_list: WorldList):
    result = set()

    for area in world_list.all_areas:
        for _, _, requirements in area.all_connections:
            for individual in requirements.all_individual:
                if individual.resource.resource_type == ResourceType.TRICK:
                    result.add(individual.resource)

    return result


def _get_trick_level_description(trick_level: LayoutTrickLevel) -> str:
    return "<html><head/><body>{}</body></html>".format(
        "".join(
            '<p align="justify">{}</p>'.format(item)
            for item in _TRICK_LEVEL_DESCRIPTION[trick_level]
        )
    )


class TrickLevelTab(OptionsPresetBaseTab):
    editor: OptionsPresetEditor

    _checkbox_for_trick: Dict[SimpleResourceInfo, QtWidgets.QCheckBox]
    _slider_for_trick: Dict[SimpleResourceInfo, QtWidgets.QSlider]
    world_list: WorldList
    trick_difficulties_layout: QtWidgets.QGridLayout

    def __init__(self, editor: OptionsPresetEditor, main_window):
        self.editor = editor

        self._main_window = main_window

        self.game_description = default_database.default_prime2_game_description()
        self.world_list = self.game_description.world_list
        self.resource_database = self.game_description.resource_database

        # Update with Options
        self.setup_trick_level_elements()

        # Alignment
        self.editor.trick_level_layout.setAlignment(QtCore.Qt.AlignTop)

    # Options
    def on_preset_changed(self, preset: OptionsPreset):
        # Trick Level
        trick_level_configuration = preset.layout.trick_level_configuration
        trick_level = trick_level_configuration.global_level

        set_combo_with_value(self.editor.logic_combo_box, trick_level)
        self.editor.logic_level_label.setText(_get_trick_level_description(trick_level))

        for (trick, checkbox), slider in zip(self._checkbox_for_trick.items(), self._slider_for_trick.values()):
            assert self._slider_for_trick[trick] is slider

            has_specific_level = trick_level_configuration.has_specific_level_for_trick(trick)

            checkbox.setEnabled(trick_level != LayoutTrickLevel.MINIMAL_RESTRICTIONS)
            slider.setEnabled(has_specific_level)
            slider.setValue(trick_level_configuration.level_for_trick(trick).as_number)
            checkbox.setChecked(has_specific_level)

    # Trick Level
    def _create_difficulty_details_row(self):
        row = 1

        trick_label = QtWidgets.QLabel(self.editor.trick_level_scroll_contents)
        trick_label.setWordWrap(True)
        trick_label.setFixedWidth(80)
        trick_label.setText("Difficulty Details")

        self.trick_difficulties_layout.addWidget(trick_label, row, 1, 1, 1)

        slider_layout = QtWidgets.QGridLayout()
        slider_layout.setHorizontalSpacing(0)
        for i in range(12):
            slider_layout.setColumnStretch(i, 1)

        for i, trick_level in enumerate(LayoutTrickLevel):
            if trick_level not in {LayoutTrickLevel.NO_TRICKS, LayoutTrickLevel.MINIMAL_RESTRICTIONS}:
                tool_button = QtWidgets.QToolButton(self.editor.trick_level_scroll_contents)
                tool_button.setText(trick_level.long_name)
                tool_button.clicked.connect(functools.partial(self._open_difficulty_details_popup, trick_level))

                slider_layout.addWidget(tool_button, 1, 2 * i, 1, 2)

        self.trick_difficulties_layout.addLayout(slider_layout, row, 2, 1, 1)

    def setup_trick_level_elements(self):
        # logic_combo_box
        for i, trick_level in enumerate(LayoutTrickLevel):
            self.editor.logic_combo_box.setItemData(i, trick_level)

        self.editor.logic_combo_box.currentIndexChanged.connect(self._on_trick_level_changed)

        self.trick_difficulties_layout = QtWidgets.QGridLayout()
        self._checkbox_for_trick = {}
        self._slider_for_trick = {}

        configurable_tricks = TrickLevelConfiguration.all_possible_tricks()
        used_tricks = _used_tricks(self.world_list)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)

        self._create_difficulty_details_row()

        row = 2
        for trick in sorted(self.resource_database.trick, key=lambda _trick: _trick.long_name):
            if trick.index not in configurable_tricks or trick not in used_tricks:
                continue

            if row > 1:
                self.trick_difficulties_layout.addItem(QtWidgets.QSpacerItem(20, 40,
                                                                             QtWidgets.QSizePolicy.Minimum,
                                                                             QtWidgets.QSizePolicy.Expanding))

            trick_configurable = QtWidgets.QCheckBox(self.editor.trick_level_scroll_contents)
            trick_configurable.setFixedWidth(16)
            trick_configurable.stateChanged.connect(functools.partial(self._on_check_trick_configurable, trick))
            self._checkbox_for_trick[trick] = trick_configurable
            self.trick_difficulties_layout.addWidget(trick_configurable, row, 0, 1, 1)

            trick_label = QtWidgets.QLabel(self.editor.trick_level_scroll_contents)
            trick_label.setSizePolicy(size_policy)
            trick_label.setWordWrap(True)
            trick_label.setFixedWidth(80)
            trick_label.setText(trick.long_name)

            self.trick_difficulties_layout.addWidget(trick_label, row, 1, 1, 1)

            slider_layout = QtWidgets.QGridLayout()
            slider_layout.setHorizontalSpacing(0)
            for i in range(12):
                slider_layout.setColumnStretch(i, 1)

            horizontal_slider = QtWidgets.QSlider(self.editor.trick_level_scroll_contents)
            horizontal_slider.setMaximum(5)
            horizontal_slider.setPageStep(2)
            horizontal_slider.setOrientation(QtCore.Qt.Horizontal)
            horizontal_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            horizontal_slider.setEnabled(False)
            horizontal_slider.valueChanged.connect(functools.partial(self._on_slide_trick_slider, trick))
            self._slider_for_trick[trick] = horizontal_slider
            slider_layout.addWidget(horizontal_slider, 0, 1, 1, 10)

            difficulties_for_trick = _difficulties_for_trick(self.world_list, trick)
            for i, trick_level in enumerate(LayoutTrickLevel):
                if trick_level == LayoutTrickLevel.NO_TRICKS or trick_level in difficulties_for_trick:
                    difficulty_label = QtWidgets.QLabel(self.editor.trick_level_scroll_contents)
                    difficulty_label.setAlignment(QtCore.Qt.AlignHCenter)
                    difficulty_label.setText(trick_level.long_name)

                    slider_layout.addWidget(difficulty_label, 1, 2 * i, 1, 2)

            self.trick_difficulties_layout.addLayout(slider_layout, row, 2, 1, 1)

            tool_button = QtWidgets.QToolButton(self.editor.trick_level_scroll_contents)
            tool_button.setText("?")
            tool_button.clicked.connect(functools.partial(self._open_trick_details_popup, trick))
            self.trick_difficulties_layout.addWidget(tool_button, row, 3, 1, 1)

            row += 1

        self.editor.trick_level_layout.addLayout(self.trick_difficulties_layout)

    def _on_check_trick_configurable(self, trick: SimpleResourceInfo, enabled: int):
        enabled = bool(enabled)

        with self.editor as editor:
            if editor.layout_configuration.trick_level_configuration.has_specific_level_for_trick(trick) != enabled:
                editor.set_layout_field(
                    "trick_level_configuration",
                    editor.layout_configuration.trick_level_configuration.set_level_for_trick(
                        trick,
                        self.editor.logic_combo_box.currentData() if enabled else None
                    )
                )

    def _on_slide_trick_slider(self, trick: SimpleResourceInfo, value: int):
        if self._slider_for_trick[trick].isEnabled():
            with self.editor as editor:
                editor.set_layout_field(
                    "trick_level_configuration",
                    editor.layout_configuration.trick_level_configuration.set_level_for_trick(
                        trick,
                        LayoutTrickLevel.from_number(value)
                    )
                )

    def _on_trick_level_changed(self):
        trick_level = self.editor.logic_combo_box.currentData()
        with self.editor as editor:
            editor.set_layout_field(
                "trick_level_configuration",
                dataclasses.replace(editor.layout_configuration.trick_level_configuration,
                                    global_level=trick_level)
            )

    def _open_trick_details_popup(self, trick: SimpleResourceInfo):
        self._trick_details_popup = TrickDetailsPopup(
            self._main_window,
            self.game_description,
            trick,
            self.editor.layout_configuration.trick_level_configuration.level_for_trick(trick),
        )
        self._trick_details_popup.show()

    def _open_difficulty_details_popup(self, difficulty: LayoutTrickLevel):
        self._trick_details_popup = TrickDetailsPopup(
            self._main_window,
            self.game_description,
            None,
            difficulty,
        )
        self._trick_details_popup.show()
