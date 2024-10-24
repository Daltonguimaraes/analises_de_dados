from flask import Flask, render_template
from models.shearch import Getdata
from models.read_data import Lerdados

app = Flask(__name__)

# Cria a lista inicial de ações e obtém os dados
inv = Getdata(list_actions=['^BVSP', 'CSMG3.SA', 'BBAS3.SA', 'CPFE3.SA', 'BRAP4.SA', 'BBSE3.SA'])
inv.date()
inv.tickets()
inv.symbols()

# Obter lista de ações através do Lerdados
ler_dados = Lerdados()
tickets, dados_acoes = ler_dados.listactions()
df_transformado = ler_dados.transformacao(tickets, dados_acoes)

@app.route('/')
def index():
    # Exibir a lista de ações disponíveis
    return render_template('index.html', tickets=tickets)

@app.route('/transform')
def transform():
    # Exibir a transformação dos dados
    return render_template('transform.html', data=df_transformado.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
