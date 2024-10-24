import datetime
import pandas as pd
import yfinance as yf
yf.pdr_override()
import pandas_datareader.data as web
import os


class Getdata:  
    def __init__(self, start=None, end=None, list_actions=None):
        if start is None:
            start = datetime.datetime.now() - datetime.timedelta(days=365)
        if end is None:
            end = datetime.datetime.now()
        if list_actions is None:
            list_actions = []

        self.start = start
        self.end = end
        self.list_actions = list_actions

    def date(self):
        print(f"A data inicial é: {self.start.strftime('%d/%m/%Y')} e a data final é: {self.end.strftime('%d/%m/%Y')}")

    def tickets(self):
        print(f'As ações selecionadas são: {self.list_actions}')

    def symbols(self):
        symbols_data = []
        for acao in self.list_actions:
            dados = web.get_data_yahoo(acao, self.start, self.end)
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
