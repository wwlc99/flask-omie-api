import requests
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Inicializar Flask e autenticação
app = Flask(__name__)
auth = HTTPBasicAuth()

# Carregar o arquivo .env
load_dotenv()

# Obter as credenciais da API Omie
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')

# Obter as credenciais de usuário e senha da API local
API_USER = os.getenv('API_USER')
API_PASSWORD = os.getenv('API_PASSWORD')

# Verificação de segurança: se as credenciais não estiverem configuradas
if not APP_KEY or not APP_SECRET:
    raise RuntimeError("As variáveis 'APP_KEY' e 'APP_SECRET' não estão configuradas no arquivo .env")
if not API_USER or not API_PASSWORD:
    raise RuntimeError("As variáveis 'API_USER' e 'API_PASSWORD' não estão configuradas no arquivo .env")

# Configuração da autenticação com Flask HTTPAuth
@auth.verify_password
def verify_password(username, password):
    if username == API_USER and password == API_PASSWORD:
        return username
    return None

# Função auxiliar para chamar a API do Omie
def chamar_api_omie(endpoint, payload):
    url = f"https://app.omie.com.br/api/v1/geral/{endpoint}/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "erro": f"Erro na requisição para a API Omie: {response.status_code}",
            "detalhes": response.text,
        }, response.status_code

# Endpoint para listar produtos
@app.route('/produtos', methods=['GET'])
@auth.login_required
def listar_produtos():
    # Obter a página e registros por página da query string
    pagina = int(request.args.get('pagina', 1))
    registros_por_pagina = int(request.args.get('registros_por_pagina', 50))

    # Parâmetros da requisição
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

    dados = chamar_api_omie("produtos", payload)

    if isinstance(dados, tuple):  # Verifica se ocorreu um erro
        return jsonify(dados[0]), dados[1]

    if 'produto_servico_listfull_response' in dados:
        registros = dados['produto_servico_listfull_response']
        if registros:
            return jsonify(registros)
        else:
            return jsonify({"mensagem": "Nenhum produto encontrado."}), 404
    else:
        return jsonify({
            "erro": "Campo 'produto_servico_listfull_response' não encontrado.",
            "resposta": dados
        }), 500

# Endpoint para listar clientes
@app.route('/clientes', methods=['GET'])
@auth.login_required
def listar_clientes():
    # Obter a página e registros por página da query string
    pagina = int(request.args.get('pagina', 1))
    registros_por_pagina = int(request.args.get('registros_por_pagina', 50))

    # Parâmetros da requisição
    payload = {
        "call": "ListarClientes",
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [
            {
                "pagina": pagina,
                "registros_por_pagina": registros_por_pagina
            }
        ]
    }

    dados = chamar_api_omie("clientes", payload)

    if isinstance(dados, tuple):  # Verifica se ocorreu um erro
        return jsonify(dados[0]), dados[1]

    if 'clientes_cadastro' in dados:
        registros = dados['clientes_cadastro']
        if registros:
            return jsonify(registros)
        else:
            return jsonify({"mensagem": "Nenhum cliente encontrado."}), 404
    else:
        return jsonify({
            "erro": "Campo 'clientes_cadastro' não encontrado.",
            "resposta": dados
        }), 500

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)