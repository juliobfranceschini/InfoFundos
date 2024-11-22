def filtrar_por_cnpj(dados, cnpj):
    # Filtrar pelos dados do CNPJ fornecido
    dados_cnpj = dados[dados['CNPJ_FUNDO_CLASSE'] == cnpj]

    if dados_cnpj.empty:
        return None
    else:
        # Depuração: Ver dados filtrados
        st.write("Dados filtrados pelo CNPJ:")
        st.write(dados_cnpj)

        # Converter a coluna de data para o formato datetime
        dados_cnpj['DT_COMPTC'] = pd.to_datetime(dados_cnpj['DT_COMPTC'], format='%Y-%m-%d', errors='coerce')

        # Depuração: Verificar as datas após conversão
        st.write("Datas após conversão:")
        st.write(dados_cnpj['DT_COMPTC'].dropna().head())

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

        # Renomear colunas
        dados_filtrados = dados_mais_recente[colunas_relevantes.keys()].rename(index=colunas_relevantes)

        # Substituir valores ausentes por "-"
        dados_filtrados = dados_filtrados.fillna("-")

        # Depuração: Verificar os dados finais antes de exibir
        st.write("Dados finais após manipulação:")
        st.write(dados_filtrados)

        return dados_filtrados
