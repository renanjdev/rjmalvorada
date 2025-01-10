from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import pandas as pd
import os
import sqlite3

import os



app = Flask(__name__)  # Instância do Flask
app.secret_key = os.getenv('SECRET_KEY', 'chave_padrao_segura')

# Configuração do banco de dados

# Corrigir o prefixo da DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inicializar SQLAlchemy e Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Função para conexão com o banco de dados
def db_connection():
    conn = sqlite3.connect('igreja.db')
    conn.execute("PRAGMA busy_timeout = 5000")  # Espera 5 segundos para evitar bloqueio
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/frequencia', methods=['GET', 'POST'])
def frequencia():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form['data']
        for key in request.form:
            if key.startswith('presente_') or key.startswith('falta_'):
                pessoa_id = key.split('_')[1]
                status = 'presente' if key.startswith('presente_') else 'ausente'

                # Salvar no banco de dados
                cursor.execute("""
                    INSERT INTO frequencia (pessoa_id, data, status)
                    VALUES (?, ?, ?)
                """, (pessoa_id, data, status))

        conn.commit()
        conn.close()
        # Redirecionar para a tela de confirmação
        return redirect(url_for('frequencia_confirmacao'))

    # Obter pessoas e grupos
    grupo = request.args.get('grupo', 'todos')
    cursor.execute("SELECT * FROM pessoas WHERE grupo = ? OR ? = 'todos'", (grupo, grupo))
    pessoas = cursor.fetchall()
    conn.close()

    return render_template('frequencia.html', pessoas=pessoas, grupo=grupo)


@app.route('/frequencia_confirmacao')
def frequencia_confirmacao():
    return render_template('frequencia_confirmacao.html')

@app.before_request
def set_default_tema():
    if 'tema' not in session:
        session['tema'] = 'superhero'  # Tema padrão

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def home():
    if 'logged_in' in session and session['logged_in']:
        tema = session.get('tema', 'superhero')  # Tema padrão
        return render_template('index.html', tema=tema)
    return redirect(url_for('login'))


@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if request.method == 'POST':
        tema = request.form.get('tema', 'default')  # Tema padrão
        session['tema'] = tema
        return redirect(url_for('home'))
    return render_template('configuracoes.html', tema=session.get('tema', 'default'))

@app.route('/salvar_configuracao', methods=['POST'])
def salvar_configuracao():
    tema = request.form['tema']
    session['tema'] = tema
    return redirect(url_for('home'))


# Função para conexão com o banco de dados
def db_connection():
    conn = sqlite3.connect('igreja.db')
    conn.execute("PRAGMA busy_timeout = 5000")  # Espera 5 segundos para evitar bloqueio
    conn.row_factory = sqlite3.Row
    return conn


