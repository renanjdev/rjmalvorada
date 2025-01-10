from app import db_connection

def limpar_dados_teste():
    conn = db_connection()
    cursor = conn.cursor()

    # Deletar registros da tabela `frequencia`
    cursor.execute("DELETE FROM frequencia;")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'frequencia';")  # Resetar ID autoincrementado

    # Deletar registros da tabela `jovens`
    cursor.execute("DELETE FROM jovens;")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'jovens';")  # Resetar ID autoincrementado

    conn.commit()
    conn.close()
    print("Todos os dados de teste foram removidos com sucesso!")

if __name__ == "__main__":
    limpar_dados_teste()
