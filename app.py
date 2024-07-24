import pandas as pd
from flask import Flask, render_template
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Carregar os dados do arquivo CSV e verificar o cabeçalho
df = pd.read_csv('dados_adj_close.csv', delimiter=';')
print(df.head())  # Adicione esta linha para verificar o cabeçalho e os dados

# Verificar e ajustar o nome das colunas, se necessário
df.columns = df.columns.str.strip()  # Remover espaços em branco dos nomes das colunas

# Convertendo a coluna 'Date' para datetime e configurando como índice
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Inicializar o servidor Flask
server = Flask(__name__)

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Definir o layout do dashboard
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-grafico',
        options=[{'label': col, 'value': col} for col in df.columns if col != 'Date'],
        value=df.columns[1]  # Selecionar a segunda coluna como valor padrão
    ),
    dcc.Graph(id='grafico')
])

# Criar os callbacks para interatividade
@app.callback(
    Output('grafico', 'figure'),
    [Input('dropdown-grafico', 'value')]
)
def update_graph(column_name):
    fig = px.line(df, x=df.index, y=column_name, title=f'Gráfico de {column_name}')
    return fig

# Criar a rota do Flask
@server.route('/')
def home():
    return render_template('index.html', dash_script=app.index_string)

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
