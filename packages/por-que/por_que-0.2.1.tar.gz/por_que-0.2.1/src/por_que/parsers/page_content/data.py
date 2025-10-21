from __future__ import annotations

import logging
import math
import struct

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING, Any

from por_que.enums import Compression, Encoding, Type
from por_que.exceptions import ParquetDataError
from por_que.file_metadata import SchemaLeaf
from por_que.parsers import physical_types
from por_que.parsers.logical_types import (
    convert_single_value,
)
from por_que.protocols import AsyncReadableSeekable, ReadableSeekable

if TYPE_CHECKING:
    from por_que.pages import DataPageV1, DataPageV2

from . import compressors
from .dictionary import DictType

logger = logging.getLogger(__name__)

type ValueTuple = tuple[Any | None, int, int]


@dataclass(slots=True, frozen=True)
class _ParseOutput:
    values_stream: ReadableSeekable
    definition_levels: list[int]
    repetition_levels: list[int]


class BaseDataPageParser[P: DataPageV1 | DataPageV2](ABC):
    """Parser for data page content."""

    def __init__(
        self,
        data_page: P,
        reader: AsyncReadableSeekable,
        physical_type: Type,
        compression_codec: Compression,
        schema_element: SchemaLeaf,
        dictionary_values: DictType | None = None,
    ) -> None:
        self.data_page = data_page
        self.reader = reader
        self.physical_type = physical_type
        self.compression_codec = compression_codec
        self.schema_element = schema_element
        self.dictionary_values = dictionary_values

    @abstractmethod
    async def _parse(self) -> _ParseOutput:
        raise NotImplementedError

    async def parse(
        self,
        apply_logical_types: bool = True,
        excluded_logical_columns: Sequence[str] | None = None,
    ) -> Iterator[ValueTuple]:
        """
        Parse data page content into Python objects. This is the public entry point.
        """
        self.reader.seek(self.data_page.start_offset + self.data_page.header_size)

        return self._read_and_reassemble_values(
            await self._parse(),
            apply_logical_types=apply_logical_types,
            excluded_logical_columns=excluded_logical_columns,
        )

    def _read_and_reassemble_values(
        self,
        parse_output: _ParseOutput,
        apply_logical_types: bool = True,
        excluded_logical_columns: Sequence[str] | None = None,
    ) -> Iterator[ValueTuple]:
        # Handle REQUIRED columns without definition levels
        # If no definition levels exist for a REQUIRED column, all values are non-null
        if (
            not parse_output.definition_levels
            and self.schema_element.repetition.name == 'REQUIRED'
        ):
            # For REQUIRED columns, schema's definition_level is 0
            # But when there are no nulls, we don't have definition levels in the data
            # So we treat all values as non-null
            num_non_null = self.data_page.num_values
        elif not parse_output.definition_levels:
            # This shouldn't happen for OPTIONAL/REPEATED columns
            num_non_null = self.data_page.num_values
        elif (
            parse_output.definition_levels
            and self.schema_element.repetition.name == 'REQUIRED'
        ):
            # REQUIRED column with nulls: has definition levels [0, 1]
            # level 1 = non-null, level 0 = null
            num_non_null = sum(
                1 for level in parse_output.definition_levels if level > 0
            )
        else:
            # OPTIONAL/REPEATED: check against schema's definition level
            num_non_null = sum(
                1
                for level in parse_output.definition_levels
                if level >= self.schema_element.definition_level
            )

        non_null_values: list = self._read_values(
            parse_output.values_stream,
            num_non_null,
        )

        return self._create_tuple_stream(
            non_null_values,
            parse_output.definition_levels,
            parse_output.repetition_levels,
            apply_logical_types,
            excluded_logical_columns,
        )

    def _create_tuple_stream(
        self,
        non_null_values: list,
        definition_levels: list[int],
        repetition_levels: list[int],
        apply_logical_types: bool,
        excluded_logical_columns: Sequence[str] | None,
    ) -> Iterator[ValueTuple]:
        """Yield (value, definition_level, repetition_level) tuples as a stream.

        This is used when reconstruct=False to provide raw data for testing the
        reconstruction algorithm. Logical type conversion is applied per-value.

        Yields:
            Tuples of (value, definition_level, repetition_level)
        """
        # Get logical type info once for all values
        apply_logical_types = apply_logical_types and not (
            excluded_logical_columns
            and self.schema_element.full_path in excluded_logical_columns
        )
        logical_type_info = self.schema_element.get_logical_type()

        # Helper to convert value if needed
        def convert_value(value):
            if apply_logical_types and value is not None:
                return convert_single_value(
                    value,
                    self.physical_type,
                    logical_type_info,
                )
            return value

        # If we have no definition levels, all values are non-null
        if not definition_levels:
            # Yield tuples with DL=0 and RL=0 for all values
            for value in non_null_values:
                yield (convert_value(value), 0, 0)
            return

        # Iterate through levels and yield tuples
        non_null_iter = iter(non_null_values)

        # Ensure we have repetition levels for each definition level
        # If not, fill with zeros
        if not repetition_levels:
            repetition_levels = [0] * len(definition_levels)

        for def_level, rep_level in zip(
            definition_levels,
            repetition_levels,
            strict=False,
        ):
            # Determine if this entry has a non-null value
            if self.schema_element.definition_level == 0:
                is_non_null = def_level > 0
            else:
                is_non_null = def_level >= self.schema_element.definition_level

            if is_non_null:
                try:
                    value = next(non_null_iter)
                    yield (convert_value(value), def_level, rep_level)
                except StopIteration:
                    raise ParquetDataError(
                        'Fewer non-null values than specified by definition levels.',
                    ) from None
            else:
                yield (None, def_level, rep_level)

    def _read_values(
        self,
        stream: ReadableSeekable,
        num_non_null: int,
    ) -> list[bool] | list[int] | list[float] | list[bytes]:
        """Selects the correct value decoder based on the encoding."""
        if num_non_null == 0:
            return []

        match self.data_page.encoding:
            case Encoding.PLAIN:
                return self._read_plain_values(
                    stream,
                    num_non_null,
                )
            case Encoding.PLAIN_DICTIONARY | Encoding.RLE_DICTIONARY:
                return self._read_dictionary_values(
                    stream,
                    num_non_null,
                )
            case Encoding.RLE:
                return self._read_rle_values(
                    stream,
                    num_non_null,
                )
            case Encoding.DELTA_BINARY_PACKED:
                return self._read_delta_binary_packed_values(
                    stream,
                    num_non_null,
                    self.physical_type,
                )
            case Encoding.DELTA_BYTE_ARRAY:
                return self._read_delta_byte_array_values(
                    stream,
                    num_non_null,
                )
            case Encoding.DELTA_LENGTH_BYTE_ARRAY:
                return self._read_delta_length_byte_array_values(
                    stream,
                    num_non_null,
                )
            case Encoding.BYTE_STREAM_SPLIT:
                return self._read_byte_stream_split_values(
                    stream,
                    num_non_null,
                )
            case _:
                raise ParquetDataError(
                    f'Encoding {self.data_page.encoding} not supported.',
                )

    def _decode_rle_with_length_prefix(
        self,
        stream: ReadableSeekable,
        bit_width: int,
        num_values: int,
    ) -> list[int]:
        length_bytes = stream.read(4)
        if len(length_bytes) != 4:
            raise ParquetDataError('Could not read 4-byte length prefix for RLE levels')
        data_length = struct.unpack('<I', length_bytes)[0]
        rle_data = stream.read(data_length)
        return self._decode_rle_levels(BytesIO(rle_data), bit_width, num_values)

    def _decode_rle_levels(
        self,
        stream: ReadableSeekable,
        bit_width: int,
        num_expected: int,
    ) -> list[int]:
        values: list[int] = []
        while len(values) < num_expected:
            header = self._read_varint(stream)
            if header is None:
                break

            if (header & 1) == 0:
                # RLE run
                count = header >> 1
                value_bytes_to_read = (bit_width + 7) // 8
                value_bytes = stream.read(value_bytes_to_read)
                if len(value_bytes) < value_bytes_to_read:
                    raise ParquetDataError('Unexpected EOF in RLE run')
                value = int.from_bytes(value_bytes, 'little')
                num_to_add = min(count, num_expected - len(values))
                values.extend([value] * num_to_add)
            else:
                # Bit-packed run
                num_groups = header >> 1
                count = num_groups * 8
                num_bytes_to_read = math.ceil(count * bit_width / 8)
                packed_bytes = stream.read(num_bytes_to_read)
                packed_values = self._read_bit_packed_integers(
                    BytesIO(packed_bytes),
                    count,
                    bit_width,
                )
                num_to_add = min(len(packed_values), num_expected - len(values))
                values.extend(packed_values[:num_to_add])

        return values

    def _read_varint(self, stream: ReadableSeekable) -> int | None:
        result, shift = 0, 0
        while True:
            byte_data = stream.read(1)
            if not byte_data:
                return None
            byte = byte_data[0]
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                return result
            shift += 7

    def _read_zigzag_varint(self, stream: ReadableSeekable) -> int | None:
        value = self._read_varint(stream)
        if value is None:
            return None
        return (value >> 1) ^ (-(value & 1))

    def _apply_integer_overflow(self, value: int, physical_type: Type) -> int:
        """Apply correct integer overflow behavior based on physical type."""
        import struct

        match physical_type:
            case Type.INT32:
                # Convert to 32-bit signed integer using struct
                return struct.unpack('<i', struct.pack('<I', value & 0xFFFFFFFF))[0]
            case Type.INT64:
                # Convert to 64-bit signed integer using struct
                return struct.unpack(
                    '<q',
                    struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF),
                )[0]
            case Type.INT96:
                # INT96 is typically unsigned, so no overflow handling needed
                return value & 0xFFFFFFFFFFFFFFFFFFFFFFFF
            case _:
                # For other types, return as-is
                return value

    def _read_bit_packed_integers(
        self,
        stream: ReadableSeekable,
        count: int,
        bit_width: int,
    ) -> list[int]:
        """
        A robust bit-stream reader that treats input as continuous bits.
        Uses a 64-bit buffer to handle cross-byte boundaries correctly.
        """
        if bit_width == 0:
            return [0] * count

        values: list[int] = []
        buffer = 0  # 64-bit buffer to hold bits
        bits_in_buffer = 0  # Number of valid bits in buffer
        mask = (1 << bit_width) - 1

        # Read values one at a time
        for _ in range(count):
            # Ensure we have enough bits in the buffer
            while bits_in_buffer < bit_width:
                byte_data = stream.read(1)
                if not byte_data:
                    # End of stream - check if we have partial bits
                    if bits_in_buffer >= bit_width:
                        break
                    # Not enough bits for another value
                    return values

                # Shift byte into buffer at the high end
                buffer |= byte_data[0] << bits_in_buffer
                bits_in_buffer += 8

            # Extract value from low-order bits
            value = buffer & mask
            values.append(value)

            # Consume the bits we just read
            buffer >>= bit_width
            bits_in_buffer -= bit_width

        return values

    # --- Per-Encoding Value Readers ---

    def _read_plain_values(
        self,
        stream: ReadableSeekable,
        num_values: int,
    ) -> list[bool] | list[int] | list[float] | list[bytes]:
        match self.physical_type:
            case Type.BOOLEAN:
                return physical_types.parse_boolean_values(stream, num_values)
            case Type.INT32:
                return physical_types.parse_int32_values(stream, num_values)
            case Type.INT64:
                return physical_types.parse_int64_values(stream, num_values)
            case Type.INT96:
                return physical_types.parse_int96_values(stream, num_values)
            case Type.FLOAT:
                return physical_types.parse_float_values(stream, num_values)
            case Type.DOUBLE:
                return physical_types.parse_double_values(stream, num_values)
            case Type.BYTE_ARRAY:
                return physical_types.parse_byte_array_values(stream, num_values)
            case Type.FIXED_LEN_BYTE_ARRAY:
                if (
                    not self.schema_element
                    or not hasattr(self.schema_element, 'type_length')
                    or self.schema_element.type_length is None
                ):
                    raise ParquetDataError(
                        'FIXED_LEN_BYTE_ARRAY requires type_length from schema element',
                    )
                return physical_types.parse_fixed_len_byte_array_values(
                    stream,
                    num_values,
                    self.schema_element.type_length,
                )
            case _:
                raise ParquetDataError(
                    f'Unsupported physical type: {self.physical_type}',
                )

    def _read_dictionary_values(
        self,
        stream: ReadableSeekable,
        num_values: int,
    ) -> DictType:
        if self.dictionary_values is None:
            raise ParquetDataError('Dictionary values required')
        bit_width_bytes = stream.read(1)
        if not bit_width_bytes:
            raise ParquetDataError('Could not read bit width for dictionary indices')
        bit_width = bit_width_bytes[0]
        indices = self._decode_rle_levels(
            stream,
            bit_width,
            num_values,
        )
        # Validate indices are within bounds
        dict_size = len(self.dictionary_values)
        for idx in indices:
            if idx >= dict_size:
                raise ParquetDataError(
                    f'Dictionary index {idx} out of bounds '
                    f'(dictionary size: {dict_size})',
                )
        return [self.dictionary_values[i] for i in indices]

    def _read_rle_values(
        self,
        stream: ReadableSeekable,
        num_values: int,
    ) -> list[bool] | list[int]:
        """Read RLE-encoded values.

        RLE encoding is primarily used for boolean values in Parquet.
        For boolean values, each bit represents a boolean value, with runs
        of repeated values encoded efficiently.
        """
        if self.physical_type == Type.BOOLEAN:
            # For boolean RLE, we use bit width of 1
            bit_width = 1
            # RLE data for booleans uses 4-byte length prefix
            return [
                bool(x)
                for x in self._decode_rle_with_length_prefix(
                    stream,
                    bit_width,
                    num_values,
                )
            ]

        # RLE can theoretically be used with other types, though rarely
        # Read bit width from first byte
        bit_width_bytes = stream.read(1)
        if not bit_width_bytes:
            raise ParquetDataError('Could not read bit width for RLE values')
        bit_width = bit_width_bytes[0]

        rle_values = self._decode_rle_levels(stream, bit_width, num_values)

        # Convert to appropriate type based on physical type
        match self.physical_type:
            case Type.INT32:
                return rle_values
            case Type.INT64:
                return rle_values
            case _:
                raise ParquetDataError(
                    'RLE encoding not supported for physical type: '
                    f'{self.physical_type}',
                )

    def _read_delta_binary_packed_values(  # noqa: C901
        self,
        stream: ReadableSeekable,
        num_values: int,
        physical_type: Type,
    ) -> list[int]:
        if num_values == 0:
            return []

        all_values: list[int] = []

        # Keep reading DBP blocks until we have enough values
        while len(all_values) < num_values:
            # Try to read the next block header
            block_size = self._read_varint(stream)
            num_mini_blocks = self._read_varint(stream)
            total_value_count = self._read_varint(stream)
            first_value = self._read_zigzag_varint(stream)

            if (
                block_size is None
                or num_mini_blocks is None
                or total_value_count is None
                or first_value is None
            ):
                # No more blocks to read
                break

            block_values = [first_value]
            if total_value_count == 1:
                all_values.extend(block_values)
                continue

            current_value = first_value
            values_read = 1

            if num_mini_blocks == 0:
                all_values.extend(block_values)
                continue

            values_per_mini_block = block_size // num_mini_blocks

            # Read blocks within this DBP block
            total_values_in_block = 0
            while (
                total_values_in_block < total_value_count
                and values_read < total_value_count
            ):
                min_delta = self._read_zigzag_varint(stream)
                if min_delta is None:
                    break

                bit_widths = stream.read(num_mini_blocks)
                if len(bit_widths) != num_mini_blocks:
                    # If we can't read all bit widths, stop processing this block
                    break

                for bit_width in bit_widths:
                    # Always read complete mini-blocks to advance stream correctly
                    if bit_width == 0:
                        # All zeros, no data to read
                        mini_block_values = [0] * values_per_mini_block
                    else:
                        mini_block_values = self._read_bit_packed_integers(
                            stream,
                            values_per_mini_block,
                            bit_width,
                        )

                    # Process values from this mini-block
                    for delta in mini_block_values:
                        if values_read >= total_value_count:
                            # We've read all values for this DBP block
                            break
                        current_value += delta + min_delta
                        # Handle integer overflow based on physical type
                        current_value = self._apply_integer_overflow(
                            current_value,
                            physical_type,
                        )
                        block_values.append(current_value)
                        values_read += 1

                    total_values_in_block += values_per_mini_block

                    # Break out if we've read all values for this DBP block
                    if values_read >= total_value_count:
                        break

            # Add values from this block to our collection
            all_values.extend(block_values)

        # Return exactly the number of values requested
        return all_values[:num_values]

    def _read_delta_byte_array_values(
        self,
        stream: ReadableSeekable,
        num_non_null_values: int,
    ) -> list[bytes]:
        # DELTA_BYTE_ARRAY format (from parquet-format spec):
        # 1. DELTA_BINARY_PACKED prefix lengths (for all values)
        # 2. DELTA_BINARY_PACKED suffix lengths (for all values)
        # 3. Concatenated suffix data

        # Read prefix lengths first (for ALL values, first should typically be 0)
        prefix_lengths = self._read_delta_binary_packed_values(
            stream,
            num_non_null_values,
            Type.INT32,  # Lengths are 32-bit integers
        )

        # Read suffix lengths (NOT total lengths!)
        suffix_lengths = self._read_delta_binary_packed_values(
            stream,
            num_non_null_values,
            Type.INT32,  # Lengths are 32-bit integers
        )

        non_null_values: list[bytes] = []
        previous_value = b''

        for i in range(num_non_null_values):
            suffix_length = suffix_lengths[i]
            prefix_length = prefix_lengths[i]

            # Validate lengths
            if suffix_length < 0:
                raise ParquetDataError(
                    f'Invalid negative suffix_length at index {i}: {suffix_length}',
                )

            if prefix_length < 0:
                raise ParquetDataError(
                    f'Invalid negative prefix_length at index {i}: {prefix_length}',
                )

            if prefix_length > len(previous_value):
                raise ParquetDataError(
                    f'Invalid prefix length at index {i}: '
                    f'prefix={prefix_length}, prev_len={len(previous_value)}',
                )

            # Read suffix bytes
            suffix = stream.read(suffix_length)
            if len(suffix) != suffix_length:
                raise ParquetDataError(f'EOF reading suffix of length {suffix_length}')

            # Reconstruct value: prefix from previous + new suffix
            if prefix_length > 0:
                prefix = previous_value[:prefix_length]
                current_value = prefix + suffix
            else:
                current_value = suffix

            non_null_values.append(current_value)
            previous_value = current_value

        return non_null_values

    def _read_delta_length_byte_array_values(
        self,
        stream: ReadableSeekable,
        num_non_null_values: int,
    ) -> list[bytes]:
        # DELTA_LENGTH_BYTE_ARRAY format (from parquet-format spec):
        # 1. DELTA_BINARY_PACKED lengths (for ALL values, including nulls)
        # 2. Concatenated data for non-null values only

        # Read lengths for ALL values (not just non-null)
        # This is different from other encodings where we only read non-null counts
        lengths = self._read_delta_binary_packed_values(
            stream,
            self.data_page.num_values,
            Type.INT32,  # Lengths are 32-bit integers
        )

        non_null_values: list[bytes] = []

        for i in range(num_non_null_values):
            length = lengths[i]

            # Validate length
            if length < 0:
                raise ParquetDataError(
                    f'Invalid negative length at index {i}: {length}',
                )

            # Read data bytes
            data = stream.read(length)
            if len(data) != length:
                raise ParquetDataError(f'EOF reading data of length {length}')

            non_null_values.append(data)

        return non_null_values

    def _read_byte_stream_split_values(  # noqa: C901
        self,
        stream: ReadableSeekable,
        num_values: int,
    ) -> list[bool] | list[int] | list[float] | list[bytes]:
        """Read Byte Stream Split encoded values.

        Byte Stream Split encoding is designed for floating point values.
        It splits each value into its component bytes and groups all bytes
        of the same position together, which often leads to better compression.

        For example, with FLOAT (4 bytes per value):
        - All byte 0s are grouped together
        - All byte 1s are grouped together
        - All byte 2s are grouped together
        - All byte 3s are grouped together
        """
        values: list = []
        match self.physical_type:
            case Type.FLOAT:
                bytes_per_value = 4
                total_bytes = bytes_per_value * num_values

                # Read all the data
                data = stream.read(total_bytes)
                if len(data) != total_bytes:
                    raise ParquetDataError(
                        f'Expected {total_bytes} bytes for {num_values} FLOAT values, '
                        f'got {len(data)} bytes',
                    )

                # Reconstruct values by interleaving bytes
                for i in range(num_values):
                    # Extract the 4 bytes for this float value from the split streams
                    byte_0 = data[i]
                    byte_1 = data[num_values + i]
                    byte_2 = data[2 * num_values + i]
                    byte_3 = data[3 * num_values + i]

                    # Reconstruct the 4-byte little-endian float
                    float_bytes = bytes([byte_0, byte_1, byte_2, byte_3])
                    value = struct.unpack('<f', float_bytes)[0]
                    values.append(value)
            case Type.DOUBLE:
                bytes_per_value = 8
                total_bytes = bytes_per_value * num_values

                # Read all the data
                data = stream.read(total_bytes)
                if len(data) != total_bytes:
                    raise ParquetDataError(
                        f'Expected {total_bytes} bytes for {num_values} DOUBLE values, '
                        f'got {len(data)} bytes',
                    )

                # Reconstruct values by interleaving bytes
                for i in range(num_values):
                    # Extract the 8 bytes for this double value from the split streams
                    float_bytes = bytes([data[j * num_values + i] for j in range(8)])

                    # Reconstruct the 8-byte little-endian double
                    value = struct.unpack('<d', float_bytes)[0]
                    values.append(value)
            case Type.INT32:
                bytes_per_value = 4
                total_bytes = bytes_per_value * num_values

                # Read all the data
                data = stream.read(total_bytes)
                if len(data) != total_bytes:
                    raise ParquetDataError(
                        f'Expected {total_bytes} bytes for {num_values} INT32 values, '
                        f'got {len(data)} bytes',
                    )

                # Reconstruct values by interleaving bytes
                for i in range(num_values):
                    # Extract the 4 bytes for this int32 value from the split streams
                    byte_0 = data[i]
                    byte_1 = data[num_values + i]
                    byte_2 = data[2 * num_values + i]
                    byte_3 = data[3 * num_values + i]

                    # Reconstruct the 4-byte little-endian signed integer
                    int_bytes = bytes([byte_0, byte_1, byte_2, byte_3])
                    value = struct.unpack('<i', int_bytes)[0]
                    values.append(value)
            case Type.INT64:
                bytes_per_value = 8
                total_bytes = bytes_per_value * num_values

                # Read all the data
                data = stream.read(total_bytes)
                if len(data) != total_bytes:
                    raise ParquetDataError(
                        f'Expected {total_bytes} bytes for {num_values} INT64 values, '
                        f'got {len(data)} bytes',
                    )

                # Reconstruct values by interleaving bytes
                for i in range(num_values):
                    # Extract the 8 bytes for this int64 value from the split streams
                    int_bytes = bytes([data[j * num_values + i] for j in range(8)])

                    # Reconstruct the 8-byte little-endian signed integer
                    value = struct.unpack('<q', int_bytes)[0]
                    values.append(value)
            case Type.FIXED_LEN_BYTE_ARRAY:
                # Get type_length from schema_element
                if (
                    not self.schema_element
                    or not hasattr(self.schema_element, 'type_length')
                    or self.schema_element.type_length is None
                ):
                    raise ParquetDataError(
                        'FIXED_LEN_BYTE_ARRAY requires type_length from schema element',
                    )

                bytes_per_value = self.schema_element.type_length
                total_bytes = bytes_per_value * num_values

                # Read all the data
                data = stream.read(total_bytes)
                if len(data) != total_bytes:
                    raise ParquetDataError(
                        f'Expected {total_bytes} bytes for {num_values} '
                        f'FIXED_LEN_BYTE_ARRAY({bytes_per_value}) values, '
                        f'got {len(data)} bytes',
                    )

                # Reconstruct values by interleaving bytes
                for i in range(num_values):
                    # Extract the N bytes for this value from the split streams
                    value_bytes = bytes(
                        [data[j * num_values + i] for j in range(bytes_per_value)],
                    )
                    values.append(value_bytes)
            case _:
                raise ParquetDataError(
                    'Byte Stream Split encoding not supported '
                    f'for physical type: {self.physical_type}',
                )

        return values


