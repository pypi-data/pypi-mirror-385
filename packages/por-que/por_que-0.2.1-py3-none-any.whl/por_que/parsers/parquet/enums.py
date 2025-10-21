from enum import IntEnum

# see https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift


# Field IDs for Parquet Thrift structures
class SchemaElementFieldId(IntEnum):
    """Field IDs for SchemaElement struct in Parquet metadata."""

    TYPE = 1
    TYPE_LENGTH = 2
    REPETITION_TYPE = 3
    NAME = 4
    NUM_CHILDREN = 5
    CONVERTED_TYPE = 6
    SCALE = 7
    PRECISION = 8
    FIELD_ID = 9
    LOGICAL_TYPE = 10


class ColumnMetadataFieldId(IntEnum):
    """Field IDs for ColumnMetaData struct in Parquet metadata."""

    TYPE = 1
    ENCODINGS = 2
    PATH_IN_SCHEMA = 3
    CODEC = 4
    NUM_VALUES = 5
    TOTAL_UNCOMPRESSED_SIZE = 6
    TOTAL_COMPRESSED_SIZE = 7
    KEY_VALUE_METADATA = 8
    DATA_PAGE_OFFSET = 9
    INDEX_PAGE_OFFSET = 10
    DICTIONARY_PAGE_OFFSET = 11
    STATISTICS = 12
    ENCODING_STATS = 13
    BLOOM_FILTER_OFFSET = 14
    BLOOM_FILTER_LENGTH = 15
    SIZE_STATISTICS = 16
    GEOSPATIAL_STATISTICS = 17


class ColumnChunkFieldId(IntEnum):
    """Field IDs for ColumnChunk struct in Parquet metadata."""

    FILE_PATH = 1
    FILE_OFFSET = 2
    META_DATA = 3
    # Page Index fields (Parquet 2.5+)
    OFFSET_INDEX_OFFSET = 4
    OFFSET_INDEX_LENGTH = 5
    COLUMN_INDEX_OFFSET = 6
    COLUMN_INDEX_LENGTH = 7
    # Encryption fields
    CRYPTO_METADATA = 8
    ENCRYPTED_COLUMN_METADATA = 9


class RowGroupFieldId(IntEnum):
    """Field IDs for RowGroup struct in Parquet metadata."""

    COLUMNS = 1
    TOTAL_BYTE_SIZE = 2
    NUM_ROWS = 3
    SORTING_COLUMNS = 4
    FILE_OFFSET = 5
    TOTAL_COMPRESSED_SIZE = 6
    ORDINAL = 7


class FileMetadataFieldId(IntEnum):
    """Field IDs for FileMetaData struct in Parquet metadata."""

    VERSION = 1
    SCHEMA = 2
    NUM_ROWS = 3
    ROW_GROUPS = 4
    KEY_VALUE_METADATA = 5
    CREATED_BY = 6
    COLUMN_ORDERS = 7
    # Encryption fields
    ENCRYPTION_ALGORITHM = 8
    FOOTER_SIGNING_KEY_METADATA = 9


class KeyValueFieldId(IntEnum):
    """Field IDs for KeyValue struct in Parquet metadata."""

    KEY = 1
    VALUE = 2


class StatisticsFieldId(IntEnum):
    """Field IDs for Statistics struct in Parquet metadata."""

    MAX = 1
    MIN = 2
    NULL_COUNT = 3
    DISTINCT_COUNT = 4
    MAX_VALUE = 5
    MIN_VALUE = 6
    IS_MAX_VALUE_EXACT = 7
    IS_MIN_VALUE_EXACT = 8


class PageHeaderFieldId(IntEnum):
    """Field IDs for PageHeader struct."""

    TYPE = 1
    UNCOMPRESSED_PAGE_SIZE = 2
    COMPRESSED_PAGE_SIZE = 3
    CRC = 4
    DATA_PAGE_HEADER = 5
    INDEX_PAGE_HEADER = 6
    DICTIONARY_PAGE_HEADER = 7
    DATA_PAGE_HEADER_V2 = 8


class DataPageHeaderFieldId(IntEnum):
    """Field IDs for DataPageHeader struct."""

    NUM_VALUES = 1
    ENCODING = 2
    DEFINITION_LEVEL_ENCODING = 3
    REPETITION_LEVEL_ENCODING = 4
    STATISTICS = 5


class DataPageHeaderV2FieldId(IntEnum):
    """Field IDs for DataPageHeaderV2 struct."""

    NUM_VALUES = 1
    NUM_NULLS = 2
    NUM_ROWS = 3
    ENCODING = 4
    DEFINITION_LEVELS_BYTE_LENGTH = 5
    REPETITION_LEVELS_BYTE_LENGTH = 6
    IS_COMPRESSED = 7
    STATISTICS = 8


class DictionaryPageHeaderFieldId(IntEnum):
    """Field IDs for DictionaryPageHeader struct."""

    NUM_VALUES = 1
    ENCODING = 2
    IS_SORTED = 3


class IndexPageHeaderFieldId(IntEnum):
    """Field IDs for IndexPageHeader struct (currently empty with just TODO)."""

    # Currently empty in the Parquet Thrift specification
    pass


class PageLocationFieldId(IntEnum):
    """Field IDs for PageLocation struct."""

    OFFSET = 1
    COMPRESSED_PAGE_SIZE = 2
    FIRST_ROW_INDEX = 3


class OffsetIndexFieldId(IntEnum):
    """Field IDs for OffsetIndex struct."""

    PAGE_LOCATIONS = 1
    UNENCODED_BYTE_ARRAY_DATA_BYTES = 2


class ColumnIndexFieldId(IntEnum):
    """Field IDs for ColumnIndex struct."""

    NULL_PAGES = 1
    MIN_VALUES = 2
    MAX_VALUES = 3
    BOUNDARY_ORDER = 4
    NULL_COUNTS = 5
    REPETITION_LEVEL_HISTOGRAMS = 6
    DEFINITION_LEVEL_HISTOGRAMS = 7


class BoundingBoxFieldId(IntEnum):
    XMIN = 1
    XMAX = 2
    YMIN = 3
    YMAX = 4
    ZMIN = 5
    ZMAX = 6
    MMIN = 7
    MMAX = 8


class GeospatialStatisticsFieldId(IntEnum):
    BBOX = 1
    GEOSPATIAL_TYPES = 2


class SizeStatisticsFieldId(IntEnum):
    UNENCODED_BYTE_ARRAY_DATA_BYTES = 1
    REPETITION_LEVEL_HISTOGRAM = 2
    DEFINITION_LEVEL_HISTOGRAM = 3


class PageEncodingStatsFieldId(IntEnum):
    PAGE_TYPE = 1
    ENCODING = 2
    COUNT = 3


class SortingColumnFieldId(IntEnum):
    COLUMN_IDX = 1
    DESCENDING = 2
    NULLS_FIRST = 3
