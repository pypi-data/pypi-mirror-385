"""Handler for parsing GNF SpecialTransformer sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class SpecialTransformerHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF SpecialTransformer components using a declarative recipe."""

    COMPONENT_CLS = SpecialTransformerLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#SpecialTransformerType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for SpecialTransformer-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.special_transformer import SpecialTransformerLV

            return SpecialTransformerLV.SpecialTransformerType
        return None
