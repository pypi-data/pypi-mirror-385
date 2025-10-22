#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#
import sys
import warnings
from jnius import autoclass
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import INDEX_OUT_OF_BOUNDS, VALID_INTERVAL, INVALID_OPTION
from pypgx._utils import conversion
from pypgx.api._pgx_context_manager import PgxContextManager
from pypgx.api._pgql_result_element import PgqlResultElement
from datetime import date, datetime, time
from typing import (
    Any, Collection, Dict, Iterator, List, Optional, Tuple, Union, TextIO, TYPE_CHECKING
)

if TYPE_CHECKING:
    # Don't import at runtime, to avoid circular imports.
    from pypgx.api._pgx_graph import PgxGraph
    from pypgx.api.frames import PgxFrame
    from pypgx.api._pgx_entity import PgxEdge, PgxVertex

ByteArrayOutputStream = autoclass("java.io.ByteArrayOutputStream")
PrintStream = autoclass("java.io.PrintStream")
ResultSetFormatter = autoclass("oracle.pgql.lang.ResultSetFormatter")
PythonClientResultSetUtil = autoclass("oracle.pgx.pypgx.internal.PythonClientResultSetUtil")

DEFAULT_PRINT_LIMIT = ResultSetFormatter.DEFAULT_PRINT_LIMIT


