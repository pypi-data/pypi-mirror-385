import json
import sys
from enum import (
    Enum,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
    final,
)

import pyunormalize

from .exceptions import (
    InvalidName,
)

# -- setup -- #
NFC: Final = pyunormalize.NFC
NFD: Final = pyunormalize.NFD


def _json_list_mapping_to_dict(
    f: Dict[str, Any],
    list_mapped_key: str,
) -> Dict[str, Any]:
    """
    Takes a `[key, [value]]` mapping from the original ENS spec json files and turns it
    into a `{key: value}` mapping.
    """
    f[list_mapped_key] = {k: v for k, v in f[list_mapped_key]}
    return f


# get the normalization spec json files downloaded from links in ENSIP-15
# https://docs.ens.domains/ens-improvement-proposals/ensip-15-normalization-standard
specs_dir_path = Path(sys.modules["faster_ens"].__file__).parent.joinpath("specs")
with specs_dir_path.joinpath("normalization_spec.json").open() as spec:
    f = json.load(spec)

    NORMALIZATION_SPEC: Final = _json_list_mapping_to_dict(f, "mapped")
    EMOJI_NORMALIZATION_SPEC: Final[List[List[int]]] = NORMALIZATION_SPEC["emoji"]
    NORMALIZATION_SPEC_CM: Final[List[int]] = NORMALIZATION_SPEC["cm"]
    NORMALIZATION_SPEC_FENCED: Final[List[List[int]]] = NORMALIZATION_SPEC["fenced"]
    NORMALIZATION_SPEC_GROUPS: Final[List[Dict[str, Any]]] = NORMALIZATION_SPEC["groups"]
    NORMALIZATION_SPEC_IGNORED: Final[List[int]] = NORMALIZATION_SPEC["ignored"]
    NORMALIZATION_SPEC_MAPPED: Final[Dict[int, List[int]]] = NORMALIZATION_SPEC["mapped"]
    NORMALIZATION_SPEC_NSM: Final[Set[int]] = set(NORMALIZATION_SPEC["nsm"])
    # clean `FE0F` (65039) from entries since it's optional
    for e in EMOJI_NORMALIZATION_SPEC:
        if 65039 in e:
            for _ in range(e.count(65039)):
                e.remove(65039)

with specs_dir_path.joinpath("nf.json").open() as nf:
    f = json.load(nf)
    NF = _json_list_mapping_to_dict(f, "decomp")


# --- Classes -- #


@final
class TokenType(Enum):
    EMOJI = "emoji"
    TEXT = "text"


class Token:
    type: ClassVar[Literal[TokenType.TEXT, TokenType.EMOJI]]
    _original_text: str
    _original_codepoints: List[int]
    _normalized_codepoints: Optional[List[int]]

    restricted: Final = False

    def __init__(self, codepoints: List[int]) -> None:
        self._original_codepoints: Final = codepoints
        self._original_text: Final = "".join(chr(cp) for cp in codepoints)
        self._normalized_codepoints = None

    @property
    def codepoints(self) -> List[int]:
        return self._normalized_codepoints or self._original_codepoints

    @property
    def text(self) -> str:
        return _codepoints_to_text(self.codepoints)


@final
class EmojiToken(Token):
    type: ClassVar = TokenType.EMOJI


@final
class TextToken(Token):
    type: ClassVar = TokenType.TEXT


@final
class Label:
    def __init__(self, type: str, tokens: List[Token]) -> None:
        self.type: Final = type
        self.tokens: Final = tokens

    @property
    def text(self) -> str:  # sourcery skip: assign-if-exp
        if not self.tokens:
            return ""

        return "".join(token.text for token in self.tokens)


@final
class ENSNormalizedName:
    labels: List[Label]

    def __init__(self, normalized_labels: List[Label]) -> None:
        self.labels: Final = normalized_labels

    @property
    def as_text(self) -> str:
        return ".".join(label.text for label in self.labels)


# -----

GROUP_COMBINED_VALID_CPS: Final[List[int]] = []

VALID_BY_GROUPS: Final[Dict[str, FrozenSet[int]]] = {}

for d in NORMALIZATION_SPEC_GROUPS:
    primary: List[int] = d["primary"]
    secondary: List[int] = d["secondary"]
    combined = primary + secondary
    GROUP_COMBINED_VALID_CPS.extend(combined)
    VALID_BY_GROUPS[d["name"]] = frozenset(combined)


