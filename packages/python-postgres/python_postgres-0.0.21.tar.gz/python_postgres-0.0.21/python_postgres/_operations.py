from typing import LiteralString, Optional

import psycopg
from psycopg import AsyncCursor, sql
from psycopg.sql import Composed
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from .types import Params, PydanticParams, Query


async def exec_query(
    pool: AsyncConnectionPool,
    cur: AsyncCursor,
    query: Query,
    params: Params,
    is_retry: bool = False,
    **kwargs,
) -> None:
    try:
        if not params:
            await cur.execute(query)
            return
        if isinstance(params, BaseModel) or (
            isinstance(params, list) and isinstance(params[0], BaseModel)
        ):
            params = _pydantic_param_to_values(params, **kwargs)
        if isinstance(params, list):
            await cur.executemany(query, params)
            return
        await cur.execute(query, params)
    except psycopg.OperationalError as error:
        if is_retry:
            raise error
        await pool.check()
        await exec_query(pool, cur, query, params, True)


def expand_values(
    table_name: LiteralString,
    values: PydanticParams,
    returning: Optional[list[LiteralString]] = None,
    **kwargs,
) -> tuple[Composed, tuple]:
    query = sql.SQL("INSERT INTO ") + sql.Identifier(table_name)
    if isinstance(values, BaseModel):
        raw = values.model_dump(**kwargs, exclude_none=True)
        vals = tuple(Jsonb(v) if _is_json(v) else v for v in raw.values())
        statement = (
            query
            + sql.SQL("(")
            + sql.SQL(", ").join(sql.Identifier(k) for k in raw.keys())
            + sql.SQL(")")
            + sql.SQL("VALUES")
            + sql.SQL("(")
            + sql.SQL(", ").join(sql.Placeholder() for _ in range(len(vals)))
            + sql.SQL(")")
        )
        statement = _returning(statement, returning)
        # debug = statement.as_string()
        return statement, vals

    models, col_names, row_sqls, row_values = [], set(), [], []
    for v in values:
        m_dict = v.model_dump(**kwargs, exclude_none=True)
        models.append(m_dict)
        col_names.update(m_dict.keys())

    for model in models:
        placeholders, row = [], []
        for c in col_names:
            if c in model:
                placeholders.append(sql.Placeholder())
                row_val = model[c]
                row.append(Jsonb(row_val) if _is_json(row_val) else row_val)
            else:
                placeholders.append(sql.DEFAULT)
        row_sqls.append(sql.SQL("(") + sql.SQL(", ").join(placeholders) + sql.SQL(")"))
        row_values.extend(row)
    columns_sql = (
        sql.SQL("(") + sql.SQL(", ").join(sql.Identifier(col) for col in col_names) + sql.SQL(")")
    )
    statement = _returning(
        query + columns_sql + sql.SQL("VALUES") + sql.SQL(", ").join(row_sqls), returning
    )
    # debug = statement.as_string()
    return statement, tuple(row_values)


def _returning(statement: Composed, returning: Optional[list[LiteralString]] = None) -> Composed:
    return (
        statement
        + sql.SQL("RETURNING ")
        + sql.SQL(", ").join(sql.Identifier(col) for col in returning)
        if returning
        else statement
    )


def _is_json(value: object) -> bool:
    return isinstance(value, dict) or (isinstance(value, list) and isinstance(value[0], dict))


def _model_to_values(model: BaseModel, **kwargs) -> tuple:
    return tuple(
        Jsonb(v) if _is_json(v) else v
        for v in model.model_dump(**kwargs, exclude_none=True).values()
    )


def _pydantic_param_to_values(model: PydanticParams, **kwargs) -> tuple | list[tuple]:
    return (
        [_model_to_values(m, **kwargs) for m in model]
        if isinstance(model, list)
        else _model_to_values(model, **kwargs)
    )
