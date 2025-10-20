"""
Control Frame Types
There are three control field types in AX.25, which correspond to the three AX.25 frame
types. These are the Info, Supervisory, and Unnumbered frame types.

Semantics change significantly based on which control type is in use. Therefore, we have
multiple dataclasses for the purpose of handling these different control field types,
as well as helper functions for identifying them.

Supervisory and Informational frames come in two flavors, modulo 8 and modulo 128.
Modulo 128 uses two-byte control fields and allows for a larger sequence frame count.

For the moment, we only support modulo 8, which means we assume all control fields to be
one byte long and consider anything else to be an error. In the future, modulo 128 may
be supported.
"""

from typing import Literal, NamedTuple, Self, cast

from pax25.ax25.constants import (
    AX25_CTRL_I,
    AX25_CTRL_INVMASK_PF,
    AX25_CTRL_MASK_I,
    AX25_CTRL_MASK_PF,
    AX25_CTRL_MASK_RECVSEQ,
    AX25_CTRL_MASK_S,
    AX25_CTRL_MASK_SENDSEQ,
    AX25_CTRL_MASK_UI,
    AX25_CTRL_S,
    AX25_CTRL_SHIFT_PF,
    AX25_CTRL_SHIFT_RECVSEQ,
    AX25_CTRL_SHIFT_SENDSEQ,
    AX25_CTRL_UI,
    AX25_ENDIAN,
    AX25_SUPERVISOR_MASK_SUBTYPE,
    S_FRAME_MAP,
    SFRAME_DISPLAY,
    U_FRAME_MAP,
    UCOMMAND_DISPLAY,
    FrameType,
    SFrameType,
    UFrameType,
)
from pax25.ax25.exceptions import DisassemblyError
from pax25.protocols import JSONObj


class Unnumbered(NamedTuple):
    """
    Unnumbered control header flags.
    """

    frame_type: UFrameType
    poll_or_final: bool = False

    @property
    def type(self) -> Literal[FrameType.UNNUMBERED]:
        """
        Returns the frame's type.
        """
        return FrameType.UNNUMBERED

    def size(self) -> int:
        """
        Unnumbered control is one byte, always.
        """
        return 1

    def __str__(self) -> str:
        """
        String representation of an unnumbered control field.
        """
        return f"<{UCOMMAND_DISPLAY[self.frame_type]}>"

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Disassembles a control byte for an unnumbered frame.
        """
        byte = data[0]
        if (byte & AX25_CTRL_UI) != AX25_CTRL_UI:
            raise DisassemblyError(
                f"Attempted to disassemble a control byte as an "
                f"unnumbered control byte, but it was something else. "
                f"Byte was {byte!r}."
            )

        frame_type = U_FRAME_MAP[byte & AX25_CTRL_INVMASK_PF]
        poll_final = bool(byte & AX25_CTRL_MASK_PF)
        return cls(frame_type=frame_type, poll_or_final=poll_final)

    def assemble(self) -> bytes:
        """
        Assembles a control byte for an unnumbered frame.
        """
        data = int(self.poll_or_final)
        data <<= AX25_CTRL_SHIFT_PF
        data |= self.frame_type.value
        return data.to_bytes(1, AX25_ENDIAN)

    @classmethod
    def from_json(cls, obj: JSONObj) -> Self:
        kwargs = {
            "frame_type": getattr(UFrameType, cast(str, obj["frame_type"]).strip("_")),
            "poll_or_final": cast(bool, obj["poll_or_final"]),
        }
        return cls(**kwargs)

    def to_json(self) -> JSONObj:
        return {
            "__class__": self.__class__.__name__,
            "frame_type": self.frame_type.name,
            "poll_or_final": self.poll_or_final,
        }


class Supervisory(NamedTuple):
    """
    Supervisor control header flags.
    """

    frame_type: SFrameType
    receiving_sequence_number: int = 0
    poll_or_final: bool = False

    @property
    def type(self) -> Literal[FrameType.SUPERVISORY]:
        """
        Returns the frame's type.

        Note: In addition to identifying the frame as a supervisory frame, supervisory
        frames have their own subtypes. The subtype is stored on the frame_type
        property.
        """
        return FrameType.SUPERVISORY

    def __str__(self) -> str:
        """
        String representation of a supervisory control field.
        """
        return f"<{SFRAME_DISPLAY[self.frame_type]}>"

    def size(self) -> int:
        """
        Supervisory control is one byte, always.
        """
        return 1

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Disassembles a control byte for a supervisory frame.
        """
        byte = data[0]
        if (byte & AX25_CTRL_MASK_S) != FrameType.SUPERVISORY.value:
            raise DisassemblyError(
                f"Attempted to disassemble a non-supervisory control byte as a "
                f"supervisory control byte. Byte was {byte!r}."
            )
        supervisory_frame_type = byte & AX25_SUPERVISOR_MASK_SUBTYPE
        poll_final = bool(byte & AX25_CTRL_MASK_PF)
        receive_sequence_number = byte & AX25_CTRL_MASK_RECVSEQ
        receive_sequence_number >>= AX25_CTRL_SHIFT_RECVSEQ
        return cls(
            receiving_sequence_number=receive_sequence_number,
            poll_or_final=poll_final,
            frame_type=S_FRAME_MAP[supervisory_frame_type],
        )

    def assemble(self) -> bytes:
        """
        Assembles a control byte for an info frame.
        """
        byte = 0
        byte |= self.receiving_sequence_number << AX25_CTRL_SHIFT_RECVSEQ
        byte |= self.poll_or_final << AX25_CTRL_SHIFT_PF
        byte |= self.frame_type.value
        return byte.to_bytes(1, AX25_ENDIAN)

    def to_json(self) -> JSONObj:
        return {
            "__class__": self.__class__.__name__,
            "frame_type": self.frame_type.name,
            "receiving_sequence_number": self.receiving_sequence_number,
            "poll_or_final": self.poll_or_final,
        }

    @classmethod
    def from_json(cls, obj: JSONObj) -> Self:
        kwargs = {
            "frame_type": getattr(SFrameType, cast(str, obj["frame_type"]).strip("_")),
            "receiving_sequence_number": cast(int, obj["receiving_sequence_number"]),
            "poll_or_final": cast(bool, obj["poll_or_final"]),
        }
        return cls(**kwargs)


