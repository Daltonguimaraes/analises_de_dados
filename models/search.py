import datetime
import pandas as pd
import yfinance as yf
import os

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