# Tela de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Login admin
        if username.upper() == "ADMIN" and password == "7698398Re":
            session['logged_in'] = True
            session['user_id'] = 0
            session['username'] = "Admin"
            session['grupo_responsavel'] = "todos"
            return redirect(url_for('home'))

        # Login de auxiliares pelo primeiro nome
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, grupo_responsavel FROM auxiliares
            WHERE SUBSTR(nome, 1, INSTR(nome || ' ', ' ') - 1) = ? AND whatsapp = ?
        """, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['nome'].split()[0]  # Extrai apenas o primeiro nome
            session['grupo_responsavel'] = user['grupo_responsavel']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Usuário ou senha inválidos")

    return render_template('login.html')

def calcular_tempo(data_inicio):
    if not data_inicio:
        return "Não informado"
    hoje = datetime.today()
    delta = hoje - data_inicio
    anos = delta.days // 365
    meses = (delta.days % 365) // 30
    dias = (delta.days % 365) % 30
    return f"{anos} anos, {meses} meses, {dias} dias"


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Cadastro de jovens/crianças
@app.route('/cadastro_jovens', methods=['GET', 'POST'])
def cadastro_jovens():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        whatsapp = request.form['whatsapp']
        endereco = request.form['endereco']
        pais = request.form['pais']
        grupo_recitativo = request.form['grupo_recitativo']
        batizado = request.form['batizado']
        data_batismo = request.form.get('data_batismo', None)
        observacoes = request.form.get('observacoes', '')

        try:
            # Valida as datas
            data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')
            if data_batismo:  # Valida somente se a data de batismo foi fornecida
                data_batismo = datetime.strptime(data_batismo, '%Y-%m-%d')
        except ValueError as e:
            # Retorna para o formulário com uma mensagem de erro
            return render_template(
                'cadastro_jovens.html',
                error="Formato de data inválido. Use o formato YYYY-MM-DD.",
            )

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jovens (nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, batizado, data_batismo, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome,
            data_nascimento.strftime('%Y-%m-%d'),
            whatsapp,
            endereco,
            pais,
            grupo_recitativo,
            batizado,
            data_batismo.strftime('%Y-%m-%d') if data_batismo else None,
            observacoes,
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('listar_jovens'))

    return render_template('cadastro_jovens.html')


# Listar jovens

@app.route('/jovens', methods=['GET'])
def listar_jovens():
    print("Acessando a rota /jovens")
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, batizado, data_batismo, observacoes
        FROM jovens
        ORDER BY nome ASC
    """)
    rows = cursor.fetchall()

    jovens = []
    for row in rows:
        try:
            # Processa dados do jovem
            hoje = datetime.today()
            data_nascimento = datetime.strptime(row['data_nascimento'], '%Y-%m-%d')
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

            # Determina informações do batismo
            if row['batizado'] == 'sim' and row['data_batismo']:
                data_batismo = datetime.strptime(row['data_batismo'], '%Y-%m-%d')
                batismo_info = f"Batizado em {data_batismo.strftime('%d/%m/%Y')}"
            else:
                batismo_info = "Não é Batizado"

            # Busca auxiliares do grupo
            cursor.execute("""
                SELECT nome FROM auxiliares WHERE grupo_responsavel = ?
            """, (row['grupo_recitativo'],))
            auxiliares = cursor.fetchall()
            lista_auxiliares = [auxiliar['nome'] for auxiliar in auxiliares]

            jovens.append({
                "id": row['id'],
                "nome": row['nome'],
                "data_nascimento": f"{data_nascimento.strftime('%d/%m/%Y')} - {idade} anos",
                "whatsapp": row['whatsapp'],
                "endereco": row['endereco'],
                "pais": row['pais'],
                "grupo_recitativo": row['grupo_recitativo'],
                "batismo_info": batismo_info,
                "observacoes": row['observacoes'] or "Nenhuma observação",
                "auxiliares": lista_auxiliares
            })

        except ValueError:
            print(f"Erro ao processar jovem com ID {row['id']}")
            continue

    conn.close()
    return render_template('listar_jovens.html', jovens=jovens)


