from flask import Flask, request, jsonify  # Importações do Flask
import requests  # Importação da biblioteca para requisições HTTP
from dotenv import load_dotenv  # Carregar variáveis de ambiente do .env
import os  # Trabalhar com variáveis de ambiente

# Carregar o arquivo .env
load_dotenv()

# Obter as credenciais das variáveis de ambiente
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')

# Verificação de segurança: se as credenciais não estiverem configuradas, o sistema para
if not APP_KEY or not APP_SECRET:
    raise RuntimeError("As variáveis 'APP_KEY' e 'APP_SECRET' não estão configuradas no arquivo .env")

# Configuração do Flask
app = Flask(__name__)

# Endpoints da API Omie
url_clientes = "https://app.omie.com.br/api/v1/geral/clientes/"
url_produtos = "https://app.omie.com.br/api/v1/geral/produtos/"

# Rota para listar clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    pagina = request.args.get('pagina', 1)
    registros_por_pagina = request.args.get('registros_por_pagina', 10)

    payload = {
        "call": "ListarClientes",
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [
            {
                "pagina": int(pagina),
                "registros_por_pagina": int(registros_por_pagina)
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url_clientes, json=payload, headers=headers)

    if response.status_code == 200:
        dados = response.json()
        if 'clientes_cadastro' in dados:
            return jsonify(dados['clientes_cadastro'])
        else:
            return jsonify({"erro": "Campo 'clientes_cadastro' não encontrado"}), 400
    else:
        return jsonify({"erro": "Erro na requisição à API Omie", "detalhes": response.text}), 500

# Rota para listar produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    pagina = request.args.get('pagina', 1)
    registros_por_pagina = request.args.get('registros_por_pagina', 50)  # Máximo permitido
    apenas_importado_api = request.args.get('apenas_importado_api', 'N')  # N ou S
    filtrar_apenas_omiepdv = request.args.get('filtrar_apenas_omiepdv', 'N')  # N ou S

    payload = {
        "call": "ListarProdutos",
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [
            {
                "pagina": int(pagina),
                "registros_por_pagina": int(registros_por_pagina),
                "apenas_importado_api": apenas_importado_api,
                "filtrar_apenas_omiepdv": filtrar_apenas_omiepdv
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url_produtos, json=payload, headers=headers)

    if response.status_code == 200:
        dados = response.json()
        if 'produto_servico_listfull_response' in dados:
            return jsonify(dados['produto_servico_listfull_response'])
        else:
            return jsonify({"erro": "Campo 'produto_servico_listfull_response' não encontrado"}), 400
    else:
        return jsonify({"erro": "Erro na requisição à API Omie", "detalhes": response.text}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)