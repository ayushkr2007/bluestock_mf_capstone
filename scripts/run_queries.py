import sqlite3

conn = sqlite3.connect("data/db/bluestock_mf.db")
with open("sql/queries.sql") as f:
    sql_text = f.read()

import re
blocks = re.split(r'(?=-- Q\d+:)', sql_text)
for block in blocks:
    block = block.strip()
    if not block.startswith("-- Q"):
        continue
    label = block.split("\n")[0]
    query = "\n".join(block.split("\n")[1:])
    print(label)
    cur = conn.execute(query)
    for row in cur.fetchmany(5):
        print("  ", row)
    print()
conn.close()