# Editar jovem
@app.route('/editar_jovem/<int:id>', methods=['GET', 'POST'])
def editar_jovem(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        whatsapp = request.form['whatsapp']
        endereco = request.form['endereco']
        pais = request.form['pais']
        grupo_recitativo = request.form['grupo_recitativo']

        cursor.execute('''
            UPDATE jovens
            SET nome = ?, data_nascimento = ?, whatsapp = ?, endereco = ?, pais = ?, grupo_recitativo = ?
            WHERE id = ?
        ''', (nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, id))
        conn.commit()
        conn.close()

        return redirect(url_for('listar_jovens'))

    cursor.execute("SELECT * FROM jovens WHERE id = ?", (id,))
    jovem = cursor.fetchone()
    conn.close()

    return render_template('editar_jovem.html', jovem=jovem)

# Excluir jovem
@app.route('/excluir_jovem/<int:id>', methods=['GET', 'POST'])
def excluir_jovem(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("DELETE FROM jovens WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_jovens'))

    cursor.execute("SELECT nome FROM jovens WHERE id = ?", (id,))
    jovem = cursor.fetchone()
    conn.close()

    return render_template('confirmar_exclusao.html', jovem=jovem, id=id)

def formatar_celular(numero):
    """Formata o número de celular no padrão (DDD) 9XXXX-XXXX"""
    if len(numero) == 11:  # Número com DDD + 9 dígitos
        return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
    elif len(numero) == 10:  # Número com DDD + 8 dígitos
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    else:
        return numero  # Retorna como está se não seguir os padrões
    

# Lista de auxiliares

@app.route('/listar_auxiliares', methods=['GET'])
def listar_auxiliares():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auxiliares ORDER BY nome ASC")
    rows = cursor.fetchall()
    conn.close()

    auxiliares = []
    for row in rows:
        # Processa as datas de forma segura
        data_nascimento = row['data_nascimento']
        data_batismo = row['data_batismo']
        data_apresentacao = row['data_apresentacao']

        # Calcula os tempos apenas se as datas estiverem disponíveis
        tempo_batismo = calcular_tempo(datetime.strptime(data_batismo, '%Y-%m-%d')) if data_batismo else "Não informado"
        tempo_auxiliar = calcular_tempo(datetime.strptime(data_apresentacao, '%Y-%m-%d')) if data_apresentacao else "Não informado"

        auxiliares.append({
            "id": row['id'],
            "nome": row['nome'],
            "grupo_responsavel": row['grupo_responsavel'],
            "whatsapp": formatar_celular(row['whatsapp']),
            "data_nascimento": datetime.strptime(data_nascimento, '%Y-%m-%d').strftime('%d/%m/%Y') if data_nascimento else "Não informado",
            "data_batismo": datetime.strptime(data_batismo, '%Y-%m-%d').strftime('%d/%m/%Y') if data_batismo else "Não informado",
            "data_apresentacao": datetime.strptime(data_apresentacao, '%Y-%m-%d').strftime('%d/%m/%Y') if data_apresentacao else "Não informado",
            "tempo_batismo": tempo_batismo,
            "tempo_auxiliar": tempo_auxiliar,
        })

    return render_template('listar_auxiliares.html', auxiliares=auxiliares)




# Cadastrar auxiliar
@app.route('/cadastro_auxiliares', methods=['GET', 'POST'])
def cadastro_auxiliares():
    if 'logged_in' not in session or session['user_id'] != 0:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        data_nascimento = request.form['data_nascimento']
        grupo_responsavel = request.form['grupo_responsavel']
        whatsapp = request.form['whatsapp']
        data_batismo = request.form['data_batismo']
        data_apresentacao = request.form['data_apresentacao']

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO auxiliares (nome, data_nascimento, grupo_responsavel, whatsapp, data_batismo, data_apresentacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, data_nascimento, grupo_responsavel, whatsapp, data_batismo, data_apresentacao))
        conn.commit()
        conn.close()

        return redirect(url_for('listar_auxiliares'))

    return render_template('cadastro_auxiliares.html')


# Editar auxiliar

@app.route('/editar_auxiliar/<int:id>', methods=['GET', 'POST'])
def editar_auxiliar(id):
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        grupo_responsavel = request.form['grupo_responsavel']
        whatsapp = request.form['whatsapp']
        data_batismo = request.form['data_batismo']
        data_apresentacao = request.form['data_apresentacao']

        cursor.execute("""
            UPDATE auxiliares
            SET nome = ?, grupo_responsavel = ?, whatsapp = ?, data_batismo = ?, data_apresentacao = ?
            WHERE id = ?
        """, (nome, grupo_responsavel, whatsapp, data_batismo, data_apresentacao, id))
        conn.commit()
        conn.close()  # Feche a conexão após salvar as alterações!
        return redirect(url_for('listar_auxiliares'))

    cursor.execute("SELECT * FROM auxiliares WHERE id = ?", (id,))
    auxiliar = cursor.fetchone()
    conn.close()  # Feche a conexão após a consulta!
    return render_template('editar_auxiliar.html', auxiliar=auxiliar)


# excluir auxiliar

@app.route('/excluir_auxiliar/<int:id>', methods=['GET', 'POST'])
def excluir_auxiliar(id):
    if 'logged_in' not in session or session['user_id'] != 0:
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("DELETE FROM auxiliares WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_auxiliares'))

    cursor.execute("SELECT nome FROM auxiliares WHERE id = ?", (id,))
    auxiliar = cursor.fetchone()
    conn.close()

    return render_template('confirmar_exclusao_auxiliar.html', auxiliar=auxiliar, id=id)


# Registrar frequência
@app.route('/controle_frequencia', methods=['GET'])
def controle_frequencia():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    grupo_responsavel = session.get('grupo_responsavel', None)
    conn = db_connection()
    cursor = conn.cursor()

    if grupo_responsavel == 'todos':  # Admin vê todos os grupos
        cursor.execute("""
            SELECT id, nome, grupo_recitativo
            FROM jovens
            ORDER BY nome ASC
        """)
    else:  # Auxiliar vê apenas os jovens de seu grupo
        cursor.execute("""
            SELECT id, nome, grupo_recitativo
            FROM jovens
            WHERE grupo_recitativo = ?
            ORDER BY nome ASC
        """, (grupo_responsavel,))

    pessoas = [{"id": row['id'], "nome": row['nome'], "grupo_recitativo": row['grupo_recitativo']} for row in cursor.fetchall()]
    conn.close()

    return render_template('controle_frequencia.html', pessoas=pessoas, grupo=grupo_responsavel)

@app.route('/relatorios')
def relatorios():
    conn = db_connection()
    cursor = conn.cursor()

    # Exemplo: Obter frequência dos jovens
    cursor.execute("""
        SELECT
            jovens.id, jovens.nome, jovens.grupo_recitativo AS grupo,
            COUNT(CASE WHEN frequencia.presente = 1 THEN 1 END) AS presencas,
            COUNT(CASE WHEN frequencia.presente = 0 THEN 1 END) AS faltas,
            MAX(frequencia.data) AS ultima_frequencia
        FROM jovens
        LEFT JOIN frequencia ON jovens.id = frequencia.jovem_id
        GROUP BY jovens.id
    """)
    rows = cursor.fetchall()

    jovens = []
    alertas = []
    for row in rows:
        total = row['presencas'] + row['faltas']
        frequencia_percentual = (row['presencas'] / total * 100) if total > 0 else 0
        ausencias_consecutivas = row['faltas'] >= 2

        jovem = {
            "id": row['id'],
            "nome": row['nome'],
            "grupo": row['grupo'],
            "frequencia": f"{frequencia_percentual:.1f}%",
            "ultima_frequencia": row['ultima_frequencia'],
        }

        jovens.append(jovem)
        if ausencias_consecutivas:
            alertas.append(jovem)

    conn.close()
    return render_template('relatorios.html', jovens=jovens, alertas=alertas)


@app.route('/relatorios/individual')
def relatorio_individual():
    # Dados para a página
    return render_template('relatorio_individual.html')

@app.route('/relatorios/grupo')
def relatorio_grupo():
    # Dados para a página
    return render_template('relatorio_grupo.html')

@app.route('/relatorios/resumo')
def relatorio_resumo():
    # Dados para a página
    return render_template('relatorio_resumo.html')

@app.route('/exportar-relatorio')
def exportar_relatorio():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            jovens.nome AS Nome, jovens.grupo_recitativo AS Grupo,
            COUNT(CASE WHEN frequencia.presente = 1 THEN 1 END) AS Presenças,
            COUNT(CASE WHEN frequencia.presente = 0 THEN 1 END) AS Faltas
        FROM jovens
        LEFT JOIN frequencia ON jovens.id = frequencia.jovem_id
        GROUP BY jovens.id
    """)
    data = cursor.fetchall()
    conn.close()

    # Converter para DataFrame e gerar Excel
    df = pd.DataFrame(data)
    file_path = 'relatorio_frequencia.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)

    import os
app.secret_key = os.getenv('SECRET_KEY', 'chave_padrao_segura')

def inicializar_banco():
    conn = sqlite3.connect('igreja.db')
    cursor = conn.cursor()

    # Criação da tabela `jovens`
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jovens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            whatsapp TEXT,
            endereco TEXT,
            pais TEXT,
            grupo_recitativo TEXT,
            batizado TEXT,
            data_batismo TEXT,
            observacoes TEXT
        )
    """)

    # Criação de outras tabelas, se necessário
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frequencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jovem_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(jovem_id) REFERENCES jovens(id)
        )
    """)

    conn.commit()
    conn.close()

# Chame a função ao iniciar a aplicação
inicializar_banco()
