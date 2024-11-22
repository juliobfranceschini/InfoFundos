import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Configurar exibição para melhor visualização
pd.set_option('display.max_columns', None)  # Mostrar todas as colunas

# Função para baixar e processar os dados de um determinado ano e mês
@st.cache_data
def carregar_dados():
    st.write("Baixando e processando os dados. Isso pode levar alguns minutos...")
    todos_dados = []
    anos = ['2024']
    meses = range(1, 13)

    for ano in anos:
        for mes in meses:
            url = f'https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/lamina_fi_{ano}{mes:02}.zip'
            response = requests.get(url)

            if response.status_code == 200:
                try:
                    with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
                        for file_name in arquivo_zip.namelist():
                            try:
                                df = pd.read_csv(
                                    arquivo_zip.open(file_name),
                                    sep=';',
                                    encoding='ISO-8859-1',
                                    on_bad_lines='skip'
                                )
                                todos_dados.append(df)
                            except Exception as e:
                                st.write(f"Erro ao processar {file_name}: {e}")
                except zipfile.BadZipFile:
                    st.write(f"Erro: Arquivo ZIP inválido para {ano}-{mes:02}.")
    
    if todos_dados:
        return pd.concat(todos_dados, ignore_index=True)
    else:
        return None

# Função para filtrar os dados de um CNPJ específico
def filtrar_por_cnpj(dados, cnpj):
    # Filtrar pelos dados do CNPJ fornecido
    dados_cnpj = dados[dados['CNPJ_FUNDO_CLASSE'] == cnpj]

    if dados_cnpj.empty:
        return None
    else:
        # Converter a coluna de data para o formato datetime para comparação
        dados_cnpj['DT_COMPTC'] = pd.to_datetime(dados_cnpj['DT_COMPTC'], format='%Y-%m-%d', errors='coerce')

        # Filtrar o registro mais recente
        dados_mais_recente = dados_cnpj.sort_values(by='DT_COMPTC', ascending=False).iloc[0]

        # Selecionar as colunas relevantes
        colunas_relevantes = {
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
        
        # Renomear colunas e substituir valores ausentes
        dados_filtrados = dados_mais_recente[colunas_relevantes.keys()].rename(index=colunas_relevantes)
        return dados_filtrados.fillna("-")  # Substituir NaN por traço

# Função principal do Streamlit
def main():
    st.title("Dashboard de Informações de Fundos de Investimento")
    st.write("O download dos dados será feito apenas uma vez. Depois, você poderá consultar rapidamente os CNPJs.")

    # Botão para carregar os dados
    if st.button("Carregar Dados"):
        dados_fundos_total = carregar_dados()
        if dados_fundos_total is not None:
            st.session_state["dados_fundos_total"] = dados_fundos_total
            st.write("Dados carregados com sucesso!")
        else:
            st.write("Falha ao carregar os dados.")

    # Verificar se os dados estão carregados
    if "dados_fundos_total" in st.session_state:
        # Entrada de CNPJ
        cnpj_input = st.text_input("Digite o CNPJ do Fundo", "")

        # Botão para buscar o CNPJ
        if st.button("Buscar CNPJ"):
            st.write(f"Buscando informações para o CNPJ: {cnpj_input}")
            dados_cnpj = filtrar_por_cnpj(st.session_state["dados_fundos_total"], cnpj_input)
            if dados_cnpj is not None:
                st.write("### Informações encontradas:")
                
                # Exibindo os dados de forma mais visual
                st.write(f"#### Nome Fantasia: {dados_cnpj['Nome fantasia']}")
                st.write(f"**CNPJ Fundo:** {dados_cnpj['CNPJ Fundo']}")
                st.write(f"**Nome Social:** {dados_cnpj['Nome Social']}")
                st.write(f"**Público-Alvo:** {dados_cnpj['Público-Alvo']}")
                st.write(f"**Data Competência:** {dados_cnpj['Data competência'].strftime('%d/%m/%Y') if dados_cnpj['Data competência'] != '-' else '-'}")
                st.write(f"**Índice Referência:** {dados_cnpj['Índice Referência']}")
                st.write(f"**Limite Alavancagem:** {dados_cnpj['Limite alavancagem']}")
                st.write(f"**Possibilidade de Perdas Patrimoniais:** {dados_cnpj['Possibilidade perdas patrimoniais']}")
                st.write(f"**Investimento Inicial Mínimo:** R$ {dados_cnpj['Investimento inicial mínimo']}")
                st.write(f"**PL:** R$ {dados_cnpj['PL']}")
                st.write(f"**Taxa ADM:** {dados_cnpj['Taxa ADM']}%")
                st.write(f"**Taxa Performance:** {dados_cnpj['Taxa Performance']}%")
                st.write(f"**Rentabilidade acumulada em 5 anos:** {dados_cnpj['Rentabilidade acumulada 5 anos ']}%")
            else:
                st.write(f"Nenhum dado encontrado para o CNPJ: {cnpj_input}")
    else:
        st.write("Por favor, carregue os dados antes de consultar um CNPJ.")

# Executar o Streamlit
if __name__ == "__main__":
    main()
