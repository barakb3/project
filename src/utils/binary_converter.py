import struct
from typing import Optional, Union


def from_bytes(
        data: bytes,
        data_type: str,
        endianness: str,
        num_bytes: Optional[int] = None
) -> Union[int, float, str]:
    """
    Read binary data using `struct.unpack` for various data types.

    Args:
        data (bytes): The binary data to read from.
        data_type (str): The data type to interpret. Supported values:
        'uint64', 'uint32', 'float', 'double', 'char', 'string'.
        endianness (str): Use `<` for little-endian, '>' for big-endian or '='
        for the system's deafult endianness.
        num_bytes (Optional[int]): Number of bytes to read for the `string`
        type. Otherwise, reads the whole data as a string.

    Returns:
        Union[int, float, str]: The interpreted value.
    """
    type_code = {
        "uint64": "Q",
        "uint32": "I",
        "float": "f",
        "double": "d",
        "char": "c",
        "string": "{}s",
        "byte": "B",
    }

    if data_type not in type_code:
        raise ValueError(f"Unsupported data type: {data_type}.")

    code = type_code[data_type]

    if data_type == "char":
        unpacked_value = struct.unpack(
            f"{endianness}{code}", data[:1]
        )[0].decode("utf-8")
    elif data_type == "string":
        num_bytes = len(data) if num_bytes is None else num_bytes
        unpacked_value = struct.unpack(
            f"{endianness}{code}".format(num_bytes), data[:num_bytes]
        )[0].decode("utf-8")
    else:
        unpacked_value = struct.unpack(
            f"{endianness}{code}", data[:struct.calcsize(code)]
        )[0]

    return unpacked_value


def to_bytes(value: Union[int, float, str],
             data_type: str,
             endianness: str,
             num_bytes: Optional[int] = None) -> bytes:
    """
    Convert values to binary data using `struct.pack` for various data types.

    Args:
        value (Union[int, float, str]): The value to convert.
        data_type (str): The data type to interpret. Supported values:
        'uint64', 'uint32', 'float', 'double', 'char', 'string'.
        endianness (str): Use `<` for little-endian, '>' for big-endian or '='
        for the system's default endianness.
        num_bytes (Optional[int]): Number of bytes to write for the `string`
        type. Otherwise, writes the whole value as a string.

    Returns:
        bytes: The binary representation of the value.
    """
    type_code = {
        "uint64": "Q",
        "uint32": "I",
        "float": "f",
        "double": "d",
        "char": "c",
        "string": "{}s",
        "byte": "B",
    }

    if data_type not in type_code:
        raise ValueError(f"Unsupported data type: {data_type}.")

    code = type_code[data_type]

    if data_type == "char":
        packed_value = struct.pack(
            f"{endianness}{code}", value.encode("utf-8")
        )
    elif data_type == "string":
        value = value.encode("utf-8")
        num_bytes = len(value) if num_bytes is None else num_bytes
        packed_value = struct.pack(
            f"{endianness}{code}".format(num_bytes), value[:num_bytes]
        )
    else:
        packed_value = struct.pack(f"{endianness}{code}", value)

    return packed_value
