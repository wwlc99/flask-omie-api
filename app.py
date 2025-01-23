import requests
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import mysql.connector
import os

# Inicializa o app Flask e a autenticação básica
app = Flask(__name__)
auth = HTTPBasicAuth()

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Credenciais da API Omie
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')

# Credenciais para autenticação local da API
API_USER = os.getenv('API_USER')
API_PASSWORD = os.getenv('API_PASSWORD')

# Configuração para conexão com o banco de dados MySQL
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Verifica credenciais de usuário e senha para autenticação
@auth.verify_password
def verify_password(username, password):
    if username == API_USER and password == API_PASSWORD:
        return username
    return None

# Função para fazer requisições à API Omie
def chamar_api_omie(endpoint, payload):
    url = f"https://app.omie.com.br/api/v1/geral/{endpoint}/"  # URL da API
    headers = {"Content-Type": "application/json"}  # Cabeçalhos da requisição
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:  # Verifica sucesso da requisição
        return response.json()  # Retorna os dados em formato JSON
    else:
        print(f"Erro na API: {response.status_code}, Detalhes: {response.text}")
        return {
            "erro": f"Erro na API: {response.status_code}",
            "detalhes": response.text,
        }, response.status_code

# Função para salvar dados no banco de dados
def salvar_no_banco(tabela, dados):
    conn = None
    cursor = None
    try:
        # Conecta ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if tabela == "clientes":
            # Salva dados de clientes no banco
            for cliente in dados:
                print(f"Salvando cliente: {cliente}")
                cursor.execute(
                    """
                    INSERT INTO clientes (id, nome, email)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nome=%s, email=%s
                    """,
                    (
                        cliente.get("codigo_cliente_omie"),
                        cliente.get("nome_fantasia"),
                        cliente.get("email"),
                        cliente.get("nome_fantasia"),
                        cliente.get("email"),
                    ),
                )

        if tabela == "produtos":
            # Salva dados de produtos no banco
            for produto in dados:
                print(f"Salvando produto: {produto}")
                cursor.execute(
                    """
                    INSERT INTO produtos (id, nome, preco)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nome=%s, preco=%s
                    """,
                    (
                        produto.get("codigo_produto"),
                        produto.get("descricao"),
                        produto.get("preco_unitario"),
                        produto.get("descricao"),
                        produto.get("preco_unitario"),
                    ),
                )

        conn.commit()  # Confirma as alterações no banco
    except Exception as e:
        if conn:
            conn.rollback()  # Desfaz alterações em caso de erro
        print(f"Erro no banco: {e}")
        raise e
    finally:
        # Fecha a conexão com o banco de dados
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Endpoint para listar e sincronizar clientes
@app.route('/clientes', methods=['GET'])
@auth.login_required
def listar_clientes():
    try:
        # Obtém parâmetros da requisição
        pagina = int(request.args.get('pagina', 1))
        registros_por_pagina = int(request.args.get('registros_por_pagina', 50))
        payload = {
            "call": "ListarClientes",
            "app_key": APP_KEY,
            "app_secret": APP_SECRET,
            "param": [{"pagina": pagina, "registros_por_pagina": registros_por_pagina}]
        }
        # Chama a API do Omie
        dados = chamar_api_omie("clientes", payload)
        if isinstance(dados, tuple):  # Verifica se houve erro
            return jsonify(dados[0]), dados[1]
        if 'clientes_cadastro' in dados:
            registros = dados['clientes_cadastro']
            print(f"Clientes recebidos: {registros}")
            salvar_no_banco("clientes", registros)  # Salva no banco
            return jsonify({"mensagem": "Clientes sincronizados com sucesso."}), 200
        else:
            return jsonify({"erro": "Estrutura inesperada da API."}), 500
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"erro": f"Erro inesperado: {e}"}), 500

# Endpoint para listar e sincronizar produtos
@app.route('/produtos', methods=['GET'])
@auth.login_required
def listar_produtos():
    try:
        # Obtém parâmetros da requisição
        pagina = int(request.args.get('pagina', 1))
        registros_por_pagina = int(request.args.get('registros_por_pagina', 50))

        print(f"Sincronizando produtos: página={pagina}, registros_por_pagina={registros_por_pagina}")

        payload = {
            "call": "ListarProdutos",
            "app_key": APP_KEY,
            "app_secret": APP_SECRET,
            "param": [
                {
                    "pagina": pagina,
                    "registros_por_pagina": registros_por_pagina,
                    "apenas_importado_api": "N",
                    "filtrar_apenas_omiepdv": "N"
                }
            ]
        }

        # Chama a API do Omie
        dados = chamar_api_omie("produtos", payload)
        print(f"Resposta completa da API Omie para produtos: {dados}")

        if isinstance(dados, tuple):  # Verifica se ocorreu um erro
            return jsonify(dados[0]), dados[1]

        if 'produto_servico_listfull_response' in dados:
            registros = dados['produto_servico_listfull_response']
            print(f"Produtos recebidos: {registros}")
            if registros:
                salvar_no_banco("produtos", registros)  # Salva no banco
                return jsonify({"mensagem": "Produtos sincronizados com sucesso."}), 200
            else:
                print("Nenhum produto encontrado.")
                return jsonify({"mensagem": "Nenhum produto encontrado."}), 404
        else:
            print(f"Campo 'produto_servico_listfull_response' não encontrado. Resposta completa: {dados}")
            return jsonify({
                "erro": "Estrutura inesperada da API.",
                "resposta": dados
            }), 500
    except Exception as e:
        print(f"Erro inesperado no endpoint /produtos: {e}")
        return jsonify({"erro": f"Erro inesperado no servidor: {e}"}), 500

# Inicia o servidor Flask na porta 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)