from flask import Flask, render_template, request, redirect, url_for
from models.shearch import Getdata
from models.read_data import Lerdados

app = Flask(__name__)

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
        return redirect(url_for('transform'))
    
    return render_template('index.html')

@app.route('/transform')
def transform():
    # Obter lista de ações através do Lerdados
    ler_dados = Lerdados()
    tickets, dados_acoes = ler_dados.listactions()
    df_transformado = ler_dados.transformacao(tickets, dados_acoes)

    # Exibir a transformação dos dados
    return render_template('transform.html', data=df_transformado.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