class Info(NamedTuple):
    """
    Info control header flags.
    """

    sending_sequence_number: int = 0
    receiving_sequence_number: int = 0
    poll_or_final: bool = False

    @property
    def type(self) -> Literal[FrameType.INFORMATIONAL]:
        """
        Returns the bit value of the info frame type identifier.
        """
        return FrameType.INFORMATIONAL

    def __str__(self) -> str:
        """
        String representation of an info control field.
        """
        return "<I>"

    def size(self) -> int:
        """
        Info control is one byte, always.
        """
        return 1

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Disassembles a control byte for an info frame.
        """
        byte = data[0]
        if (byte & AX25_CTRL_MASK_I) != FrameType.INFORMATIONAL.value:
            raise DisassemblyError(
                f"Attempted to disassemble a non-info control byte as a control byte. "
                f"Byte was {byte!r}."
            )
        receiving_sequence_number = (
            byte & AX25_CTRL_MASK_RECVSEQ
        ) >> AX25_CTRL_SHIFT_RECVSEQ
        sending_sequence_number = (
            byte & AX25_CTRL_MASK_SENDSEQ
        ) >> AX25_CTRL_SHIFT_SENDSEQ
        poll_final = bool(byte & AX25_CTRL_MASK_PF)
        return cls(
            receiving_sequence_number=receiving_sequence_number,
            sending_sequence_number=sending_sequence_number,
            poll_or_final=poll_final,
        )

    def assemble(self) -> bytes:
        """
        Assembles a control byte for an info frame.
        """
        data = 0
        data |= self.receiving_sequence_number << AX25_CTRL_SHIFT_RECVSEQ
        data |= self.sending_sequence_number << AX25_CTRL_SHIFT_SENDSEQ
        data |= self.poll_or_final << AX25_CTRL_SHIFT_PF
        return data.to_bytes(1, AX25_ENDIAN)

    def to_json(self) -> JSONObj:
        return {
            "__class__": "Info",
            "sending_sequence_number": self.sending_sequence_number,
            "receiving_sequence_number": self.receiving_sequence_number,
            "poll_or_final": self.poll_or_final,
        }

    @classmethod
    def from_json(cls, obj: JSONObj) -> Self:
        kwargs = {
            "sending_sequence_number": cast(int, obj["sending_sequence_number"]),
            "receiving_sequence_number": cast(int, obj["receiving_sequence_number"]),
            "poll_or_final": cast(bool, obj["poll_or_final"]),
        }
        return cls(**kwargs)  # type: ignore[arg-type]


def derive_control_class(
    data: bytes,
) -> type[Info] | type[Unnumbered] | type[Supervisory]:
    """
    Derives the appropriate control class for a given control byte.
    """
    byte = data[0]
    if (byte & AX25_CTRL_MASK_I) == AX25_CTRL_I:
        return Info
    if (byte & AX25_CTRL_MASK_UI) == AX25_CTRL_UI:
        return Unnumbered
    if (byte & AX25_CTRL_MASK_S) == AX25_CTRL_S:
        return Supervisory
    # Pretty sure it's actually impossible to hit this point, since we're using two bits
    # and all options are accounted for.
    raise DisassemblyError(  # pragma: no cover
        f"Could not identify the correct control field type! Byte was {byte!r}"
    )


control_class_dict: dict[str, type[Unnumbered] | type[Info] | type[Supervisory]] = {
    "Unnumbered": Unnumbered,
    "Info": Info,
    "Supervisory": Supervisory,
}


def control_from_json(obj: JSONObj) -> Unnumbered | Info | Supervisory:
    """
    Given a dict representation of a control sequence, return the native control
    structure.
    """
    if obj["__class__"] not in ("Unnumbered", "Info", "Supervisory"):
        raise TypeError("Control class not recognized!")
    return control_class_dict[cast(str, obj["__class__"])].from_json(obj)
