from typing import Any
import sqlalchemy as sa
import sqlalchemy.orm.session as sa_session


def make_update_statement_column_value(
    table: sa.Table,
    column_name: str,
    value: Any
):
    new_value = {column_name: value}
    return sa.update(table).values(**new_value)


def set_column_values_session(
    table: sa.Table,
    column_name: str,
    value: Any,
    session: sa_session.Session
) -> None:
    stmt = make_update_statement_column_value(table, column_name, value)
    session.execute(stmt)


def set_column_values(
    table: sa.Table,
    column_name: str,
    value: Any,
    engine: sa.engine.Engine
) -> None:
    session = sa_session.Session(engine)
    try:
        set_column_values_session(table, column_name, value, session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e