import dataclasses
from typing import Optional

from randovania.layout.layout_configuration import LayoutConfiguration
from randovania.layout.patcher_configuration import PatcherConfiguration


@dataclasses.dataclass(frozen=True)
class OptionsPreset:
    name: str
    description: str
    reference: Optional["OptionsPreset"]

    patcher: PatcherConfiguration
    layout: LayoutConfiguration

    @property
    def as_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "reference": self.reference.name if self.reference is not None else None,
            "patcher": self.patcher.as_json,
            "layout": self.layout.as_json,
        }
