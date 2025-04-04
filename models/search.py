import datetime
import pandas as pd
import yfinance as yf
import os
import requests

class Getdata:  
    def __init__(self, period="1y", interval="1d", list_actions=None):
        if list_actions is None:
            list_actions = []

        self.period = period
        self.interval = interval
        self.list_actions = list_actions

    def date(self):
        print(f"O período selecionado é: {self.period} e o intervalo é: {self.interval}")

    def tickets(self):
        print(f'As ações selecionadas são: {self.list_actions}')

    def symbols(self):
        symbols_data = []
        for acao in self.list_actions:
            ticker = yf.Ticker(acao)
            dados = ticker.history(period=self.period, interval=self.interval, auto_adjust=False)
            dados = dados.assign(acao=acao)
            symbols_data.append(dados)

        dados_completos = pd.concat(symbols_data)
        
        # salvar os dados em arquivo CSV
        local = datetime.datetime.now()
        file = local.strftime('%H_%M_%S')
        dir = local.strftime('%d-%m-%Y')
        os.makedirs(f'data/symbols/{dir}', exist_ok=True)
        dados_completos.to_csv(f'data/symbols/{dir}/symbols-{file}.csv', sep=';', encoding='utf-8', index=True)
        print("----------------------------------------------------------------------------------")
        print(f'Dados salvos em: data/symbols/{dir}, com o nome {file}.csv')
        print("----------------------------------------------------------------------------------")
        return dados_completos

    def getipca(self):
        # Código da série do IPCA
        codigo_serie = 16121

        # Datas: dataInicial deve ser MENOR que dataFinal
        dataInicial = datetime.date(2024, 4, 2)  # Exemplo fixo, igual ao da sua URL
        dataFinal = datetime.date(2025, 4, 2)    # Exemplo fixo

        # Converte para formato dd/mm/yyyy exigido pela API
        dataInicial_str = dataInicial.strftime('%d/%m/%Y')
        dataFinal_str = dataFinal.strftime('%d/%m/%Y')

        # Monta URL
        url = (
        f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados'
        f'?formato=json&dataInicial={dataInicial_str}&dataFinal={dataFinal_str}')

        # Requisição
        response = requests.get(url)

        if response.status_code == 200:
            dados = response.json()
            if dados:
                df_ipca = pd.DataFrame(dados)
                df_ipca.to_csv('./data/dados_ipca.csv', sep=';', encoding='utf-8', index=False)
                return df_ipca
            else:
                print("A API retornou uma lista vazia.")
                return pd.DataFrame()
        else:
            print(f'Erro na requisição: {response.status_code}')
            return pd.DataFrame()