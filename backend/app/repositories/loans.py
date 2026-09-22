import sqlite3
def list_all(conn): return [dict(r) for r in conn.execute("SELECT * FROM loans ORDER BY id").fetchall()]
def get(conn, lid):
    row = conn.execute("SELECT * FROM loans WHERE id=?", (lid,)).fetchone()
    return dict(row) if row else None
def update(conn, lid, fields):
    cols = [k for k in ("name", "principal", "annual_rate", "months") if fields.get(k) is not None]
    if cols:
        conn.execute(f"UPDATE loans SET {', '.join(f'{c}=?' for c in cols)} WHERE id=?",
            [fields[c] for c in cols] + [lid])
        conn.commit()
    return get(conn, lid)