class DataPageV1Parser(BaseDataPageParser):
    async def _parse(self) -> _ParseOutput:
        repetition_levels: list[int] = []
        definition_levels: list[int] = []

        # DataPageV1: Everything is compressed together
        compressed_data = await self.reader.read(self.data_page.compressed_page_size)
        decompressed_data = compressors.decompress_data(
            compressed_data,
            self.compression_codec,
            self.data_page.uncompressed_page_size,
        )

        # Sanity check: decompressed data must match expected uncompressed size
        if len(decompressed_data) != self.data_page.uncompressed_page_size:
            raise ParquetDataError(
                f"Decompressed data size ({len(decompressed_data)}) doesn't match "
                f'expected uncompressed size ({self.data_page.uncompressed_page_size})',
            )

        stream = BytesIO(decompressed_data)

        # Read repetition levels if the schema indicates they exist
        if self.schema_element.repetition_level > 0:
            bit_width = (self.schema_element.repetition_level).bit_length()
            repetition_levels = self._decode_rle_with_length_prefix(
                stream,
                bit_width,
                self.data_page.num_values,
            )

        # Read definition levels if the schema indicates they exist
        # This handles REQUIRED fields inside OPTIONAL/REPEATED parents
        if self.schema_element.definition_level > 0:
            bit_width = (self.schema_element.definition_level).bit_length()
            definition_levels = self._decode_rle_with_length_prefix(
                stream,
                bit_width,
                self.data_page.num_values,
            )

        return _ParseOutput(
            stream,
            definition_levels,
            repetition_levels,
        )


