"""Utility helpers for dealing with ESX files."""
from typing import List
from . import esx_constants as C


def byte_array_to_list(b: bytes) -> List[int]:
    """Convert a bytes object to a list of integers."""
    return list(b)


def list_to_byte_array(lst: List[int]) -> bytes:
    """Convert a list of integers (0-255) to bytes."""
    return bytes(lst)


def pack_int(packed_int: int, input_value: int, num_bits: int, num_shifted_left: int) -> int:
    """Pack a small integer into a larger integer at a specific bit offset."""
    bits_unshifted = (1 << num_bits) - 1
    bits_shifted = bits_unshifted << num_shifted_left
    shifted_input_value = input_value << num_shifted_left
    packed_int &= ~bits_shifted
    packed_int |= shifted_input_value
    return packed_int


def is_valid_esx_file(data: bytes) -> bool:
    """Validate that the provided data appears to be an ESX file."""
    if len(data) < C.ADDR_VALID_ESX_CHECK_2 + 12:
        return False

    check_one = data[C.ADDR_VALID_ESX_CHECK_1 : C.ADDR_VALID_ESX_CHECK_1 + 12]
    if not (check_one.startswith(b"KORG") and check_one[7] == 0x71 and check_one[8:11] == b"ESX"):
        return False

    check_two = data[C.ADDR_VALID_ESX_CHECK_2 : C.ADDR_VALID_ESX_CHECK_2 + 12]
    if not (check_two.startswith(b"KORG") and check_two[7] == 0x71):
        return False

    return True
