import requests
import pandas as pd  # Certifique-se de importar pandas aqui

# Credenciais
APP_KEY = '38333295000'
APP_SECRET = 'fed2163e2e8dccb53ff914ce9e2f1258'

# Endpoint da API
url = "https://app.omie.com.br/api/v1/geral/clientes/"

# Parâmetros da requisição
payload = {
    "call": "ListarClientes",
    "app_key": APP_KEY,
    "app_secret": APP_SECRET,
    "param": [
        {
            "pagina": 1,
            "registros_por_pagina": 10
        }
    ]
}

# Cabeçalhos
headers = {"Content-Type": "application/json"}

# Fazendo a requisição
response = requests.post(url, json=payload, headers=headers)

# Verificando o resultado da requisição
if response.status_code == 200:
    print("Dados retornados com sucesso!")
    
    # Pegando os dados principais
    dados = response.json()
    
    if 'clientes_cadastro' in dados:
        registros = dados['clientes_cadastro']
        if registros:  # Verifica se há registros
            df = pd.DataFrame(registros)
            print(df.head())  # Visualiza os primeiros registros (opcional)
            df.to_csv("clientes.csv", index=False)
            print("Dados salvos em 'clientes.csv'.")
        else:
            print("Nenhum registro encontrado na resposta.")
    else:
        print("Campo 'clientes_cadastro' não encontrado na resposta da API.")
else:
    print(f"Erro na requisição: {response.status_code}")
    print(response.text)