def _extract_valid_codepoints() -> FrozenSet[int]:
    all_valid: Set[int] = set()
    for valid_cps in VALID_BY_GROUPS.values():
        all_valid.update(valid_cps)
    all_valid.update(map(ord, NFD("".join(map(chr, all_valid)))))
    return frozenset(all_valid)


def _construct_whole_confusable_map() -> Dict[int, FrozenSet[str]]:
    """
    Create a mapping, per confusable, that contains all the groups in the cp's whole
    confusable excluding the confusable extent of the cp itself - as per the spec at
    https://docs.ens.domains/ens-improvement-proposals/ensip-15-normalization-standard
    """
    whole_map: Dict[int, Set[str]] = {}
    
    whole: Dict[str, List[int]]
    for whole in NORMALIZATION_SPEC["wholes"]:
        whole_confusables = set(whole["valid"] + whole["confused"])
        confusable_extents: List[Tuple[Set[int], Set[str]]] = []

        for confusable_cp in whole_confusables:
            # create confusable extents for all whole confusables
            groups: Set[str] = set()
            for gn, gv in VALID_BY_GROUPS.items():
                if confusable_cp in gv:
                    groups.add(gn)

            if len(confusable_extents) == 0:
                confusable_extents.append(({confusable_cp}, groups))
            else:
                extent_exists = False
                for entry in confusable_extents:
                    if any(g in entry[1] for g in groups):
                        extent_exists = True
                        entry[0].update({confusable_cp})
                        entry[1].update(groups)
                        break

                if not extent_exists:
                    confusable_extents.append(({confusable_cp}, groups))

        for confusable_cp in whole_confusables:
            if confusable_cp in whole["confused"]:
                confusable_cp_extent_groups: Set[str] = set()
                this_group: Set[str] = set()

                for ce in confusable_extents:
                    if confusable_cp in ce[0]:
                        confusable_cp_extent_groups.update(ce[1])
                    else:
                        this_group.update(ce[1])

                # remove the groups from confusable_cp's confusable extent
                whole_map[confusable_cp] = this_group.difference(
                    confusable_cp_extent_groups
                )

    return {k: frozenset(whole_map[k]) for k in whole_map}


WHOLE_CONFUSABLE_MAP: Final = _construct_whole_confusable_map()
VALID_CODEPOINTS: Final = _extract_valid_codepoints()
MAX_LEN_EMOJI_PATTERN: Final = max(map(len, EMOJI_NORMALIZATION_SPEC))
NSM_MAX: Final[int] = NORMALIZATION_SPEC["nsm_max"]


def _is_fenced(cp: int, spec: List[List[int]]) -> bool:
    return any(cp == fenced[0] for fenced in spec)


def _codepoints_to_text(cps: Union[List[List[int]], List[int]]) -> str:
    if not cps:
        return ""
    elif isinstance(cps[0], int):
        return "".join(map(chr, cps))
    else:
        return "".join(map(_codepoints_to_text, cps))


