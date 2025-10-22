from __future__ import annotations

import inspect
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Mapping,
    Protocol,
    Union,
)

import pyarrow
from _chalk_shared_public.chalk_function_registry import CHALK_SQL_FUNCTION_REGISTRY

from libchalk.chalksql import (
    ChalkSqlCatalog,
    PyTableProvider,
    sql_to_table,
)
from libchalk.chalktable import ChalkTable, SchemaDescriptor

from .dataframe import DataFrame, _generate_table_name
from .lazyframe import LazyFrame

# TODO: support LazyFrame
COMPATIBLE_TYPES = (pyarrow.Table, pyarrow.RecordBatch, DataFrame)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping
    from types import TracebackType
    from typing import Any, TypeAlias

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

    CompatibleFrameType: TypeAlias = Union[pyarrow.Table, pyarrow.RecordBatch, DataFrame, LazyFrame]

    from libchalk.chalksql import BatchUDFTableProvider, PyTableProvider
    from libchalk.utils import ChalkError as LibChalkError

    class TableProviderSpec(Protocol):
        def scan(self) -> ChalkTable: ...
        def get_schema(self) -> SchemaDescriptor: ...

    # taken from chalk-private/engine/chalkengine/chalksql/providers
    class SchemaProvider(Protocol):
        """Protocol for schema providers that provide table information and table resolution."""

        def get_tables(self) -> list[str]:
            """Return a list of available table names."""
            ...

        def resolve_table(self, table_name: str) -> "PyTableProvider | BatchUDFTableProvider | LibChalkError":
            """Resolve a table name to a table provider, or a LibChalkError for user errors"""
            ...

        def get_description(self) -> str:
            """Return a description of the schema provider."""
            ...


# implements TableProvider
class SimpleTableProvider:
    def __init__(self, table: ChalkTable):
        self.table = table

    def get_schema(self) -> SchemaDescriptor:
        return self.table.schema

    def scan(self) -> ChalkTable:
        return self.table


# implements SchemaProvider
class SimpleSchemaProvider:
    def __init__(self, tables: dict[str, ChalkTable]):
        self.tables = tables

    def get_tables(self):
        return list(self.tables.keys())

    def register_table(self, name: str, table: ChalkTable):
        self.tables[name] = table

    def resolve_table(self, table_name: str):
        return PyTableProvider(SimpleTableProvider(self.tables[table_name]))

    def get_description(self):
        return "The set of ChalkTable's registered in SQLContext"


