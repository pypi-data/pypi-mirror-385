"""Functions to interact with database."""
import dataclasses
import datetime

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

from membank import errors as e


# Mapping of Python types with SQL types
SQL_TABLE_TYPES = {
    float: sa.Float,
    str: sa.String,
    int: sa.Integer,
    datetime.datetime: sa.DateTime,
    datetime.date: sa.Date,
    bytes: sa.LargeBinary,
    bool: sa.Boolean,
    dict: sa.JSON,
    list: sa.JSON,
}


def get_sql_col_type(py_type):
    """From Python data type py_type returns SQL type."""
    if py_type in SQL_TABLE_TYPES:
        return SQL_TABLE_TYPES[py_type]
    raise e.GeneralMemoryError(f"Type {py_type} is not supported")


def make_stmt(sql_table, return_class, *filtering, **matching):
    """Do select stmt."""
    stmt = sa.select(*_get_selectables(sql_table, return_class))
    return filter_stmt(stmt, sql_table, *filtering, **matching)


def filter_stmt(stmt, sql_table, *filtering, **matching):
    """Prepare SQL statement and returns it."""
    if matching:
        for key, value in matching.items():
            stmt = stmt.where(getattr(sql_table.c, key) == value)
    if filtering:
        for item in filtering:
            stmt = stmt.where(item)
    return stmt


def get_item(sql_table, engine, return_class, **matching):
    """Get item from table."""
    stmt = make_stmt(sql_table, return_class, **matching)
    with engine.connect() as conn:
        cursor = execute_stmt(conn, stmt).first()
    return return_class(*cursor) if cursor else None


def get_list(sql_table, engine, return_class, *filtering, **matching):
    """Get list of items from table."""
    stmt = make_stmt(sql_table, return_class, *filtering, **matching)
    return get_from_sql(return_class, stmt, engine)


def delete_item(sql_table, engine, **matching):
    """Execute delete stmt."""
    stmt = sa.delete(sql_table)
    stmt = filter_stmt(stmt, sql_table, **matching)
    with engine.connect() as conn:
        execute_stmt(conn, stmt)
        conn.commit()


def get_from_sql(return_class, stmt, engine):
    """Get all items from table as per SQL statement."""
    with engine.connect() as conn:
        cursor = execute_stmt(conn, stmt)
        return [return_class(*i) for i in cursor]


def update_item(sql_table, engine, item, key=None):
    """Create or update an item in table."""
    stmt = sa.select(sql_table)
    if key:
        col = _getmemattr(sql_table.c, key)
        val = getattr(item, key)
        stmt = stmt.where(col == val)
    else:
        for col, val in _unpack_values(item, sql_table):
            stmt = stmt.where(col == val)
    with engine.connect() as conn:
        rows = execute_stmt(conn, stmt)
        record = rows.first()
    if not record or (record and key):
        if record and key:
            col = getattr(sql_table.c, key)
            val = getattr(item, key)
            stmt = sql_table.update()
            stmt = stmt.where(col == val)
        else:
            stmt = sql_table.insert()
        stmt = stmt.values(dict(_unpack_values(item, sql_table)))
        with engine.connect() as conn:
            with conn.begin():
                execute_stmt(conn, stmt)


def execute_stmt(conn, stmt):
    """Execute SQL statement."""
    try:
        return conn.execute(stmt)
    except sa.exc.StatementError as error:
        msg = str(error.orig)
        if isinstance(error.orig, TypeError):
            msg += " Invalid field type, possibly use 'encode' in metadata"
        if "no such table:" in msg:
            msg = msg.split(":", maxsplit=1)[-1].strip()
            raise e.MemoryTableDoesNotExist(msg) from None
        raise e.GeneralMemoryError(msg) from None


def sync_table(sql_table, engine, obj):
    """Sync table as per obj values."""
    with engine.connect() as conn:
        alembic = Operations(MigrationContext.configure(conn))
        fields = dataclasses.fields(obj)
        for field in fields:
            if field.name not in sql_table.c:
                col_type = get_sql_col_type(field.type)
                col = sa.Column(field.name, col_type)
                alembic.add_column(sql_table.name, col)


def introspect_table_fields(sql_table):
    """Introspect table fields."""
    fields = []
    for col in sql_table.c:
        col_type = None
        for py_type, sql_type in SQL_TABLE_TYPES.items():
            if isinstance(col.type, sql_type):
                col_type = py_type
                break
        if not col_type:
            msg = f"Column '{col.name}' has unsupported type '{col.type}'"
            raise e.GeneralMemoryError(msg)
        fields.append((col.name, col_type))
    return fields


def create_table(table, instance, engine):
    """Add a memory attribute.

    Memory attribute must be instance of dataclass In database words
    this adds a new Table
    """
    with engine.connect() as conn:
        alembic = Operations(MigrationContext.configure(conn))
        fields = dataclasses.fields(instance)
        cols = []
        for field in fields:
            col_type = get_sql_col_type(field.type)
            col = sa.Column(field.name, col_type)
            cols.append(col)
        try:
            alembic.create_table(table, *cols)
        except sa.exc.OperationalError as error:
            msg = error.args[0]
            if "table" in msg and "already exists" in msg:
                msg = f"Table {table} already exists. Use change instead"
                raise e.GeneralMemoryError(msg) from None


class FilterOperator():
    """Allows to filter memory items by expressions."""

    def __init__(self, name, meta):
        """Initialize."""
        self.__name = name
        if name in meta.tables:
            self.__sql_table = meta.tables[name]
        else:
            self.__sql_table = None
        self.__column = False
        self.__operator = False

    def __lt__(self, other):
        """Operations with <."""
        op = self.__column < other if self.__operator else None
        return self.__sql_table, op

    def __le__(self, other):
        """Operations with <=."""
        op = self.__column <= other if self.__operator else None
        return self.__sql_table, op

    def __eq__(self, other):
        """Operations with ==."""
        op = self.__column == other if self.__operator else None
        return self.__sql_table, op

    def __ne__(self, other):
        """Operations with !=."""
        op = self.__column != other if self.__operator else None
        return self.__sql_table, op

    def __gt__(self, other):
        """Operations with >."""
        op = self.__column > other if self.__operator else None
        return self.__sql_table, op

    def __ge__(self, other):
        """Operations with >=."""
        op = self.__column >= other if self.__operator else None
        return self.__sql_table, op

    def __getattr__(self, name):
        if getattr(self.__sql_table, "name", False):
            self.__column = getattr(self.__sql_table.c, name, False)
            if self.__column is False:
                msg = f"'{self.__name}' does not hold '{name}'"
                raise e.GeneralMemoryError(msg)
            self.__operator = True
        return self


def _getmemattr(obj, name):
    """Get memory attribute."""
    try:
        return getattr(obj, name)
    except AttributeError:
        raise e.MemoryOutOfSyncError(obj, name) from None


def _unpack_values(obj, table):
    """Unpack values from object using table as reference."""
    for i in dataclasses.fields(obj):
        key = _getmemattr(table.c, i.name)
        val = getattr(obj, i.name)
        if "encode" in i.metadata:
            val = i.metadata["encode"](val)
        yield key, val


def _get_selectables(table, obj):
    """Get column names in their respective order as per dataclass object."""
    for i in dataclasses.fields(obj):
        key = _getmemattr(table.c, i.name)
        yield key
