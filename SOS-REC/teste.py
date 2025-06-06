import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'documento',  # Atualize para o novo banco UTF8
    'user': 'postgres',
    'password': '12345',
    'port': 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("Conectado com sucesso!")

    # O encoding agora é UTF8 por padrão, não precisa ajustar!
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuario LIMIT 5;")
    dados = cur.fetchall()

    for row in dados:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("Erro:", e)
