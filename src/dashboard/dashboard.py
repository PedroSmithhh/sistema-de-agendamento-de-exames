import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
from datetime import datetime

# Carregar os dados
@st.cache_data
def load_data():
    try:
        estruturado = pd.read_csv(r'data\processed\estruturado_processado.csv', dtype={'CPF': str})
        nao_estruturado = pd.read_csv(r'data\processed\nao_estruturado_processado.csv', dtype={'CPF': str})
        resultado = pd.read_csv(r'data\processed\resultado_processado.csv', dtype={'CPF': str})
        
        for df in [estruturado, nao_estruturado, resultado]:
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col].fillna('', inplace=True)
                else:
                    df[col].fillna(0, inplace=True)
        
        st.success("Dados carregados com sucesso!")
        return estruturado, nao_estruturado, resultado
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Carregar os dados
estruturado, nao_estruturado, resultado = load_data()

# Interface
st.sidebar.header('Filtros de Consulta')
visao = st.sidebar.radio('Selecione a Visão:', 
                        ('Estruturado', 'Não Estruturado', 'Resultado Processado'))

# Opção para selecionar tipo de filtro de data
filtro_data_tipo = st.sidebar.radio('Tipo de Filtro de Data:', ('Intervalo de Datas', 'Data Específica'))

if filtro_data_tipo == 'Intervalo de Datas':
    data_inicio = st.sidebar.date_input('Data Início', datetime(2020, 1, 1))
    data_fim = st.sidebar.date_input('Data Fim', datetime.today())
    data_especifica = None
else:
    data_especifica = st.sidebar.date_input('Selecione a Data', datetime(2020, 1, 1))
    data_inicio = data_especifica
    data_fim = data_especifica

# Converter datas para datetime
data_inicio_dt = pd.to_datetime(data_inicio.strftime('%Y-%m-%d'), format='%Y-%m-%d')
data_fim_dt = pd.to_datetime(data_fim.strftime('%Y-%m-%d'), format='%Y-%m-%d')

# Função de filtro
def filter_dates(df, data_inicio_dt, data_fim_dt):
    if 'DATA' not in df.columns:
        st.warning("Coluna 'DATA' não encontrada!")
        return df
    
    df_copy = df.copy()
    df_copy['DATA'] = pd.to_datetime(df_copy['DATA'], format='%Y-%m-%d', errors='coerce')
    
    df_filtered = df_copy[(df_copy['DATA'] >= data_inicio_dt) & (df_copy['DATA'] <= data_fim_dt)]
    
    return df_filtered

# Função para criar tabela de tipos de exames e quantidades
def cria_tabela_exame(df):
    if 'exame_resultado' not in df.columns:
        st.warning("Coluna 'exame_resultado' não encontrada!")
        return
    
    # Contar ocorrências de cada tipo de exame
    exam_counts = df['exame_resultado'].value_counts().reset_index()
    exam_counts.columns = ['Tipo de Exame', 'Quantidade']
    
    # Exibir a tabela
    st.write("### Quantidade por Tipo de Exame:")
    st.write(exam_counts)

# Processamento
if visao == 'Estruturado':
    st.write("Dados Estruturados (5 primeiras linhas):", estruturado.head())
    df = filter_dates(estruturado, data_inicio_dt, data_fim_dt)
    st.header('Análise dos Dados Estruturados')
    
    if filtro_data_tipo == 'Data Específica':
        st.subheader(f"Exames Solicitados em {data_especifica.strftime('%d/%m/%Y')}")
        st.write(f"### Total de Exames: {len(df)}")
    else: 
        st.subheader(f'Exames Solicitados entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}')
        st.write(f'### Total de Exames: {len(df)}')
    
    if 'SOLICITANTE' in df.columns:
        st.write("### Exames por Solicitante:")
        st.write(df['SOLICITANTE'].value_counts())
    else:
        st.warning("Coluna 'SOLICITANTE' não encontrada!")

    # Adicionar tabela de tipos de exames e quantidades
    cria_tabela_exame(df)

elif visao == 'Não Estruturado':
    st.write("Dados Não Estruturados (5 primeiras linhas):", nao_estruturado.head())
    df = filter_dates(nao_estruturado, data_inicio_dt, data_fim_dt)
    st.header('Análise dos Dados Não Estruturados')
    
    if filtro_data_tipo == 'Data Específica':
        st.subheader(f"Exames Solicitados em {data_especifica.strftime('%d/%m/%Y')}")
        st.write(f"### Total de Exames: {len(df)}")
    else: 
        st.subheader(f'Exames Solicitados entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}')
        st.write(f'### Total de Exames: {len(df)}')

    if 'SOLICITANTE' in df.columns:
        st.write("### Exames por Solicitante:")
        st.write(df['SOLICITANTE'].value_counts())

    cria_tabela_exame(df)

elif visao == 'Resultado Processado':
    st.write("Resultado Processado (5 primeiras linhas):", resultado.head())
    df = filter_dates(resultado, data_inicio_dt, data_fim_dt)
    st.header('Análise dos Resultados Processados')
    
    if filtro_data_tipo == 'Data Específica':
        st.subheader(f"Exames Processados em {data_especifica.strftime('%d/%m/%Y')}")
        st.write(f"### Total de Exames: {len(df)}")
    else: 
        st.subheader(f'Exames Solicitados entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}')
        st.write(f'### Total de Exames: {len(df)}')

    if 'SOLICITANTE' in df.columns:
        st.write("### Exames por Solicitante:")
        st.write(df['SOLICITANTE'].value_counts())

    cria_tabela_exame(df)
