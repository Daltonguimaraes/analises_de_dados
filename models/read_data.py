from models.scandir import Getfiles
import pandas as pd

class Lerdados:
    # Ler o último arquivo CSV disponível no diretório
    def listactions(self):
        conjunto = Getfiles()
        csv_files = conjunto.directories()
        csv_files_sorted = sorted(csv_files, key=lambda x: x[1], reverse=True)
        latest_csv_file = csv_files_sorted[0][0]
        print(f'O último arquivo adicionado foi: {latest_csv_file}')
        print("----------------------------------------------------------------------------------")

        dados_acoes = pd.read_csv(latest_csv_file, sep=";")
        tickets = dados_acoes['acao'].unique()
        print(f'Lista de ações: {tickets}')
        print("----------------------------------------------------------------------------------")
        return tickets, dados_acoes

    # Transformar os dados filtrando informações relevantes
    def transformacao(self, tickets, dados_acoes):
        df_resultado = pd.DataFrame({'Date': []})

        for acoes in tickets:
            df_filtrado = dados_acoes[dados_acoes['acao'] == acoes][['Date', 'Adj Close']]
            df_filtrado = df_filtrado.rename(columns={'Adj Close': acoes})
            df_resultado = df_resultado.merge(df_filtrado, on='Date', how='outer')

        print(df_resultado.tail(6))
        df_resultado.to_csv('data/dados_adj_close.csv', sep=';', encoding='utf-8', index=True)
        return df_resultado
