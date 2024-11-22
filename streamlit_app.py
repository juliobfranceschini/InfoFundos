import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Configurar exibição para melhor visualização
pd.set_option('display.max_columns', None)  # Mostrar todas as colunas

# Função para baixar e processar os dados de um determinado ano e mês
def processar_dados(ano, mes):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/lamina_fi_{ano}{mes:02}.zip'
    response = requests.get(url)

    if response.status_code == 200:
        try:
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
                dataframes = []
                for file_name in arquivo_zip.namelist():
                    try:
                        df = pd.read_csv(
                            arquivo_zip.open(file_name),
                            sep=';',
                            encoding='ISO-8859-1',
                            on_bad_lines='skip'
                        )
                        dataframes.append(df)
                    except Exception as e:
                        st.write(f"Erro ao processar {file_name}: {e}")
                if dataframes:
                    return pd.concat(dataframes, ignore_index=True)
                else:
                    st.write("Nenhum dado válido encontrado no arquivo ZIP.")
                    return None
        except zipfile.BadZipFile:
            st.write("Erro: Arquivo ZIP inválido.")
            return None
    else:
        st.write(f"Erro ao baixar dados de {ano}-{mes:02}. URL: {url}")
        return None

# Função para filtrar os dados de um CNPJ específico
def filtrar_por_cnpj(dados, cnpj):
    dados_cnpj = dados[dados['CNPJ_FUNDO_CLASSE'] == cnpj]

    if dados_cnpj.empty:
        return None
    else:
        dados_cnpj_unicos = dados_cnpj.drop_duplicates(subset=['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'DENOM_SOCIAL'])
        colunas_relevantes = [
            'CNPJ_FUNDO_CLASSE', 'DENOM_SOCIAL', 'DT_COMPTC', 'NM_FANTASIA',
            'PUBLICO_ALVO', 'INDICE_REFER', 'PR_PL_ALAVANC', 'RISCO_PERDA',
            'INVEST_INICIAL_MIN', 'VL_PATRIM_LIQ', 'TAXA_ADM', 'TAXA_ADM_MIN',
            'TAXA_ADM_MAX', 'TAXA_PERFM', 'PR_RENTAB_FUNDO_5ANO',
        ]
        dados_filtrados = dados_cnpj_unicos[colunas_relevantes]
        novos_nomes = {
            'CNPJ_FUNDO_CLASSE': 'CNPJ Fundo',
            'DENOM_SOCIAL': 'Nome Social',
            'DT_COMPTC': 'Data competência',
            'NM_FANTASIA': 'Nome fantasia',
            'PUBLICO_ALVO': 'Público-Alvo',
            'INDICE_REFER': 'Índice Referência',
            'PR_PL_ALAVANC': 'Limite alavancagem',
            'RISCO_PERDA': 'Possibilidade perdas patrimoniais',
            'INVEST_INICIAL_MIN': 'Investimento inicial mínimo',
            'VL_PATRIM_LIQ': 'PL',
            'TAXA_ADM': 'Taxa ADM',
            'TAXA_ADM_MIN': 'Taxa ADM Min',
            'TAXA_ADM_MAX': 'Taxa ADM Max',
            'TAXA_PERFM': 'Taxa Performance',
            'PR_RENTAB_FUNDO_5ANO': 'Rentabilidade acumulada 5 anos ',
        }
        return dados_filtrados.rename(columns=novos_nomes)

# Função principal do Streamlit
def main():
    st.title("Dashboard de Informações de Fundos de Investimento")
    st.write("Carregue os dados uma vez e consulte pelo CNPJ do fundo.")

    # Controle para armazenar os dados carregados
    if "dados_fundos_total" not in st.session_state:
        st.session_state["dados_fundos_total"] = None

    # Botão para carregar os dados
    if st.button("Carregar Dados"):
        st.write("Baixando e processando os dados. Aguarde...")
        todos_dados = []
        anos = ['2024']
        meses = range(1, 13)

        for ano in anos:
            for mes in meses:
                df = processar_dados(ano, mes)
                if df is not None:
                    todos_dados.append(df)

        if todos_dados:
            st.session_state["dados_fundos_total"] = pd.concat(todos_dados, ignore_index=True)
            st.write("Dados carregados com sucesso!")
        else:
            st.write("Nenhum dado foi processado.")

    # Entrada de CNPJ
    cnpj_input = st.text_input("Digite o CNPJ do Fundo", "")

    # Botão para buscar o CNPJ
    if st.button("Buscar CNPJ"):
        if st.session_state["dados_fundos_total"] is not None:
            st.write(f"Buscando informações para o CNPJ: {cnpj_input}")
            dados_cnpj = filtrar_por_cnpj(st.session_state["dados_fundos_total"], cnpj_input)
            if dados_cnpj is not None:
                st.write("Informações encontradas:")
                st.dataframe(dados_cnpj)
            else:
                st.write(f"Nenhum dado encontrado para o CNPJ: {cnpj_input}")
        else:
            st.write("Por favor, carregue os dados primeiro.")

# Executar o Streamlit
if __name__ == "__main__":
    main()
