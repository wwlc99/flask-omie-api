from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carregar o arquivo .env
load_dotenv()

# Obter as credenciais do banco de dados
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Verificar se todas as variáveis estão configuradas
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise RuntimeError("Credenciais do banco de dados não configuradas no arquivo .env")

# Configuração do Flask
app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Rota para consultar clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    pagina = int(request.args.get('pagina', 1))
    registros_por_pagina = int(request.args.get('registros_por_pagina', 10))
    offset = (pagina - 1) * registros_por_pagina

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Query para listar os clientes com paginação
        cur.execute("""
            SELECT codigo_cliente_omie, nome, email 
            FROM clientes
            ORDER BY nome
            LIMIT %s OFFSET %s
        """, (registros_por_pagina, offset))

        clientes = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(clientes)
    except Exception as e:
        return jsonify({"erro": "Erro ao consultar o banco de dados", "detalhes": str(e)}), 500

# Rota para consultar produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    pagina = int(request.args.get('pagina', 1))
    registros_por_pagina = int(request.args.get('registros_por_pagina', 10))
    offset = (pagina - 1) * registros_por_pagina

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Query para listar os produtos com paginação
        cur.execute("""
            SELECT codigo_produto, descricao, preco
            FROM produtos
            ORDER BY descricao
            LIMIT %s OFFSET %s
        """, (registros_por_pagina, offset))

        produtos = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(produtos)
    except Exception as e:
        return jsonify({"erro": "Erro ao consultar o banco de dados", "detalhes": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)