class DataPageV2Parser(BaseDataPageParser):
    async def _parse(self) -> _ParseOutput:
        repetition_levels: list[int] = []
        definition_levels: list[int] = []

        # DataPageV2: Levels are uncompressed, only values are compressed
        # Read all data (levels + compressed values)
        all_data = await self.reader.read(self.data_page.compressed_page_size)
        stream = BytesIO(all_data)

        rep_level_bytes = b''
        if self.data_page.repetition_levels_byte_length > 0:
            rep_level_bytes = stream.read(
                self.data_page.repetition_levels_byte_length,
            )
            bit_width = (self.schema_element.repetition_level).bit_length()
            repetition_levels = self._decode_rle_levels(
                BytesIO(rep_level_bytes),
                bit_width,
                self.data_page.num_values,
            )

        def_level_bytes = b''
        if self.data_page.definition_levels_byte_length > 0:
            def_level_bytes = stream.read(
                self.data_page.definition_levels_byte_length,
            )
            bit_width = (self.schema_element.definition_level).bit_length()
            definition_levels = self._decode_rle_levels(
                BytesIO(def_level_bytes),
                bit_width,
                self.data_page.num_values,
            )

        # Now decompress the remaining values data
        compressed_values = stream.read()
        # DataPageV2 has is_compressed as the authoritative source
        # as to whether the page is compressed, except it is optional
        # so we simply fall back to the length check in decompress_data
        values_stream = BytesIO(
            compressors.decompress_data(
                compressed_values,
                self.compression_codec,
                (
                    self.data_page.uncompressed_page_size
                    - len(rep_level_bytes)
                    - len(def_level_bytes)
                ),
            ),
        )

        return _ParseOutput(
            values_stream,
            definition_levels,
            repetition_levels,
        )
