from typing import List, Union

import sqlparse
from sqlalchemy import text
from sqlalchemy.orm import Session


def is_readonly_sql(sql: str) -> bool:
    """
    只允许：
      SELECT / WITH / VALUES / EXPLAIN / DESCRIBE / SHOW
    拒绝：
      INSERT/UPDATE/DELETE/CREATE/ALTER/DROP/TRUNCATE/LOAD/REPLACE/LOCK/UNLOCK/GRANT/REVOKE/EXECUTE/CALL
    """
    sql_clean = sqlparse.format(sql.strip(), strip_comments=True)
    tokens = [t.normalized for t in sqlparse.parse(sql_clean)[0].flatten()
              if t.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.DML, sqlparse.tokens.DDL)]

    forbidden = {"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE",
                 "LOAD", "REPLACE", "LOCK", "UNLOCK", "GRANT", "REVOKE", "EXEC", "CALL"}
    allowed_root = {"SELECT", "WITH", "EXPLAIN", "DESCRIBE", "SHOW", "VALUES"}

    root = tokens[0].upper() if tokens else ""
    if root not in allowed_root:
        return False
    if any(k in forbidden for k in tokens):
        return False
    return True


def session_sql_execute(db_session: Session, sql_text: Union[str, List], query_only: bool = True):
    if isinstance(sql_text, str):
        # 处理单条SQL语句
        if query_only:
            if not is_readonly_sql(sql_text):
                return []
        result = db_session.execute(text(f"{sql_text}"))
        columns = list(result.keys())
        rows = [dict(zip(columns, r)) for r in result.fetchall()]
        return rows
    elif isinstance(sql_text, list):
        results = []
        for sub_sql_text in sql_text:
            if query_only:
                if not is_readonly_sql(sub_sql_text):
                    continue
            result = db_session.execute(text(f"{sub_sql_text}"))
            columns = list(result.keys())
            rows = [dict(zip(columns, r)) for r in result.fetchall()]
            results.append(rows)
            return results
    else:
        return []