def _validate_tokens_and_get_label_type(tokens: List[Token]) -> str:
    """
    Validate tokens and return the label type.

    :param List[Token] tokens: the tokens to validate
    :raises InvalidName: if any of the tokens are invalid
    """
    if all(token.type == TokenType.EMOJI for token in tokens):
        return "emoji"

    label_text = "".join(token.text for token in tokens)
    concat_text_tokens_as_str = "".join(
        t.text for t in tokens if t.type == TokenType.TEXT
    )
    all_token_cps = [cp for t in tokens for cp in t.codepoints]

    if len(tokens) == 1 and tokens[0].type == TokenType.TEXT:
        # if single text token
        encoded = concat_text_tokens_as_str.encode()
        try:
            encoded.decode("ascii")  # if label is ascii

            if "_" in concat_text_tokens_as_str[concat_text_tokens_as_str.count("_") :]:
                raise InvalidName(
                    "Underscores '_' may only occur at the start of a label: "
                    f"'{label_text}'"
                )
            elif concat_text_tokens_as_str[2:4] == "--":
                raise InvalidName(
                    "A label's third and fourth characters cannot be hyphens '-': "
                    f"'{label_text}'"
                )
            return "ascii"
        except UnicodeDecodeError:
            pass

    if 95 in all_token_cps[all_token_cps.count(95) :]:
        raise InvalidName(
            f"Underscores '_' may only occur at the start of a label: '{label_text}'"
        )

    norm_spec_fenced = NORMALIZATION_SPEC_FENCED
    if _is_fenced(all_token_cps[0], norm_spec_fenced) or _is_fenced(all_token_cps[-1], norm_spec_fenced):
        raise InvalidName(
            f"Label cannot start or end with a fenced codepoint: '{label_text}'"
        )

    for cp_index, cp in enumerate(all_token_cps):
        if cp_index == len(all_token_cps) - 1:
            break
        next_cp = all_token_cps[cp_index + 1]
        if _is_fenced(cp, norm_spec_fenced) and _is_fenced(next_cp, norm_spec_fenced):
            raise InvalidName(
                f"Label cannot contain two fenced codepoints in a row: '{label_text}'"
            )

    cm = NORMALIZATION_SPEC_CM
    if any(t.type == TokenType.TEXT and t.codepoints[0] in cm for t in tokens):
        raise InvalidName(
            "At least one text token in label starts with a "
            f"combining mark: '{label_text}'"
        )

    # find first group that contains all chars in label
    text_token_cps_set = {
        cp
        for token in tokens
        if token.type == TokenType.TEXT
        for cp in token.codepoints
    }

    chars_group_name = None
    for group_name, group_cps in VALID_BY_GROUPS.items():
        if text_token_cps_set.issubset(group_cps):
            chars_group_name = group_name
            break

    if not chars_group_name:
        raise InvalidName(
            f"Label contains codepoints from multiple groups: '{label_text}'"
        )

    # apply NFD and check contiguous NSM sequences
    NSM_SPEC = NORMALIZATION_SPEC_NSM
    for group in NORMALIZATION_SPEC_GROUPS:
        if group["name"] == chars_group_name:
            if "cm" not in group:
                nfd_cps = [
                    ord(nfd_c) for c in concat_text_tokens_as_str for nfd_c in NFD(c)
                ]

                next_index = -1
                for cp_i, cp in enumerate(nfd_cps):
                    if cp_i <= next_index:
                        continue

                    if cp in NSM_SPEC:
                        if cp_i == len(nfd_cps) - 1:
                            break

                        contiguous_nsm_cps = [cp]
                        next_index = cp_i + 1
                        next_cp = nfd_cps[next_index]
                        while next_cp in NSM_SPEC:
                            contiguous_nsm_cps.append(next_cp)
                            if len(contiguous_nsm_cps) > NSM_MAX:
                                raise InvalidName(
                                    "Contiguous NSM sequence for label greater than NSM"
                                    f" max of {NSM_MAX}: '{label_text}'"
                                )
                            next_index += 1
                            if next_index == len(nfd_cps):
                                break
                            next_cp = nfd_cps[next_index]

                        if not len(contiguous_nsm_cps) == len(set(contiguous_nsm_cps)):
                            raise InvalidName(
                                "Contiguous NSM sequence for label contains duplicate "
                                f"codepoints: '{label_text}'"
                            )
            break

    # check wholes
    # start with set of all groups with confusables
    retained_groups = set(VALID_BY_GROUPS.keys())
    confused_chars: Set[int] = set()
    buffer: Set[int] = set()

    for char_cp in text_token_cps_set:
        groups_excluding_ce = WHOLE_CONFUSABLE_MAP.get(char_cp)

        if groups_excluding_ce and len(groups_excluding_ce) > 0:
            if len(retained_groups) == 0:
                break
            else:
                retained_groups = retained_groups.intersection(groups_excluding_ce)
                confused_chars.add(char_cp)

        elif GROUP_COMBINED_VALID_CPS.count(char_cp) == 1:
            return chars_group_name

        else:
            buffer.add(char_cp)

    if len(confused_chars) > 0:
        for retained_group_name in retained_groups:
            valid = VALID_BY_GROUPS[retained_group_name]
            if all(cp in valid for cp in buffer):
                # Though the spec doesn't mention this explicitly, if the buffer is
                # empty, the label is confusable. This allows for using ``all()`` here
                # since that yields ``True`` on empty sets.
                # e.g. ``all(cp in group_cps for cp in set())`` is ``True``
                # for any ``group_cps``.
                if len(buffer) == 0:
                    msg = (
                        "All characters in label are confusable: "
                        f"'{label_text}' ({chars_group_name} / "
                    )
                    msg += (
                        f"{[rgn for rgn in retained_groups]})"
                        if len(retained_groups) > 1
                        else f"{retained_group_name})"
                    )
                else:
                    msg = (
                        f"Label is confusable: '{label_text}' "
                        f"({chars_group_name} / {retained_group_name})"
                    )
                raise InvalidName(msg)

    return chars_group_name


