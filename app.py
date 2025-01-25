import os
import requests
import mysql.connector
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Credenciais da API Omie
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')

# Configuração do banco de dados MySQL
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Função para chamar a API Omie
def chamar_api_omie(endpoint, payload):
    url = f"https://app.omie.com.br/api/v1/geral/{endpoint}/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na API Omie: {response.status_code} - {response.text}")
        return None

# Função para salvar dados no banco de dados
def salvar_no_banco(tabela, dados):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if tabela == "clientes":
            for cliente in dados:
                codigo_cliente = cliente.get("codigo_cliente_omie")
                nome = cliente.get("nome_fantasia")
                email = cliente.get("email", "N/A")

                if not codigo_cliente or not nome:
                    print(f"Cliente inválido ignorado: {cliente}")
                    continue

                cursor.execute(
                    """
                    INSERT INTO clientes (id, nome, email)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nome=%s, email=%s
                    """,
                    (
                        codigo_cliente,
                        nome,
                        email,
                        nome,
                        email,
                    ),
                )
        elif tabela == "produtos":
            for produto in dados:
                codigo_produto = produto.get("codigo_produto")
                descricao = produto.get("descricao")
                preco_unitario = produto.get("preco_unitario", 0.0)

                if not codigo_produto or not descricao:
                    print(f"Produto inválido ignorado: {produto}")
                    continue

                cursor.execute(
                    """
                    INSERT INTO produtos (id, nome, preco)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nome=%s, preco=%s
                    """,
                    (
                        codigo_produto,
                        descricao,
                        preco_unitario,
                        descricao,
                        preco_unitario,
                    ),
                )

        conn.commit()
        print(f"Dados salvos na tabela {tabela} com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")
    finally:
        if conn:
            conn.close()

# Função principal para sincronizar produtos
def sincronizar_produtos(completo=True):
    endpoint = "produtos"
    call = "ListarProdutos" if completo else "ListarProdutosResumido"

    payload = {
        "call": call,
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 50,
                "apenas_importado_api": "N",
                "filtrar_apenas_omiepdv": "N",
            }
        ],
    }

    resposta = chamar_api_omie(endpoint, payload)

    if resposta:
        # Buscar produtos na chave correta
        produtos = resposta.get("produto_servico_cadastro")
        if produtos:
            salvar_no_banco("produtos", produtos)
        else:
            print(f"Nenhum produto encontrado no método {call}.")
    else:
        print("Erro ao chamar a API para sincronizar produtos.")

# Função principal para sincronizar clientes
def sincronizar_clientes():
    endpoint = "clientes"
    payload = {
        "call": "ListarClientes",
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 50
            }
        ],
    }

    resposta = chamar_api_omie(endpoint, payload)
    if resposta:
        clientes = resposta.get("clientes_cadastro")
        if clientes:
            salvar_no_banco("clientes", clientes)
        else:
            print("Nenhum cliente encontrado na resposta da API.")
    else:
        print("Erro ao chamar a API para sincronizar clientes.")

# Função para sincronizar ambos
def sincronizar_dados():
    print("Sincronizando produtos...")
    sincronizar_produtos(completo=True)  # Sincronizar produtos com dados completos
    print("Sincronizando clientes...")
    sincronizar_clientes()

# Executar a sincronização
if __name__ == "__main__":
    sincronizar_dados()