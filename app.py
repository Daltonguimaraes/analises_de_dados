from flask import Flask, render_template, request, redirect, url_for
from models.search import Getdata
from models.read_data import Lerdados
from models.analise import analises, plot_markowitz
import plotly.express as px
import pandas as pd

app = Flask(__name__)

# Index
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recebe a lista de ações do formulário
        actions_list = request.form.get('actions_list')
        # Divide a string em uma lista de ações, removendo espaços extras
        actions = [action.strip() for action in actions_list.split(',')]
        
        # Cria o objeto Getdata com a lista de ações fornecida pelo usuário
        inv = Getdata(list_actions=actions)
        inv.date()
        inv.tickets()
        inv.symbols()
        inv.getipca()
        inv.getselic()

        # Obter lista de açoes pelo modulo lerdados
        ler_dados = Lerdados()
        tickets, dados_acoes = ler_dados.listactions()
        ler_dados.transformacao(tickets, dados_acoes)

        # Obter lista de dividendos pelo modulo lerdados
        ler_dados.dividendos(tickets, dados_acoes)    

        # Redireciona para a página de transformação após a consulta
        return redirect(url_for('dashboard'))
    
    return render_template('index.html')

# Apresentação dos dados transformados 
@app.route('/transform')
def transform():
    # Obter lista de ações através do Lerdados
    ler_dados = Lerdados()
    tickets, dados_acoes = ler_dados.listactions()
    df_transformado = ler_dados.transformacao(tickets, dados_acoes)

    # Exibir a transformação dos dados
    return render_template('transform.html', data=df_transformado.to_dict(orient='records'))

# Painel de gráficos com dados
@app.route('/dashboard')
def dashboard():
    # Tópico preços
    # Carrega o arquivo CSV
    df_price = pd.read_csv('./data/dados_adj_close.csv', sep=';', encoding='utf-8')
    
    #contar as colunas (ativos)
    num_colunas = len(df_price.columns) - 2 # Subtrai 2 para ignorar a coluna de data, e índice "IBOV"
    
    # Carrega o arquivo dado_ipca.csv
    df_ipca = pd.read_csv('./data/dados_ipca.csv', sep=';', encoding='utf-8')

    # Última data do arquivo dado_ipca.csv
    last_date = df_ipca['data'].iloc[-1]
    # Último valor do IPCA
    last_ipca = df_ipca['valor'].iloc[-1]
    
    # Carrega o arquivo dado_selic.csv
    df_selic = pd.read_csv('./data/dados_selic.csv', sep=';', encoding='utf-8')
    # Última data do arquivo dado_selic.csv
    last_date_selic = df_selic['data'].iloc[-1]
    # Último valor da Selic
    last_selic = df_selic['valor'].iloc[-1]

    # Cria um gráfico de linhas usando Plotly
    fig_price = px.area(
        df_price,
        x='Date',  # Coluna de datas
        y=df_price.columns[1:],  # Todas as colunas de ações, excluindo 'Date'
        title='Gráfico de Linhas das Ações'
    )

    # Tópico dividendos
    # Carrega o arquivo CSV
    df_yield = pd.read_csv('./data/dados_dividendos.csv', sep=';', encoding='utf-8')

    # Cria um gráfico de barras empilhadas para dividendos usando Plotly
    # Calcula a soma dos valores de cada coluna, excluindo 'Date'
    soma_dividendos = df_yield.iloc[:, 3:].sum()

    # Cria um DataFrame temporário para visualização
    df_soma = soma_dividendos.reset_index()
    df_soma.columns = ['Ação', 'Soma dos Dividendos']

    # Cria o gráfico de barras
    fig_yield = px.bar(
        df_soma,
        x='Soma dos Dividendos',
        y='Ação',
        title='Soma dos Dividendos por Ação no Período'
    )
    
    # Converte os gráficos para HTML com nomes distintos
    graph_price_html = fig_price.to_html(full_html=False)
    graph_yield_html = fig_yield.to_html(full_html=False)

    # Passa os gráficos e o número de colunas para o template
    return render_template(
        'dashboard.html',
        graph_price_html=graph_price_html,
        graph_yield_html=graph_yield_html,
        num_colunas=num_colunas,
        last_ipca=last_ipca,
        last_selic=last_selic
    )

# Painel de análise de ativos
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    allocation = None
    leftover = None
    total_portfolio_value = None
    markowitz_plot = None

    if request.method == 'POST':
        try:
            # Receber o valor total do portfólio do formulário HTML
            total_portfolio_value = float(request.form['portfolio_value'])

            # Carregar os dados de carteira
            carteira = pd.read_csv('./data/dados_adj_close.csv', sep=';', encoding='utf-8', parse_dates=['Date'], index_col='Date')
            # Calcular último preço de cada ativo (excluindo IBOV, se existir)
            ultima_linha = carteira.iloc[-1]
            ultimos_precos = ultima_linha.drop(labels=['IBOV'], errors='ignore').to_dict()

            # Carrega o arquivo dado_selic.csv
            df_selic = pd.read_csv('./data/dados_selic.csv', sep=';', encoding='utf-8')
            # Última data do arquivo dado_selic.csv
            last_date_selic = df_selic['data'].iloc[-1]
            # Último valor da Selic
            last_selic = df_selic['valor'].iloc[-1]

            # Chamar a função de análise do script analise.py
            allocation, leftover, total_value = analises(carteira, total_portfolio_value)

            # Chamar a função de plotagem do script analise.py
            markowitz_plot = plot_markowitz(carteira, list(allocation.keys()))

            # Renderizar com os dados calculados
            return render_template('analysis.html', allocation=allocation, leftover=leftover, total_portfolio_value=total_value, markowitz_plot=markowitz_plot, last_selic=last_selic, ultimos_precos=ultimos_precos)
        except Exception as e:
            return render_template('analysis.html', error_message="Erro ao processar a análise: " + str(e))

    # GET request: apenas renderizar o formulário
    return render_template('analysis.html', allocation=allocation, leftover=leftover, total_portfolio_value=total_portfolio_value, markowitz_plot=markowitz_plot)

# Roda o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)