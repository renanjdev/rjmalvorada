import random
from datetime import datetime, timedelta
from app import db_connection

def gerar_registros_teste():
    conn = db_connection()
    cursor = conn.cursor()

    # Lista de IDs de exemplo (ajuste conforme sua tabela `jovens`)
    ids_jovens = [1, 2, 3, 4, 5]  # IDs existentes na tabela `jovens`
    status_opcoes = ['presente', 'ausente']

    # Gera 20 registros aleatórios
    hoje = datetime.now()
    for i in range(20):
        pessoa_id = random.choice(ids_jovens)
        data = (hoje - timedelta(weeks=i)).strftime('%Y-%m-%d')  # Reuniões semanais
        status = random.choice(status_opcoes)

        # Inserir no banco
        cursor.execute("""
        INSERT INTO frequencia (pessoa_id, data, status)
        VALUES (?, ?, ?)
        """, (pessoa_id, data, status))

    conn.commit()
    conn.close()
    print("20 registros de teste adicionados com sucesso!")
