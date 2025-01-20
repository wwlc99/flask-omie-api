import requests
import pandas as pd

# Credenciais
APP_KEY = '38333295000'
APP_SECRET = 'fed2163e2e8dccb53ff914ce9e2f1258'

# Endpoint da API
url = "https://app.omie.com.br/api/v1/geral/produtos/"

# Parâmetros da requisição
payload = {
    "call": "ListarProdutos",
    "app_key": APP_KEY,
    "app_secret": APP_SECRET,
    "param": [
        {
            "pagina": 1,
            "registros_por_pagina": 50,  # Máximo de registros por página
            "apenas_importado_api": "N",  # N para listar tudo, S para listar apenas os importados pela API
            "filtrar_apenas_omiepdv": "N"  # N para listar tudo, S para listar apenas produtos OmiePDV
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
    print("Resposta da API:", dados)  # Exibe o JSON completo retornado

    # Verifica se o campo esperado está presente
    if 'produto_servico_listfull_response' in dados:
        registros = dados['produto_servico_listfull_response']
        if registros:  # Verifica se há registros
            df = pd.DataFrame(registros)
            print(df.head())  # Visualiza os primeiros registros (opcional)
            df.to_csv("produtos.csv", index=False)
            print("Dados salvos em 'produtos.csv'.")
        else:
            print("Nenhum produto encontrado na resposta.")
    else:
        print("Campo 'produto_servico_listfull_response' não encontrado na resposta da API.")
else:
    print(f"Erro na requisição: {response.status_code}")
    print(response.text)