def _build_and_validate_label_from_tokens(tokens: List[Token]) -> Label:
    for token in tokens:
        if token.type == TokenType.TEXT:
            # apply NFC normalization to text tokens
            chars = [chr(cp) for cp in token._original_codepoints]
            nfc = NFC(chars)
            token._normalized_codepoints = [ord(c) for c in nfc]

    label_type = _validate_tokens_and_get_label_type(tokens)

    return Label(label_type, tokens)


def _buffer_codepoints_to_chars(buffer: Union[List[int], List[List[int]]]) -> str:
    return "".join(
        "".join(chr(c) for c in char) if isinstance(char, list) else chr(char)
        for char in buffer
    )


# -----


def normalize_name_ensip15(name: str) -> ENSNormalizedName:
    """
    Normalize an ENS name according to ENSIP-15
    https://docs.ens.domains/ens-improvement-proposals/ensip-15-normalization-standard

    :param str name: the dot-separated ENS name
    :raises InvalidName: if ``name`` has invalid syntax
    """
    if not name:
        return ENSNormalizedName([])
    elif isinstance(name, (bytes, bytearray)):
        name = name.decode("utf-8")

    raw_labels = name.split(".")

    if any(len(label) == 0 for label in raw_labels):
        raise InvalidName("Labels cannot be empty")

    normalized_labels = []

    # Read these C constants into locals only once
    emoji_spec = EMOJI_NORMALIZATION_SPEC
    ignored_spec = NORMALIZATION_SPEC_IGNORED
    mapped_spec = NORMALIZATION_SPEC_MAPPED
    valid_codepoints = VALID_CODEPOINTS
    emoji_max_len = MAX_LEN_EMOJI_PATTERN

    for label_str in raw_labels:
        # _input takes the label and breaks it into a list of unicode code points
        # e.g. "xyz👨🏻" -> [120, 121, 122, 128104, 127995]
        _input = [ord(c) for c in label_str]
        buffer: List[int] = []
        tokens: List[Token] = []

        while len(_input) > 0:
            emoji_codepoint = None
            end_index = 1
            while end_index <= len(_input):
                current_emoji_sequence = _input[:end_index]

                if len(current_emoji_sequence) > emoji_max_len:
                    # if we've reached the max length of all known emoji patterns
                    break

                # remove 0xFE0F (65039)
                elif 65039 in current_emoji_sequence:
                    current_emoji_sequence.remove(65039)
                    _input.remove(65039)
                    if len(_input) == 0:
                        raise InvalidName("Empty name after removing 65039 (0xFE0F)")
                    end_index -= 1  # reset end_index after removing 0xFE0F

                if current_emoji_sequence in emoji_spec:
                    emoji_codepoint = current_emoji_sequence
                end_index += 1

            if emoji_codepoint:
                if len(buffer) > 0:
                    # emit `Text` token with values in buffer
                    tokens.append(TextToken(buffer))
                    buffer = []  # clear the buffer

                # emit `Emoji` token with values in emoji_codepoint
                tokens.append(EmojiToken(emoji_codepoint))
                _input = _input[len(emoji_codepoint) :]

            else:
                leading_codepoint = _input.pop(0)

                if leading_codepoint in ignored_spec:
                    pass

                elif (
                    mapped := mapped_spec.get(leading_codepoint)
                ) is not None:
                    for cp in mapped:
                        buffer.append(cp)

                else:
                    if leading_codepoint in valid_codepoints:
                        buffer.append(leading_codepoint)
                    else:
                        raise InvalidName(
                            f"Invalid character: '{chr(leading_codepoint)}' | "
                            f"codepoint {leading_codepoint} ({hex(leading_codepoint)})"
                        )

            if len(buffer) > 0 and len(_input) == 0:
                tokens.append(TextToken(buffer))

        # create a `Label` instance from tokens
        # - Apply NFC to each `Text` token
        # - Run tokens through "Validation" section of ENSIP-15
        normalized_label = _build_and_validate_label_from_tokens(tokens)
        normalized_labels.append(normalized_label)

    # - join labels back together after normalization
    return ENSNormalizedName(normalized_labels)