def _get_frame_locals(
    *,
    of_type: type | Collection[type] | Callable[[Any], bool] | None = COMPATIBLE_TYPES,
    n_objects: int | None = None,
    named: str | Collection[str] | Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Return compatible frame objects from the local stack."""
    return _get_stack_locals(of_type=of_type, n_objects=n_objects, named=named)


def _get_stack_locals(
    of_type: type | Collection[type] | Callable[[Any], bool] | None = None,
    *,
    named: str | Collection[str] | None = None,
    n_objects: int | None = None,
    n_frames: int | None = None,
) -> dict[str, Any]:
    """
    Taken from: https://github.com/pola-rs/polars/blob/py-1.34.0/py-polars/src/polars/_utils/various.py#L507
    Retrieve f_locals from all (or the last 'n') stack frames from the calling location.

    Parameters
    ----------
    of_type
        Only return objects of this type; can be a single class, tuple of
        classes, or a callable that returns True/False if the object being
        tested is considered a match.
    n_objects
        If specified, return only the most recent `n` matching objects.
    n_frames
        If specified, look at objects in the last `n` stack frames only.
    named
        If specified, only return objects matching the given name(s).
    """
    objects: dict[str, CompatibleFrameType] = {}
    examined_frames = 0

    if isinstance(named, str):
        named = (named,)
    if n_frames is None:
        n_frames = sys.maxsize

    if inspect.isfunction(of_type):
        matches_type = of_type
    else:
        if isinstance(of_type, Collection):
            of_type = tuple(of_type)

        def matches_type(obj: Any) -> bool:
            return isinstance(obj, of_type)

    if named is not None:
        if isinstance(named, str):
            named = (named,)
        elif not isinstance(named, set):
            named = set(named)

    stack_frame = inspect.currentframe()
    stack_frame = getattr(stack_frame, "f_back", None)
    try:
        while stack_frame and examined_frames < n_frames:
            local_items = list(stack_frame.f_locals.items())
            global_items = list(stack_frame.f_globals.items()) if stack_frame.f_globals else []

            # Search locals first
            for nm, obj in reversed(local_items):
                if nm not in objects and (named is None or nm in named) and (of_type is None or matches_type(obj)):
                    objects[nm] = obj
                    if n_objects is not None and len(objects) >= n_objects:
                        return objects

            # Also check globals for the current frame
            for nm, obj in reversed(global_items):
                if nm not in objects and (named is None or nm in named) and (of_type is None or matches_type(obj)):
                    objects[nm] = obj
                    if n_objects is not None and len(objects) >= n_objects:
                        return objects

            stack_frame = stack_frame.f_back
            examined_frames += 1
    finally:
        # https://docs.python.org/3/library/inspect.html
        # > Though the cycle detector will catch these, destruction of the frames
        # > (and local variables) can be made deterministic by removing the cycle
        # > in a finally clause.
        del stack_frame

    return objects


class SQLContext:
    """
    Run SQL queries against DataFrame and arrow data.
    """

    _catalog: ChalkSqlCatalog
    _env: str
    _schema_prover: SimpleSchemaProvider
    _tables_scope_stack: list[set[str]]

    def __init__(
        self,
        frames: Mapping[str, CompatibleFrameType] | None = None,
        *,
        register_globals: bool | int = False,
        function_registry=CHALK_SQL_FUNCTION_REGISTRY,
        **named_frames: CompatibleFrameType,
    ) -> None:
        """
        Initialize a new `SQLContext`.

        Parameters
        ----------
        frames
            A `{name:frame, ...}` mapping which can include DataFrames *and*
            pyarrow Table and RecordBatch objects.
        register_globals
            Register compatible objects found
            in the globals, automatically mapping their variable name to a table name.
            To register other objects (pandas/pyarrow data) pass them explicitly, or
            call the `execute_global` classmethod. If given an integer then only the
            most recent "n" objects found will be registered.
        **named_frames
            Named eager/lazy frames, provided as kwargs.
        """
        frames = dict(frames or {})
        if register_globals:
            for name, obj in _get_frame_locals().items():
                if name not in frames and name not in named_frames:
                    named_frames[name] = obj

        self._env = _generate_table_name()
        self._schema_provider = SimpleSchemaProvider({})
        self._catalog = ChalkSqlCatalog(function_registry=function_registry)
        self._catalog.register_schema_provider(self._env, self._schema_provider)

        if frames or named_frames:
            frames.update(named_frames)
            self.register_many(frames)

    @classmethod
    def execute_global(cls, query: str) -> DataFrame:
        """
        Immediately execute a SQL query, automatically registering frame globals.

        Parameters
        ----------
        query
            A valid SQL query string.
        """
        # TODO: constrain by table names in query
        with cls(register_globals=True) as ctx:
            return ctx.execute(query=query)

    def __enter__(self) -> Self:
        """Track currently registered tables on scope entry; supports nested scopes."""
        self._tables_scope_stack = getattr(self, "_tables_scope_stack", [])
        self._tables_scope_stack.append(set(self.tables()))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    def __repr__(self) -> str:
        n_tables = len(self.tables())
        return f"<SQLContext [tables:{n_tables}] at 0x{id(self):x}>"

    def execute(self, query: str) -> DataFrame:
        """
        Parse the given SQL query and execute it against the registered frame data.

        Parameters
        ----------
        query
            A valid string SQL query.
        """
        plan = sql_to_table(
            self._catalog,
            self._env,
            query,
        )
        return DataFrame(plan, {})

    def register(self, name: str, frame: CompatibleFrameType) -> Self:
        """
        Register a single frame as a table, using the given name.

        Parameters
        ----------
        name
            Name of the table.
        frame
            eager/lazy frame to associate with this table name.

        See Also
        --------
        register_globals
        register_many
        """
        if isinstance(frame, pyarrow.Table):
            self._catalog.register_constant_table(name, frame)
        elif isinstance(frame, pyarrow.RecordBatch):
            # Convert RecordBatch to Table
            # TODO: handle with register_record_batch
            self._catalog.register_constant_table(name, pyarrow.Table.from_batches([frame]))
        elif isinstance(frame, DataFrame):
            _pa = frame._maybe_materialized()
            if _pa:
                self._catalog.register_constant_table(name, _pa)
            else:
                self._schema_provider.register_table(name, frame._plan)
        else:
            raise TypeError(f"{name} has unsupported table type {type(frame)}")

        return self

    def register_globals(self, n: int | None = None) -> Self:
        """
        Register all frames (lazy or eager) found in the current globals scope.

        Automatically maps variable names to table names.

        See Also
        --------
        register
        register_many

        Parameters
        ----------
        n
            Register only the most recent "n" frames.
        """
        frames = _get_frame_locals(n_objects=n)
        return self.register_many(frames=frames)

    def register_many(
        self,
        frames: Mapping[str, CompatibleFrameType] | None = None,
        **named_frames: CompatibleFrameType,
    ) -> Self:
        """
        Register multiple eager/lazy frames as tables, using the associated names.

        Parameters
        ----------
        frames
            A `{name:frame, ...}` mapping.
        **named_frames
            Named eager/lazy frames, provided as kwargs.

        See Also
        --------
        register
        register_globals
        """
        frames = dict(frames or {})
        frames.update(named_frames)
        for name, frame in frames.items():
            self.register(name, frame)
        return self

    def tables(self) -> list[str]:
        """
        Return a list of the registered table names.

        Notes
        -----
        The :meth:`tables` method will return the same values as the
        "SHOW TABLES" SQL statement, but as a list instead of a frame.
        """
        result = self.execute("SHOW TABLES")
        batches = result.run()
        if batches:
            arrow_table = pyarrow.Table.from_batches(batches)
            return arrow_table.column("table_name").to_pylist()
        return []
