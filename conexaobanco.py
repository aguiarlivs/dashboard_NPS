from db_connection import get_connection

query = """
SELECT *
FROM public.integracao_nps
LIMIT 10;
"""

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        colunas = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

dados = [dict(zip(colunas, row)) for row in rows]

for linha in dados:
    print(linha)
