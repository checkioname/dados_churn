# -*- coding: utf-8 -*-
"""limpeza_churn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IiYTmrK3drxfxYHCQCu-ojxw16UnXVpp

Fazendo a limpeza dos dados churn de uma certa empresa para o uso futuro em um modelo de ml

-Churn é um termo utilizado para se referir à taxa de cancelamento de clientes em um determinado período de tempo. Em outras palavras, é a porcentagem de clientes que deixam de usar um produto ou serviço em um determinado período.
"""

import pandas as pd

url ='https://caelum-online-public.s3.amazonaws.com/2929-pandas/dataset-telecon.json'

dados_churn = pd.read_json(url)

from pandas.io.json import json_normalize
#Normalizando dados json

dados_churn['conta'][0]

pd.json_normalize(dados_churn['conta']).head()

"""Como normalizar todas as colunas? Normalizar e concatenar todas as colunas

#**TRANSFORMANDO DADOS EM TABELAS**
"""

import urllib.request, json

with urllib.request.urlopen(url) as f:
    json_bruto = json.load(f)

dados_normalizados = pd.json_normalize(json_bruto)

dados_normalizados.head()

#verificar os tipos e corrigir futuramente
dados_normalizados.info()

#dados_normalizados['conta.cobranca.Total'] = dados_normalizados['conta.cobranca.Total'].astype('float')

# Como tratar as linhas com espaços vazios? primeiro retornar as linhas
dados_normalizados[dados_normalizados['conta.cobranca.Total'] == ' '][
    ['cliente.tempo_servico','conta.contrato','conta.cobranca.mensal','conta.cobranca.Total']
]

# Atribuir valores a essa coluna, no nosso caso o valor total é a duração do contrato * o valor mensal
idx = dados_normalizados[dados_normalizados['conta.cobranca.Total'] == ' '].index

dados_normalizados.loc[idx,'conta.cobranca.Total'] = dados_normalizados.loc[idx,'conta.cobranca.mensal'] * 24

dados_normalizados.loc[idx,'cliente.tempo_servico'] = 24

dados_normalizados.loc[idx][
    ['cliente.tempo_servico','conta.contrato','conta.cobranca.mensal','conta.cobranca.Total']
]

dados_normalizados['conta.cobranca.Total'] = dados_normalizados['conta.cobranca.Total'].astype(float)
dados_normalizados.info()

#verificar dados vazios
dados_normalizados.query("Churn == ''")

#Salvar uma copia do df sem os dados vazios
df = dados_normalizados[dados_normalizados['Churn'] != ''].copy()

# ajustar o index
df.reset_index(inplace=True,drop=True)

# Dropar os valores duplicados
df.drop_duplicates(inplace=True)
df.duplicated().sum()

#tratar dados nulos
df.isna().sum()

df['cliente.tempo_servico'].isna().sum()

filtro = df['cliente.tempo_servico'].isna()
df[filtro][['cliente.tempo_servico','conta.cobranca.mensal','conta.cobranca.Total']]

import numpy as np

#Completar a celula que tem valores vazios
df['cliente.tempo_servico'].fillna(
  np.ceil(
      df[filtro]['conta.cobranca.mensal'] / df[filtro]['conta.cobranca.Total']
  ),inplace=True
)

df.isna().sum()

# dropar as amostras das colunas conta.contrato , conta.faturamente_eletronico , conta.metodo_pagamento
# Salvar outro df independente

df_clean = df.dropna(subset=['conta.contrato', 'conta.faturamente_eletronico', 'conta.metodo_pagamento']).copy()
df_clean.reset_index(inplace=True,drop=True)

df_clean.isna().sum()


import seaborn as sns
sns.boxplot(x=df_clean['cliente.tempo_servico'])

# Porque ficou tao cagado?? Vamos tirar esses outliers
q1 = df_clean['cliente.tempo_servico'].quantile(.25)
q3 = df_clean['cliente.tempo_servico'].quantile(.75)

iqr = q3 - q1
limite_inferior = q1 - 1.5*iqr
limite_superior = q3 + 1.5*iqr

# Pegar os valores menores que o limite inferior ou maiores que o limite superior (os outliers)
outliers = (df_clean['cliente.tempo_servico'] < limite_inferior) | (df_clean['cliente.tempo_servico'] > limite_superior)

df_clean[outliers]['cliente.tempo_servico']

# corrigindo os outliers
df_clean.loc[outliers,'cliente.tempo_servico'] = np.ceil(
    df_clean.loc[outliers,'conta.cobranca.Total']/
    df_clean.loc[outliers,'conta.cobranca.mensal']
)

sns.boxplot(x=df_clean['cliente.tempo_servico'])

#Alguns valores continuaram errados. Nossos dados estao incorretos? Hora de dropar essas amostras?
# Para dropar vamos atualizar nossa variavel dos outliers

q1 = df_clean['cliente.tempo_servico'].quantile(.25)
q3 = df_clean['cliente.tempo_servico'].quantile(.75)

iqr = q3 - q1
limite_inferior = q1 - 1.5*iqr
limite_superior = q3 + 1.5*iqr

index_outliers = (df_clean['cliente.tempo_servico'] < limite_inferior) | (df_clean['cliente.tempo_servico'] > limite_superior)
df_clean[index_outliers]

df_clean = df_clean[~index_outliers]
df_clean.reset_index(drop=True,inplace=True)
df_clean

sns.boxplot(x=df_clean['cliente.tempo_servico'])

kaggle datasets download -d rm1000/fortune-500-companies