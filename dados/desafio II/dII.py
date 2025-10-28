import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# tratamento base: carregar tabela
try:
    # puxando os dados da tabela
    dados = pd.read_csv('Base_Membros_Desempenho.csv')
    # verificação se os dados foram puxados:
    print(dados.head())
    
    # verificando os cargos e quantidade 
    print()
    print(dados['Nivel_Senioridade'].unique())
    print(dados['Nivel_Senioridade'].value_counts())
    print()


    # =-=-=-=-=-=-=-=-= Primeiro Tratamento =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Nível Senioridade =-=-=-=-=-=-=-=-= #

    mapeamento_senioridade = {
        'Jr': 'Júnior',
        'JR': 'Júnior',
        'P': 'Pleno',
        'pleno': 'Pleno',
        'Senior': 'Sênior',
        'senior': 'Sênior',
        'N/D': np.nan
    }

    # corrigindo os cargos
    dados['Nivel_Senioridade'] = dados['Nivel_Senioridade'].replace(mapeamento_senioridade)

    # corrigindo os dados nulos 
    moda_da_senioridade = dados['Nivel_Senioridade'].mode()[0]
    dados['Nivel_Senioridade'] = dados['Nivel_Senioridade'].fillna(moda_da_senioridade)

    # verificação se foi ou não corrigido
    print(dados['Nivel_Senioridade'].unique())  # lista para ver os cargos atuais
    print(dados['Nivel_Senioridade'].value_counts())    # lista para ver se houve ou não preenchimento dos N/D
    print()


    # =-=-=-=-=-=-=-=-= Segundo Tratamento =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Avaliação Técnica =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Avaliação Comportamental =-=-=-=-=-=-=-=-= #

    # covertendo todos os valores para str e fazendo as substituições para padronizar e poder fazer cálculos
    dados['Avaliacao_Tecnica'] = dados['Avaliacao_Tecnica'].astype(str).str.replace(',', '.')
    dados['Avaliacao_Tecnica'] = pd.to_numeric(dados['Avaliacao_Tecnica'], errors='coerce')
    dados['Avaliacao_Comportamental'] = dados['Avaliacao_Comportamental'].astype(str).str.replace(',', '.')
    dados['Avaliacao_Comportamental'] = pd.to_numeric(dados['Avaliacao_Comportamental'], errors='coerce')

    # corrigindo valores nulos com a média
    media_tec = dados['Avaliacao_Tecnica'].mean()
    media_comp = dados['Avaliacao_Comportamental'].mean()
    dados['Avaliacao_Tecnica'] = dados['Avaliacao_Tecnica'].fillna(media_tec)
    dados['Avaliacao_Comportamental'] = dados['Avaliacao_Comportamental'].fillna(media_comp)

    # substiuindo tudo para vírgula
    dados['Avaliacao_Tecnica'] = dados['Avaliacao_Tecnica'].map(lambda x: f"{x:.1f}".replace('.', ','))
    dados['Avaliacao_Comportamental'] = dados['Avaliacao_Comportamental'].map(lambda x: f"{x:.1f}".replace('.', ','))

    # verificação
    print()
    print(dados['Avaliacao_Tecnica'].head())                # padrão
    print(dados['Avaliacao_Tecnica'].isnull().sum())        # valor nulo

    print()
    print(dados['Avaliacao_Comportamental'].head())         # padrão
    print(dados['Avaliacao_Comportamental'].isnull().sum()) # valor nulo
    print()


    # =-=-=-=-=-=-=-=-= Terceiro Tratamento =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Engajamento PIGs =-=-=-=-=-=-=-=-= #

    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'].astype(str)          # garante que é texto
    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'].str.replace('%', '')  # remove o símbolo %
    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'].replace(['N/A', 'n/a', 'ND', 'nd'], np.nan)

    # converte o texto em número
    dados['Engajamento_PIGs'] = pd.to_numeric(dados['Engajamento_PIGs'], errors='coerce')

    # de % para decimal
    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'] / 100

    # preenchendo valores nulos com a média
    media_pigs = dados['Engajamento_PIGs'].mean()
    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'].fillna(media_pigs)

    # padronizando casas decimais e vírgula
    dados['Engajamento_PIGs'] = dados['Engajamento_PIGs'].map(lambda x: f"{x:.3f}".replace('.', ','))

    # verificação
    print("Engajamento PIGs após tratamento:")
    print(dados['Engajamento_PIGs'].head())
    print("Média usada para preenchimento:", round(media_pigs, 3))
    print()


    # =-=-=-=-=-=-=-=-= Quarto Tratamento =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Score Desempenho =-=-=-=-=-=-=-=-= #

    # voltando os dados para float apenas para cálculo
    dados['Score_Desempenho'] = (
        dados['Avaliacao_Tecnica'].str.replace(',', '.').astype(float) +
        dados['Avaliacao_Comportamental'].str.replace(',', '.').astype(float)
    ) / 2
    # padronizando com vírgula
    dados['Score_Desempenho'] = dados['Score_Desempenho'].map(lambda x: f"{x:.1f}".replace('.', ','))

    # verificação
    print(dados[['Avaliacao_Tecnica', 'Avaliacao_Comportamental', 'Score_Desempenho']].head())
    print()


    # =-=-=-=-=-=-=-=-= Quinto Tratamento =-=-=-=-=-=-=-=-= #
    # =-=-=-=-=-=-=-=-= Status Membro =-=-=-=-=-=-=-=-= #

    # para lógica, cria float temporário
    dados['Score_Desempenho_float'] = dados['Score_Desempenho'].str.replace(',', '.').astype(float)
    dados['Engajamento_PIGs_float'] = dados['Engajamento_PIGs'].str.replace(',', '.').astype(float)
    condicao_score = dados['Score_Desempenho_float'] >= 7.0
    condicao_engajamento = dados['Engajamento_PIGs_float'] >= 0.8
    dados['Status_Membro'] = np.where(condicao_score & condicao_engajamento, 'Em Destaque', 'Padrão')
    # remove colunas auxiliares
    dados.drop(['Score_Desempenho_float', 'Engajamento_PIGs_float'], axis=1, inplace=True)

    # verificação
    print(dados[['Score_Desempenho', 'Engajamento_PIGs', 'Status_Membro']].head(10))


    # =-=-=-=-=-=-=-=-= Final =-=-=-=-=-=-=-=-= #
    
    # exportando para Excel
    dados.to_excel('Base_Membros_Desempenho_Padronizada.xlsx', index=False)

    # =-=-=-=-=-=-=-=-= Exportar PDF completo =-=-=-=-=-=-=-=-= #
    fig, ax = plt.subplots(figsize=(20, max(6, len(dados)*0.25)))  # altura ajustada ao número de linhas
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=dados.values, colLabels=dados.columns, cellLoc='center', loc='center')
    plt.savefig('Base_Membros_Desempenho_Padronizada.pdf', bbox_inches='tight')
    plt.close()

    print("Arquivos Excel e PDF gerados com sucesso!")


    # =-=-=-=-=-=-=-=-= Versão para Looker Studio =-=-=-=-=-=-=-=-= #
    dados_limp = dados.copy()

    # substituindo vírgulas por pontos apenas nas colunas numéricas
    dados_limp['Engajamento_PIGs'] = dados_limp['Engajamento_PIGs'].str.replace(',', '.')
    dados_limp['Score_Desempenho'] = dados_limp['Score_Desempenho'].str.replace(',', '.')

    # salvando CSV compatível com Looker Studio (UTF-8 puro)
    dados_limp.to_csv('Base_Membros_Desempenho_UTF8.csv', index=False, encoding='utf-8', sep=',')

    print("Arquivo CSV para Looker Studio gerado com sucesso!")


except FileNotFoundError:
    print('Arquivo não encontrado')
