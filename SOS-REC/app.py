# Importação de bibliotecas necessárias
from flask import Flask, request, redirect, render_template, jsonify, url_for, session, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
import requests  # Para previsão do tempo
from bs4 import BeautifulSoup
from flask import jsonify

# Inicialização do aplicativo Flask
app = Flask(__name__)
app.secret_key = 'a3f9c4b7e6d2f8a9c1e0b4d3f7a6c5e1'

# Configurações do servidor de e-mail SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'jonisvitor167@gmail.com'
SMTP_PASSWORD = 'vxng qxdb pebj ndxz'

# Configurações de conexão com o banco de dados PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'documento',
    'user': 'postgres',
    'password': '12345',
    'port': 5432
}

# Configurações para previsão do tempo (OpenWeatherMap)
WEATHER_API_KEY = '58246719fba798dc554e47bee5da40ea'
WEATHER_CITY = 'Recife'
WEATHER_URL = f'https://api.openweathermap.org/data/2.5/weather?q={WEATHER_CITY}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br'

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Conectado ao banco de dados com sucesso!")
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

# Página inicial — login
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('principal'))
    return render_template('index.html')

# Página principal — só acessa se logado
@app.route('/principal')
def principal():
    if 'usuario' not in session:
        flash("Por favor, faça login para acessar esta página.", "warning")
        return redirect(url_for('index'))
    usuario = session['usuario']
    return render_template('principal.html', usuario=usuario)

# Login — processa formulário
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        flash("Por favor, preencha email e senha.", "warning")
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT nome FROM usuario WHERE email = %s AND senha = %s;", (email, senha))
            result = cur.fetchone()
            cur.close()
            if result:
                session['usuario'] = result[0]
                flash(f"Bem-vindo, {result[0]}!", "success")
                print(f"Usuário {result[0]} logado com sucesso.")
                return redirect(url_for('principal'))
            else:
                flash("Login inválido. Verifique email e senha.", "danger")
                print("Login inválido.")
        except Exception as e:
            print("Erro ao realizar login:", e)
            flash("Erro interno ao tentar realizar login.", "danger")
        finally:
            conn.close()
    return redirect(url_for('index'))

# Logout
@app.route('/logout')
def logout():
    session.clear()  # Remove todos os dados da sessão
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('index'))

# Cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Adicionar usuário
@app.route('/add', methods=['POST'])
def add_usuario():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    telefone = request.form.get('telefone')
    endereco = request.form.get('endereco')
    numeroCasa = request.form.get('numeroCasa')
    dataNascimento = request.form.get('dataNascimento')
    sexo = request.form.get('sexo')
    senha = request.form.get('senha')
    email = request.form.get('email')

    if not all([nome, cpf, telefone, endereco, numeroCasa, dataNascimento, sexo, senha, email]):
        flash("Por favor, preencha todos os campos.", "warning")
        return redirect(url_for('cadastro'))

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO usuario (nome, cpf, telefone, endereco, numeroCasa, dataNascimento, sexo, senha, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cpf) DO NOTHING;
            """, (nome, cpf, telefone, endereco, numeroCasa, dataNascimento, sexo, senha, email))
            conn.commit()
            cur.close()
            flash("Cadastro realizado com sucesso! Faça login.", "success")
            print(f"Usuário {nome} cadastrado com sucesso!")
        except Exception as e:
            print("Erro ao adicionar usuário:", e)
            flash("Erro ao cadastrar usuário.", "danger")
        finally:
            conn.close()
    return redirect(url_for('index'))

# Enviar alerta por email
@app.route('/alerta', methods=['POST'])
def alerta():
    data = request.get_json()
    mensagem = data.get('mensagem', 'Alerta recebido!')

    contatos = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT email FROM usuario WHERE email IS NOT NULL;")
            contatos = [row[0] for row in cur.fetchall()]
            cur.close()
        except Exception as e:
            print("Erro ao buscar emails:", e)
        finally:
            conn.close()

    enviar_email(mensagem, contatos)
    return jsonify({"status": "Email enviado"}), 200

# Função para enviar e-mails
def enviar_email(mensagem, contatos):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
    except Exception as e:
        print(f"Erro ao conectar SMTP: {e}")
        return

    for email in contatos:
        try:
            msg = MIMEMultipart()
            msg['From'] = f"SOS-REC Alerta <{SMTP_USER}>"
            msg['To'] = email
            msg['Subject'] = '⚠️ Alerta do Sistema ⚠️'
            msg.attach(MIMEText(mensagem, 'plain'))
            server.sendmail(SMTP_USER, email, msg.as_string())
            print(f"Email enviado para {email}")
        except Exception as e:
            print(f"Erro ao enviar para {email}: {e}")

    server.quit()

# Receber distância
@app.route('/distancia', methods=['POST'])
def receber_distancia():
    data = request.get_json()
    if not data or 'distancia' not in data:
        return jsonify({"erro": "JSON inválido. Envie no formato: {'distancia': valor}"}), 400

    try:
        valor = float(data['distancia'])
    except ValueError:
        return jsonify({"erro": "Valor de distância inválido, deve ser numérico"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO distancias (valor) VALUES (%s);", (valor,))
            conn.commit()
            cur.close()
            print(f"Distância {valor} salva com sucesso.")
        except Exception as e:
            print("Erro ao salvar distância:", e)
            return jsonify({"erro": "Erro interno ao salvar"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"erro": "Falha na conexão com o banco de dados"}), 500

    return jsonify({"status": "Distância salva com sucesso"}), 201

# Retornar últimas distâncias (dados para o gráfico)
@app.route('/distancias')
def get_distancias():
    conn = get_db_connection()
    dados = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT timestamp, valor FROM distancias ORDER BY timestamp DESC LIMIT 10;")
            rows = cur.fetchall()
            dados = [{'timestamp': row[0].isoformat(), 'valor': row[1]} for row in rows]
            cur.close()
        except Exception as e:
            print("Erro ao buscar dados distancias:", e)
        finally:
            conn.close()
    return jsonify(dados)

# Previsão do tempo
@app.route('/previsao_tempo')
def previsao_tempo():
    try:
        response = requests.get(WEATHER_URL)
        response.raise_for_status()
        data = response.json()

        resultado = {
            'temperatura': round(data['main']['temp']),
            'condicao': data['weather'][0]['description'].capitalize(),
            'humidade': data['main']['humidity']
        }
        return jsonify(resultado)
    except Exception as e:
        print("Erro ao obter previsão do tempo:", e)
        return jsonify({'erro': 'Não foi possível obter a previsão', 'detalhe': str(e)}), 500
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
