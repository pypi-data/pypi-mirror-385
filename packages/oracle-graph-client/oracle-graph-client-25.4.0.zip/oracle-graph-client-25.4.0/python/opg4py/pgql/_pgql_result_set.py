#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
import sys
from jnius import autoclass
from opg4py._utils.error_handling import java_handler
from opg4py._utils.item_converter import convert_to_python_type
from ._pgql_result_set_metadata import PgqlResultSetMetaData
from datetime import date, datetime, time
from typing import Any, Iterator, List, Optional, Union, TextIO

ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
PrintStream = autoclass('java.io.PrintStream')
ResultSetFormatter = autoclass('oracle.pgql.lang.ResultSetFormatter')


class PgqlResultSet:
    """Wrapper class for oracle.pg.rdbms.pgql.PgqlResultSet."""

    def __init__(self, java_pgql_result_set) -> None:
        self._java_pgql_result_set = java_pgql_result_set
        self._is_closed = False
        self.num_results = 0
        while self._java_pgql_result_set.next():
            self.num_results += 1
        self.before_first()

        metadata = self.get_metadata()
        self._num_columns = metadata.get_column_count()
        self._columns = [metadata.get_column_name(i + 1) for i in range(self._num_columns)]

    def _assert_not_closed(self) -> None:
        if self._is_closed:
            raise RuntimeError("result set closed")

    def get_row(self, row) -> Any:
        """Get row from result_set.

        :param row: Row index
        """
        self._assert_not_closed()
        if row < 0 or row >= self.num_results:
            error_message = "'{idx}' must be an integer: 0 <= '{idx}' <= {max_idx}"
            raise RuntimeError(error_message.format(idx='row', max_idx=self.num_results - 1))

        tmp_row = self._to_list(row, row + 1)[0]

        if self._num_columns == 1:
            return tmp_row[0]

        return tmp_row

    def get_slice(self, start: int, stop: int, step: int = 1) -> List[list]:
        """Get slice from result_set.

        :param start: Start index
        :param stop: Stop index
        :param step: Step size
        """
        self._assert_not_closed()

        if start < 0 or stop > self.num_results or start > stop:
            error_message = "'start': {start} and 'stop': {stop} must define a valid interval within: [0, {max_idx}]"
            raise RuntimeError(error_message.format(start=start, stop=stop, max_idx=self.num_results))

        return [self.get_row(row) for row in range(start, stop, step)]

    def to_pandas(self):
        """Convert to pandas DataFrame (this method requires pandas).

        :return: PgqlResultSet as a Pandas Dataframe
        """
        self._assert_not_closed()

        try:
            import numpy as np  # noqa: F401
        except Exception:
            raise ImportError("Could not import numpy")

        try:
            import pandas as pd
        except Exception:
            raise ImportError("Could not import pandas")

        results = self._to_list(0, self.num_results)
        dataframe = pd.DataFrame(results, columns=self._columns)
        return dataframe.sort_index().infer_objects()

    def _to_list(self, start, stop):
        """Get the section from start to stop of this result_set as a list.

        :param start: Initial index in range
        :param stop: Last index inrage
        """
        self._assert_not_closed()

        if start < 0 or stop > self.num_results or start > stop:
            error_message = "'start': {start} and 'stop': {stop} must define a valid interval within: [0, {max_idx}]"
            raise RuntimeError(error_message.format(start=start, stop=stop, max_idx=self.num_results))

        results = []

        for i in range(start, stop):
            self.absolute(i + 1)  # Results start at index 1
            result = [self.get(column) for column in self._columns]
            results.append(result)

        return results

    def next(self) -> bool:
        """Move the cursor forward one row from its current position.

        :return: True if the cursor points to a valid row; False if the new cursor is positioned after the last row
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.next, [])

    def previous(self) -> bool:
        """Move the cursor to the previous row from its current position.

        :return: True if the cursor points to a valid row; False if the new cursor is positioned before the first row
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.previous, [])

    def before_first(self) -> None:
        """Set the cursor before the first row."""
        self._assert_not_closed()
        java_handler(self._java_pgql_result_set.beforeFirst, [])

    def after_last(self) -> None:
        """Place the cursor after the last row."""
        self._assert_not_closed()
        java_handler(self._java_pgql_result_set.afterLast, [])

    def first(self) -> bool:
        """Move the cursor to the first row in the result set.

        :return: True if the cursor points to a valid row; False if the result set does not have any results
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.first, [])

    def last(self) -> bool:
        """Move the cursor to the last row in the result set.

        :return: True if the cursor points to a valid row; False if the result set does not have any results
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.last, [])

    def absolute(self, row) -> bool:
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
        return java_handler(self._java_pgql_result_set.absolute, [row])

    def relative(self, rows) -> bool:
        """Move the cursor a relative number of row with respect to the current position.

        Note a negative number will move the cursor backwards.

        Note: Calling relative(1) is equal to next() and relative(-1) is equal to previous. Calling
        relative(0) is possible when the cursor is positioned at a row, not when it is positioned
        before the first or after the last row. However, relative(0) will not update the position of
        the cursor.

        :param rows: Relative number of rows to move from current position

        :return: True if the cursor is moved to a position in the ResultSet object;
            False if the cursor is moved before the first or after the last row
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.relative, [rows])

    def get(self, element: Union[str, int]) -> Any:
        """Get the value of the designated element by element index or name.

        :param element: Integer or string representing index or name
        :return: Content of cell
        """
        self._assert_not_closed()
        return convert_to_python_type(java_handler(self._java_pgql_result_set.getObject, [element]))

    def get_boolean(self, element: Union[str, int]) -> Optional[bool]:
        """Get the value of the designated element by element index or name as a Boolean.

        :param element: Integer or String representing index or name
        :return: Boolean
        """
        self._assert_not_closed()
        return bool(java_handler(self._java_pgql_result_set.getBoolean, [element]))

    def get_date(self, element: Union[str, int]) -> Optional[date]:
        """Get the value of the designated element by element index or name as a datetime Date.

        :param element: Integer or String representing index or name
        :return: datetime.date
        """
        self._assert_not_closed()
        return convert_to_python_type(java_handler(self._java_pgql_result_set.getDate, [element]))

    def get_float(self, element: Union[str, int]) -> Optional[float]:
        """Get the value of the designated element by element index or name as a Float.

        :param element: Integer or String representing index or name
        :return: Float
        """
        self._assert_not_closed()
        # Python unified float and double, so retrieve value as Java.lang.Double but treat it as float in Python
        return java_handler(self._java_pgql_result_set.getDouble, [element])

    def get_integer(self, element: Union[str, int]) -> Optional[int]:
        """Get the value of the designated element by element index or name as an Integer.

        :param element: Integer or String representing index or name
        :return: Integer
        """
        self._assert_not_closed()
        # Python unified int and long, so retrieve value as Java.lang.Long but treat it as int in Python
        return java_handler(self._java_pgql_result_set.getLong, [element])

    def get_list(self, element: Union[str, int]) -> Optional[List[str]]:
        """Get the value of the designated element by element index or name as a List.

        :param element: Integer or String representing index or name
        :return: List
        """
        self._assert_not_closed()
        return list(java_handler(self._java_pgql_result_set.getList, [element]))

    def get_string(self, element: Union[str, int]) -> Optional[str]:
        """Get the value of the designated element by element index or name as a String.

        :param element: Integer or String representing index or name
        :return: String
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.getString, [element])

    def get_time(self, element: Union[str, int]) -> Optional[time]:
        """Get the value of the designated element by element index or name as a datetime Time.

        :param element: Integer or String representing index or name
        :return: datetime.time
        """
        self._assert_not_closed()
        return convert_to_python_type(java_handler(self._java_pgql_result_set.getTime, [element]))

    def get_time_with_timezone(self, element: Union[str, int]) -> Optional[time]:
        """Get the value of the designated element by element index or name as a datetime Time with timezone.

        :param element: Integer or String representing index or name
        :return: datetime.time
        """
        self._assert_not_closed()
        time = java_handler(self._java_pgql_result_set.getTimeWithTimezone, [element])
        return convert_to_python_type(time)

    def get_timestamp(self, element: Union[str, int]) -> Optional[datetime]:
        """Get the value of the designated element by element index or name as a Datetime.

        :param element: Integer or String representing index or name
        :return: datetime.datetime
        """
        self._assert_not_closed()
        java_timestamp = java_handler(self._java_pgql_result_set.getTimestamp, [element])
        return convert_to_python_type(java_timestamp)

    def get_timestamp_with_timezone(self, element: Union[str, int]) -> Optional[datetime]:
        """Get the value of the designated element by element index or name as a Datetime with timezone.

        :param element: Integer or String representing index or name
        :return: datetime.datetime
        """
        self._assert_not_closed()
        java_timestamp = java_handler(self._java_pgql_result_set.getTimestampWithTimezone, [element])
        return convert_to_python_type(java_timestamp)

    def get_vertex_labels(self, element: Union[str, int]) -> List[str]:
        """Get the value of the designated element by element index or name as a list of labels.

        :param element: Integer or String representing index or name
        :return: list
        """
        self._assert_not_closed()
        return list(java_handler(self._java_pgql_result_set.getVertexLabels, [element]))

    def get_value_type(self, element) -> int:
        """Get the type of value of the designated element by element index or name as an Integer.

        :param element: Integer or String representing index or name
        :return: Integer
        """
        self._assert_not_closed()
        return java_handler(self._java_pgql_result_set.getValueType, [element])

    def print(
        self,
        file: Optional[TextIO] = None,
        num_results: int = ResultSetFormatter.DEFAULT_PRINT_LIMIT,
        start: int = 0,
    ) -> None:
        """Print the result set.

        :param file: File to which results are printed (default is ``sys.stdout``)
        :param num_results: Number of results to be printed
        :param start: Index of the first result to be printed
        """
        self._assert_not_closed()
        self.before_first()  # Ensure we are at the beginning of the result set
        if file is None:
            # We don't have sys.stdout as a default parameter so that any changes
            # to sys.stdout are taken into account by this function
            file = sys.stdout

        # GM-21982: redirect output to the right file
        output_stream = ByteArrayOutputStream()
        print_stream = PrintStream(output_stream, True)
        java_handler(self._java_pgql_result_set.print, [print_stream, num_results, start])
        print(output_stream.toString(), file=file)
        print_stream.close()
        output_stream.close()
        self.before_first()  # print moves the cursor, move it back to beginning of the result set

    def get_metadata(self) -> PgqlResultSetMetaData:
        """Get the ResultSet MetaData.

        :return: PgqlResultSetMetaData
        """
        java_result_set_metadata = java_handler(self._java_pgql_result_set.getMetaData, [])
        return PgqlResultSetMetaData(java_result_set_metadata)

    def fetchall(self) -> List[tuple]:
        """Fetch all (remaining) rows of a query result, returning them as a list of tuples.
        An empty list is returned if no more rows are available.

        :return: A list of tuples with all (remaining) rows of a query result
        """
        self._assert_not_closed()
        results = []
        while self.next():
            result = tuple(self.get(column) for column in self._columns)
            results.append(result)

        return results

    def fetchmany(self, num_rows: int = 1) -> List[tuple]:
        """Fetch the next set of rows of a query result, returning a list of tuples.
        An empty list is returned if no more rows are available.

        :return: A list of tuples with the next set of rows of a query result
        """
        self._assert_not_closed()
        results = []
        for i in range(num_rows):
            if self.next() is False:
                break
            result = tuple(self.get(column) for column in self._columns)
            results.append(result)

        return results

    def fetchone(self) -> tuple:
        """Fetch the next row of a query result set, returning a single tuple or None when no more data is available.

        :return: A single tuple with the next row of a query result
        """
        self._assert_not_closed()
        return tuple(self.get(column) for column in self._columns) if self.next() else None

    def close(self) -> None:
        """Free resources on the server taken up by this result_set object."""
        java_handler(self._java_pgql_result_set.close, [])
        self._is_closed = True

    def __len__(self) -> int:
        self._assert_not_closed()
        return self.num_results

    def __iter__(self) -> Iterator[List[Any]]:
        """Iterate over result_set object.

        This method may change result_set cursor.
        """
        self._assert_not_closed()
        return (self.get_row(row) for row in range(self.num_results))

    def __getitem__(self, idx: Union[slice, tuple, int]) -> Any:
        self._assert_not_closed()
        if isinstance(idx, int):
            self.absolute(idx)
            return self
        elif isinstance(idx, tuple):
            (index, col_type, column) = idx
            self.absolute(index)
            return self.__get_column_by_type(col_type, column)
        elif isinstance(idx, slice):
            start = 0 if idx.start is None else idx.start
            stop = self.num_results if idx.stop is None else idx.stop
            step = 1 if idx.step is None else idx.step
            return self.get_slice(start, stop, step)

    def __get_column_by_type(self, col_type: str, column: Union[str, int]) -> Any:
        self._assert_not_closed()
        col_type = col_type.lower()
        if col_type == "string":
            return self.get_string(column)
        elif col_type == "integer":
            return self.get_integer(column)
        elif col_type == "float":
            return self.get_float(column)
        elif col_type == "boolean":
            return self.get_boolean(column)
        elif col_type == "vertex_labels":
            return self.get_vertex_labels(column)
        elif col_type == "date":
            return self.get_date(column)
        elif col_type == "time":
            return self.get_time(column)
        elif col_type == "timestamp":
            return self.get_timestamp(column)
        elif col_type == "timeWithTimezone":
            return self.get_time_with_timezone(column)
        elif col_type == "timestampWithTimezone":
            return self.get_timestamp_with_timezone(column)
        elif col_type == "list":
            return self.get_list(column)
        else:
            return self.get(column)

    def __repr__(self) -> str:
        self._assert_not_closed()
        return "{}(java_pgql_result_set: {}, # of results: {})".format(
            self.__class__.__name__, self._java_pgql_result_set.__class__.__name__, len(self))

    def __str__(self) -> str:
        self._assert_not_closed()
        return repr(self)

    def __hash__(self) -> int:
        self._assert_not_closed()
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        self._assert_not_closed()
        if not isinstance(other, self.__class__):
            return False
        return bool(self._java_pgql_result_set.equals(other._java_pgql_result_set))
