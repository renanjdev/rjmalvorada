from app import db_connection

def limpar_dados_teste():
    conn = db_connection()
    cursor = conn.cursor()

    # Deletar todos os registros da tabela `frequencia`
    cursor.execute("DELETE FROM frequencia;")

    # Opcional: Reiniciar o ID autoincrementado
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'frequencia';")

    conn.commit()
    conn.close()
    print("Dados de teste removidos com sucesso!")
