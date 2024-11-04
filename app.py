from flask import Flask, render_template, request, redirect, url_for
from models.shearch import Getdata
from models.read_data import Lerdados
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
    # Carrega o arquivo CSV
    df = pd.read_csv('./data/dados_adj_close.csv', sep=';', encoding='utf-8')
    
    # Cria um gráfico de linhas usando Plotly
    fig = px.area(
        df,
        x='Date',  # Coluna de datas
        y=df.columns[1:],  # Todas as colunas de ações, excluindo 'Date'
        title='Gráfico de Linhas das Ações'
    )

    # Converte o gráfico para HTML
    graph_html = fig.to_html(full_html=False)

    # Passa o gráfico para o template
    return render_template('dashboard.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