class PgqlResultSet(PgxContextManager):
    """Result set of a pattern matching query.

    Note: retrieving results from the server is not thread-safe.
    """

    _java_class = "oracle.pgx.api.PgqlResultSet"

    def __init__(self, graph: Optional["PgxGraph"], java_pgql_result_set) -> None:
        self._pgql_result_set = java_pgql_result_set
        self._result_set_util = PythonClientResultSetUtil(java_pgql_result_set)
        self.graph = graph
        self._cached_data: Dict[int, List] = {}
        self._cache_ceil = -1
        self._id_cols: Dict[int, str] = {}
        self._populate_id_cols()
        self.is_closed = False

    @property
    def id(self) -> str:
        """Get the id of this result set"""
        return self._pgql_result_set.getId()

    @property
    def num_results(self) -> int:
        """Get the number of results"""
        return self._pgql_result_set.getNumResults()

    @property
    def col_count(self) -> int:
        """Get the number of columns"""
        metadata = java_handler(self._pgql_result_set.getMetaData, [])
        return java_handler(metadata.getColumnCount, [])

    @property
    def columns(self) -> List[str]:
        """Get the column names"""
        metadata = java_handler(self._pgql_result_set.getMetaData, [])
        return [java_handler(metadata.getColumnName, [i + 1]) for i in range(self.col_count)]

    @property
    def pgql_result_elements(self) -> Dict:
        """Get the result elements of this result set"""
        return self._pgql_result_elements(return_type="str")

    def _pgql_result_elements(self, return_type="str") -> Dict:
        if return_type not in ("str", "result_element"):
            raise ValueError(INVALID_OPTION.format(
                var="return_type", opts=("str", "result_element")
            ))
        if return_type == "str":
            warnings.warn(
                """In a later version, `pgql_result_elements` """
                """will return `pypgx.api.PgqlResultElement` objects""",
                DeprecationWarning,
            )
        pgql_result_elements = {}
        result_elements = self._pgql_result_set.getPgqlResultElements()
        for idx in range(result_elements.size()):
            java_result_elem = java_handler(result_elements.get, [idx])
            if return_type == "str":
                col_name = java_result_elem.getVarName()
                pgql_result_elements[idx] = col_name
            else:
                pgql_result_elements[idx] = PgqlResultElement(java_result_elem)
        return pgql_result_elements

    def _populate_id_cols(self) -> None:
        result_elements = self._pgql_result_elements(return_type="result_element")
        for idx, result_element in result_elements.items():
            if result_element.element_type is not None:
                self._id_cols[idx] = result_element.element_type

    def _assert_not_closed(self) -> None:
        if self.is_closed:
            raise RuntimeError("result set closed")

    def get_row(self, row: int) -> Any:
        """Get row from result_set.
        This method may change result_set cursor.

        :param row: Row index
        """
        self._assert_not_closed()
        if row < 0 or row > self.num_results - 1:
            raise RuntimeError(INDEX_OUT_OF_BOUNDS.format(idx="row", max_idx=self.num_results - 1))

        if row in self._cached_data:
            return self._cached_data[row]
        else:
            tmp_row = self._result_set_util.toList(row, row + 1)[0]
            cached_row = list(tmp_row)

            for idx in self._id_cols.keys():
                cached_row[idx] = conversion.anything_to_python(tmp_row[idx], self.graph)

            if len(self.pgql_result_elements) == 1:
                cached_row = cached_row[0]
            self._cached_data[row] = cached_row

        return cached_row

    def _insert_slice_to_cache(self, typed_query_list, start, stop):
        """Insert whole slice of rows from result_list into cache."""
        for i in range(0, stop - start + 1):
            self._cached_data[i + start] = typed_query_list[i]

    def _convert_row_to_python(self, item):
        """Wrap anything_to_python to convert whole row,
        since lambdas are not allowed.

        :param item: row to convert
        """
        row = item
        for i in self._id_cols.keys():
            row[i] = conversion.anything_to_python(item[i], self.graph)
        return row

    def _convert_item_to_python(self, item):
        """Wrap anything_to_python to add argument,
        since lambdas are not allowed.

        :param item: Item to convert
        """
        return conversion.anything_to_python(item, self.graph)

    def get_slice(self, start: int, stop: int, step: int = 1) -> List[list]:
        """Get slice from result_set.
        This method may change result_set cursor.

        :param start: Start index
        :param stop: Stop index
        :param step: Step size
        """
        self._assert_not_closed()

        if start < 0 or stop > self.num_results - 1 or start > stop:
            raise RuntimeError(
                VALID_INTERVAL.format(start=start, stop=stop, max_idx=self.num_results)
            )

        # fill cache first if data is not available
        if stop >= self._cache_ceil:
            query_list = self._result_set_util.toList(self._cache_ceil + 1, stop + 1)
            typed_query_list = list(map(self._convert_row_to_python, query_list))
            self._insert_slice_to_cache(typed_query_list, self._cache_ceil + 1, stop)
            self._cache_ceil = stop

        # fill the slice
        typed_query_list = []
        for row in range(start, stop + 1, step):
            typed_query_list.append(self._cached_data[row])

        return typed_query_list

    def to_frame(self) -> "PgxFrame":
        """Copy the content of this result set into a new PgxFrames

        :return: a new PgxFrame containing the content of the result set
        """
        self._assert_not_closed()
        from pypgx.api.frames._pgx_frame import PgxFrame

        java_frame = java_handler(self._pgql_result_set.toFrame, [])
        return PgxFrame(java_frame)

    def to_pandas(self):
        """
        Convert to pandas DataFrame.
        This method may change result_set cursor.
        This method requires pandas.

        :return: PgqlResultSet as a Pandas Dataframe
        """
        self._assert_not_closed()

        try:
            import numpy as np
        except Exception:
            raise ImportError("Could not import numpy")

        try:
            import pandas as pd
        except Exception:
            raise ImportError("Could not import pandas")

        # Unpack all these byte arrays
        java_type_to_np_type = {
            'double': np.float64, 'long': np.int64,
            'float': np.float32, 'integer': np.int32,
            'boolean': bool
        }
        java_type_to_pd_type = {
            "double": "Float64", "long": "Int64",
            "float": "Float32", "integer": "Int32",
            "boolean": "boolean"
        }

        # Run the conversion method
        serialized_columns = self._result_set_util.serialize()

        # Fetch the columns and their names (byte columns will also be unpacked into numpy)
        columns_with_names = dict()
        column_names_to_pandas_types = dict()
        for column in serialized_columns:
            column_name = column.getName()
            if not column.isBytes():
                columns_with_names[column_name] = column.getAsObjects()
            else:
                column_java_type = column.getType().toString()
                # Unpacking byte arrays as little-endian; that's how they're dumped in serialize()
                unpacked_column = np.frombuffer(
                    column.getAsBytes().tostring(),
                    dtype=np.dtype(
                        java_type_to_np_type[column_java_type]
                    ).newbyteorder('<')
                )
                # In case the host machine is big-endian, the array needs to be adjusted.
                # Reference:
                # https://pandas.pydata.org/pandas-docs/stable/user_guide/gotchas.html#byte-ordering-issues
                if sys.byteorder == 'big':
                    unpacked_column = unpacked_column.byteswap().newbyteorder()
                columns_with_names[column_name] = unpacked_column
                column_names_to_pandas_types[column_name] = java_type_to_pd_type[column_java_type]

        # Create the DataFrame and resolve remaining Jnius objects (convert them to python)
        df = pd.DataFrame(columns_with_names).astype(column_names_to_pandas_types)

        # Replace nulls with Pandas nullable numeric type
        for column in serialized_columns:
            if column.isBytes():
                # Unpacking byte arrays as little-endian; that's how they're dumped in serialize()
                null_indices = np.frombuffer(
                    column.getNullIndicesAsBytes().tostring(),
                    dtype=np.dtype('int32').newbyteorder('<')
                )
                df.loc[null_indices, column.getName()] = pd.NA

        for column_index in self._id_cols.keys():
            column_name = self.pgql_result_elements[column_index]
            df[column_name] = df[column_name].apply(self._convert_item_to_python)

        return df.sort_index().infer_objects()

    def absolute(self, row: int) -> bool:
        """Move the cursor to the given row number in this ResultSet object.

        If the row number is positive, the cursor moves to the given row number with respect to the
        beginning of the result set. The first row is 1, so absolute(1) moves the cursor to the
        first row.

        If the row number is negative, the cursor moves to the given row number with respect to the
        end of the result set. So absolute(-1) moves the cursor to the last row.

        :param row: Row to move to

        :return: True if the cursor is moved to a position in the ResultSet object;
            False if the cursor is moved before the first or after the last row
        """
        self._assert_not_closed()
        return bool(java_handler(self._pgql_result_set.absolute, [row]))

    def relative(self, rows: int) -> bool:
        """Move the cursor a relative number of row with respect to the current position. A
        negative number will move the cursor backwards.

        Note: Calling relative(1) is equal to next() and relative(-1) is equal to previous. Calling
        relative(0) is possible when the cursor is positioned at a row, not when it is positioned
        before the first or after the last row. However, relative(0) will not update the position of
        the cursor.

        :param rows: Relative number of rows to move from current position

        :return: True if the cursor is moved to a position in the ResultSet object; False if
            the cursor is moved before the first or after the last row
        """
        self._assert_not_closed()
        return java_handler(self._pgql_result_set.relative, [rows])

    def before_first(self) -> None:
        """Set the cursor before the first row"""
        self._assert_not_closed()
        java_handler(self._pgql_result_set.beforeFirst, [])

    def after_last(self) -> None:
        """Place the cursor after the last row"""
        self._assert_not_closed()
        java_handler(self._pgql_result_set.afterLast, [])

    def first(self) -> bool:
        """Move the cursor to the first row in the result set

        :return: True if the cursor points to a valid row; False if the result set does not
            have any results
        """
        self._assert_not_closed()
        return bool(java_handler(self._pgql_result_set.first, []))

    def last(self) -> bool:
        """Move the cursor to the first row in the result set

        :return: True if the cursor points to a valid row; False if the result set does not
            have any results
        """
        self._assert_not_closed()
        return bool(java_handler(self._pgql_result_set.last, []))

    def next(self) -> bool:
        """Move the cursor forward one row from its current position

        :return: True if the cursor points to a valid row; False if the new cursor is positioned
            after the last row
        """
        self._assert_not_closed()
        return bool(java_handler(self._pgql_result_set.next, []))

    def previous(self) -> bool:
        """Move the cursor to the previous row from its current position

        :return: True if the cursor points to a valid row; False if the new cursor is positioned
            before the first row
        """
        self._assert_not_closed()
        return bool(java_handler(self._pgql_result_set.previous, []))

    def get(self, element: Union[str, int]) -> Any:
        """Get the value of the designated element by element index or name

        :param element: Integer or string representing index or name
        :return: Content of cell
        """
        self._assert_not_closed()
        java_value = java_handler(self._pgql_result_set.getObject, [element])
        return conversion.anything_to_python(java_value)

    def get_boolean(self, element: Union[str, int]) -> Optional[bool]:
        """Get the value of the designated element by element index or name as a Boolean

        :param element: Integer or String representing index or name
        :return: Boolean
        """
        self._assert_not_closed()
        result = java_handler(self._pgql_result_set.getBoolean, [element])
        return conversion.optional_boolean_to_python(result)

    def get_date(self, element: Union[str, int]) -> Optional[date]:
        """Get the value of the designated element by element index or name as a datetime Date

        :param element: Integer or String representing index or name
        :return: datetime.date
        """
        self._assert_not_closed()
        java_local_date = java_handler(self._pgql_result_set.getDate, [element])
        return conversion.local_date_to_python(java_local_date)

    def get_double(self, element: Union[str, int]) -> Optional[float]:
        """Get the value of the designated element by element index or name as a float.

        This method is for precision, as a Java floats and doubles have different precisions.

        :param element: Integer or String representing index or name
        :return: Float
        """
        self._assert_not_closed()
        return java_handler(self._pgql_result_set.getDouble, [element])

    def get_edge(self, element: Union[str, int]) -> Optional["PgxEdge"]:
        """Get the value of the designated element by element index or name as a PgxEdge.

        :param element: Integer or String representing index or name
        :return: PgxEdge
        """
        from pypgx.api._pgx_entity import PgxEdge

        self._assert_not_closed()
        java_edge = java_handler(self._pgql_result_set.getEdge, [element])
        if self.graph is None:
            raise TypeError(
                "This `PgqlResultSet` was initialized without a graph, so cannot get vertex."
            )
        elif java_edge is None:
            return None
        return PgxEdge(self.graph, java_edge)

    def get_float(self, element: Union[str, int]) -> Optional[float]:
        """Get the value of the designated element by element index or name as a float.

        This method returns a value with less precision than a double usually has.

        :param element: Integer or String representing index or name
        :return: Float
        """
        self._assert_not_closed()
        return java_handler(self._pgql_result_set.getFloat, [element])

    def get_integer(self, element: Union[str, int]) -> Optional[int]:
        """Get the value of the designated element by element index or name as an int.

        :param element: Integer or String representing index or name
        :return: Integer
        """
        self._assert_not_closed()
        return java_handler(self._pgql_result_set.getInteger, [element])

    def get_legacy_datetime(self, element: Union[str, int]) -> Optional[datetime]:
        """Get the value of the designated element by element index or name as a datetime.

        Works with most time and date type cells. If the date is not specified, default is set to
        to Jan 1 1970.

        :param element: Integer or String representing index or name
        :return: datetime.datetime
        """
        self._assert_not_closed()
        java_date = java_handler(self._pgql_result_set.getLegacyDate, [element])
        return conversion.legacy_date_to_python(java_date)

    def get_list(self, element: Union[str, int]) -> Optional[List[str]]:
        """Get the value of the designated element by element index or name as a list.

        :param element: Integer or String representing index or name
        :return: List
        """
        # The return type is Optional[...] because this method returns None if the PGQL query gives
        # a null value, which can happen with ARRAY_AGG.

        self._assert_not_closed()
        java_list = java_handler(self._pgql_result_set.getList, [element])
        return conversion.collection_to_python_list(java_list)

    def get_long(self, element: Union[str, int]) -> Optional[int]:
        """Get the value of the designated element by element index or name as an int.

        :param element: Integer or String representing index or name
        :return: Long
        """
        return java_handler(self._pgql_result_set.getLong, [element])

    def get_point2d(self, element: Union[str, int]) -> Optional[Tuple[float, float]]:
        """Get the value of the designated element by element index or name as a 2D tuple.

        :param element: Integer or String representing index or name
        :return: (X, Y)
        """
        self._assert_not_closed()
        java_point2d = java_handler(self._pgql_result_set.getPoint2D, [element])
        return conversion.point2d_to_python(java_point2d)

    def get_string(self, element: Union[str, int]) -> Optional[str]:
        """Get the value of the designated element by element index or name as a string.

        :param element: Integer or String representing index or name
        :return: String
        """
        self._assert_not_closed()
        return java_handler(self._pgql_result_set.getString, [element])

    def get_time(self, element: Union[str, int]) -> Optional[time]:
        """Get the value of the designated element by element index or name as a datetime Time.

        :param element: Integer or String representing index or name
        :return: datetime.time
        """
        self._assert_not_closed()
        java_time = java_handler(self._pgql_result_set.getTime, [element])
        return conversion.local_time_to_python(java_time)

    def get_time_with_timezone(self, element: Union[str, int]) -> Optional[time]:
        """Get the value of the designated element by element index or name as a datetime Time that
        includes timezone.

        :param element: Integer or String representing index or name
        :return: datetime.time
        """
        self._assert_not_closed()
        time = java_handler(self._pgql_result_set.getTimeWithTimezone, [element])
        return conversion.time_with_timezone_to_python(time)

    def get_timestamp(self, element: Union[str, int]) -> Optional[datetime]:
        """Get the value of the designated element by element index or name as a datetime.

        :param element: Integer or String representing index or name
        :return: datetime.datetime
        """
        self._assert_not_closed()
        java_timestamp = java_handler(self._pgql_result_set.getTimestamp, [element])
        return conversion.timestamp_to_python(java_timestamp)

    def get_timestamp_with_timezone(self, element: Union[str, int]) -> Optional[datetime]:
        """Get the value of the designated element by element index or name as a datetime.

        :param element: Integer or String representing index or name
        :return: datetime.datetime
        """
        self._assert_not_closed()
        java_timestamp = java_handler(self._pgql_result_set.getTimestampWithTimezone, [element])
        return conversion.timestamp_with_timezone_to_python(java_timestamp)

    def get_vertex(self, element: Union[str, int]) -> Optional["PgxVertex"]:
        """Get the value of the designated element by element index or name as a PgxVertex.

        :param element: Integer or String representing index or name
        :return: PgxVertex
        """
        from pypgx.api._pgx_entity import PgxVertex

        self._assert_not_closed()
        java_vertex = java_handler(self._pgql_result_set.getVertex, [element])
        if self.graph is None:
            raise TypeError(
                "This `PgqlResultSet` was initialized without a graph, so cannot get vertex."
            )
        elif java_vertex is None:
            return None
        return PgxVertex(self.graph, java_vertex)

    # Unlike most other getters on this class, this can't return None.
    def get_vertex_labels(self, element: Union[str, int]) -> Collection[str]:
        """Get the value of the designated element by element index or name as a collection of
        labels.

        Note: This method currently returns a list, but this behavior should not be relied upon.
        In a future version, a set will be returned instead.

        :param element: Integer or String representing index or name
        :return: collection of labels
        """
        self._assert_not_closed()
        java_labels = java_handler(self._pgql_result_set.getVertexLabels, [element])
        return conversion.collection_to_python_list(java_labels)

    def __len__(self) -> int:
        self._assert_not_closed()
        return self.num_results

    def __getitem__(self, idx: Union[slice, int]) -> Union[List[list], List[Any]]:
        self._assert_not_closed()
        if isinstance(idx, slice):
            istart = 0 if idx.start is None else idx.start
            istop = self.num_results if idx.stop is None else idx.stop
            istep = 1 if idx.step is None else idx.step
            return self.get_slice(start=istart, stop=istop - 1, step=istep)
        else:
            return self.get_row(idx)

    def __iter__(self) -> Iterator[List[Any]]:
        """Iterate over result_set object
        This method may change result_set cursor.
        """
        self._assert_not_closed()
        return (self.get_row(row) for row in range(self.num_results))

    def __repr__(self) -> str:
        self._assert_not_closed()
        return "{}(id: {}, num. results: {}, graph: {})".format(
            self.__class__.__name__,
            self.id,
            self.num_results,
            (self.graph.name if self.graph is not None else "None"),
        )

    def __str__(self) -> str:
        self._assert_not_closed()
        return repr(self)

    def print(
        self,
        file: Optional[TextIO] = None,
        num_results: int = DEFAULT_PRINT_LIMIT,
        start: int = 0,
    ) -> None:
        """Print the result set.

        :param file: File to which results are printed (default is ``sys.stdout``)
        :param num_results: Number of results to be printed
        :param start: Index of the first result to be printed
        """
        self._assert_not_closed()
        if file is None:
            # We don't have sys.stdout as a default parameter so that any changes
            # to sys.stdout are taken into account by this function
            file = sys.stdout

        # GM-21982: redirect output to the right file
        output_stream = ByteArrayOutputStream()
        print_stream = PrintStream(output_stream, True)
        self._pgql_result_set.print(print_stream, num_results, start)
        print(output_stream.toString(), file=file)
        print_stream.close()
        output_stream.close()

    def __hash__(self) -> int:
        self._assert_not_closed()
        graph_name = str(self.graph.name) if self.graph is not None else "-"
        return hash((str(self), graph_name, str()))

    def __eq__(self, other: object) -> bool:
        self._assert_not_closed()
        if not isinstance(other, self.__class__):
            return False
        return bool(self._pgql_result_set.equals(other._pgql_result_set))

    def close(self) -> None:
        """Free resources on the server taken up by this frame."""
        java_handler(self._pgql_result_set.close, [])
        self.is_closed = True
