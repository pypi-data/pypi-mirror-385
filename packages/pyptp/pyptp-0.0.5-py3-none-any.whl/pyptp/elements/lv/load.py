"""Low-voltage load element for asymmetrical network modeling.

Provides detailed load modeling with phase-specific power consumption,
harmonic analysis capabilities, and profile-based load behavior
required for accurate unbalanced load flow analysis in LV networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
    NIL_GUID,
    Guid,
    config,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import HarmonicsType
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class LoadLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Low-voltage load element with comprehensive modeling capabilities.

    Supports asymmetrical load modeling with individual phase and
    phase-to-phase power specifications, harmonic content analysis,
    and time-varying load profiles for detailed LV network studies.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for LV loads.

        Encompasses all essential load characteristics including connection
        node, phase-specific power consumption, behavioral parameters,
        and harmonic generation specifications.
        """

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        pa: float = optional_field(0)
        qa: float = optional_field(0)
        pb: float = optional_field(0)
        qb: float = optional_field(0)
        pc: float = optional_field(0)
        qc: float = optional_field(0)
        pab: float = optional_field(0)
        qab: float = optional_field(0)
        pac: float = optional_field(0)
        qac: float = optional_field(0)
        pbc: float = optional_field(0)
        qbc: float = optional_field(0)
        behaviour_sort: str = string_field()
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        switch_on_frequency: float = optional_field(0)
        harmonics_type: str = string_field()

        def serialize(self) -> str:
            """Serialize load general properties to GNF format.

            Manually constructs property string with conditional inclusion
            of non-default values to minimize file size.

            Returns:
                Space-separated property string for GNF file section.

            """
            props = []
            if self.node != NIL_GUID:
                props.append(f"Node:'{{{str(self.node).upper()}}}'")
            props.append(f"GUID:'{{{str(self.guid).upper()}}}'")
            props.append(f"CreationTime:{self.creation_time}")
            if self.mutation_date != 0:
                props.append(f"MutationDate:{self.mutation_date}")
            if self.revision_date != 0.0:
                props.append(f"RevisionDate:{self.revision_date}")
            props.append(f"Name:'{self.name}'")
            props.append(f"s_L1:{self.s_L1!s}")
            props.append(f"s_L2:{self.s_L2!s}")
            props.append(f"s_L3:{self.s_L3!s}")
            props.append(f"s_N:{self.s_N!s}")
            props.append(f"FieldName:'{self.field_name}'")
            if self.pa != 0:
                props.append(f"Pa:{self.pa}")
            if self.qa != 0:
                props.append(f"Qa:{self.qa}")
            if self.pb != 0:
                props.append(f"Pb:{self.pb}")
            if self.qb != 0:
                props.append(f"Qb:{self.qb}")
            if self.pc != 0:
                props.append(f"Pc:{self.pc}")
            if self.qc != 0:
                props.append(f"Qc:{self.qc}")
            if self.pab != 0:
                props.append(f"Pab:{self.pab}")
            if self.qab != 0:
                props.append(f"Qab:{self.qab}")
            if self.pac != 0:
                props.append(f"Pac:{self.pac}")
            if self.qac != 0:
                props.append(f"Qac:{self.qac}")
            if self.pbc != 0:
                props.append(f"Pbc:{self.pbc}")
            if self.qbc != 0:
                props.append(f"Qbc:{self.qbc}")
            props.append(f"BehaviourSort:'{self.behaviour_sort}'")
            if self.profile != DEFAULT_PROFILE_GUID:
                props.append(f"Profile:'{{{str(self.profile).upper()}}}'")
            if self.switch_on_frequency != 0:
                props.append(f"SwitchOnFrequency:{self.switch_on_frequency}")
            props.append(f"HarmonicsType:'{self.harmonics_type}'")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> LoadLV.General:
            """Parse load general properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed load properties.

            """
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                s_L1=data.get("s_L1", True),
                s_L2=data.get("s_L2", True),
                s_L3=data.get("s_L3", True),
                s_N=data.get("s_N", True),
                field_name=data.get("FieldName", ""),
                pa=data.get("Pa", 0),
                qa=data.get("Qa", 0),
                pb=data.get("Pb", 0),
                qb=data.get("Qb", 0),
                pc=data.get("Pc", 0),
                qc=data.get("Qc", 0),
                pab=data.get("Pab", 0),
                qab=data.get("Qab", 0),
                pac=data.get("Pac", 0),
                qac=data.get("Qac", 0),
                pbc=data.get("Pbc", 0),
                qbc=data.get("Qbc", 0),
                behaviour_sort=data.get("BehaviourSort", ""),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                switch_on_frequency=data.get("SwitchOnFrequency", 0),
                harmonics_type=data.get("HarmonicsType", ""),
            )

    general: General
    presentations: list[ElementPresentation]
    harmonics: HarmonicsType | None = None

    def __post_init__(self) -> None:
        """Initialize mixins after dataclass instantiation.

        Ensures proper initialization of ExtrasNotesMixin and
        HasPresentationsMixin for consistent element behavior.
        """
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Register load in LV network with GUID-based indexing.

        Args:
            network: Target LV network for load registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.loads:
            logger.critical("Load %s already exists, overwriting", self.general.guid)
        network.loads[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete load to GNF format.

        Returns:
            Multi-line string with all load sections for GNF file output.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        if self.harmonics:
            lines.append(f"#HarmonicsType {self.harmonics.serialize()}")

        # Serialize extras and notes using safe accessors
        lines.extend(f"#Extra Text:{extra.text}" for extra in self.safe_extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.safe_notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LoadLV:
        """Create load instance from parsed GNF data.

        Args:
            data: Dictionary containing parsed GNF sections for load element.

        Returns:
            Fully initialized TLoadLS instance with all properties and
            sub-components properly deserialized.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        harmonics = None
        if data.get("harmonics"):
            from .shared import HarmonicsType

            harmonics = HarmonicsType.deserialize(data["harmonics"][0])

        return cls(
            general=general,
            presentations=presentations,
            harmonics=harmonics,
        )
