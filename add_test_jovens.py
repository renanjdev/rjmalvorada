import random
from faker import Faker
from app import db_connection

def cadastrar_jovens_teste():
    fake = Faker("pt_BR")
    conn = db_connection()
    cursor = conn.cursor()

    grupos = ["Meninos 0 a 6 anos", "Meninas 0 a 6 anos", "Meninos 7 a 11 anos", "Meninas 7 a 11 anos", "Moços 12+ anos", "Moças 12+ anos"]
    batizados = ["sim", "nao"]

    for _ in range(30):
        nome = fake.first_name()
        data_nascimento = fake.date_of_birth(minimum_age=5, maximum_age=20)
        whatsapp = fake.phone_number()
        endereco = fake.address()
        pais = f"{fake.first_name()} e {fake.first_name()}"
        grupo_recitativo = random.choice(grupos)
        batizado = random.choice(batizados)
        data_batismo = fake.date_between(start_date="-10y", end_date="today") if batizado == "sim" else None
        observacoes = fake.sentence()

        cursor.execute("""
        INSERT INTO jovens (nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, batizado, data_batismo, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, batizado, data_batismo, observacoes))

    conn.commit()
    conn.close()
    print("30 jovens de teste adicionados com sucesso!")

if __name__ == "__main__":
    cadastrar_jovens_teste()
