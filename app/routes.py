from flask import Blueprint, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
from dagster import DagsterClient
from flask import current_app

# Removidos os imports diretos de modelos de extração para usar via Dagster
# from app.models.search import Getdata 
from app.models.read_data import Lerdados
from app.models.analise import analises, plot_markowitz
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        actions_list = request.form.get("actions_list")
        actions = [action.strip() for action in actions_list.split(",")]

        # Conecta ao cliente Dagster (deve estar rodando em DAGSTER_HOST:DAGSTER_PORT)
        client = DagsterClient(
            current_app.config['DAGSTER_HOST'], 
            port_number=int(current_app.config['DAGSTER_PORT'])
        )
        
        # Dispara o Job passando a lista de ações como configuração
        client.submit_job_execution(
            "market_data_job",
            run_config={
                "ops": {
                    "raw_market_data": {
                        "config": {"tickers": actions}
                    }
                }
            }
        )

        return redirect(url_for("main.dashboard"))

    return render_template("index.html")


@main_bp.route("/transform")
def transform():
    ler_dados = Lerdados()
    tickets, dados_acoes = ler_dados.listactions()
    df_transformado = ler_dados.transformacao(tickets, dados_acoes)

    return render_template("transform.html", data=df_transformado.to_dict(orient="records"))


@main_bp.route("/dashboard")
def dashboard():
    df_price = pd.read_csv("./data/dados_adj_close.csv", sep=";", encoding="utf-8")
    num_colunas = len(df_price.columns) - 2

    df_ipca = pd.read_csv("./data/dados_ipca.csv", sep=";", encoding="utf-8")
    last_ipca = df_ipca["valor"].iloc[-1]

    df_selic = pd.read_csv("./data/dados_selic.csv", sep=";", encoding="utf-8")
    last_selic = df_selic["valor"].iloc[-1]

    fig_price = px.area(
        df_price,
        x="Date",
        y=df_price.columns[1:],
        title="Gráfico de Linhas das Ações",
    )

    df_yield = pd.read_csv("./data/dados_dividendos.csv", sep=";", encoding="utf-8")
    soma_dividendos = df_yield.iloc[:, 3:].sum()
    df_soma = soma_dividendos.reset_index()
    df_soma.columns = ["Ação", "Soma dos Dividendos"]

    fig_yield = px.bar(
        df_soma,
        x="Soma dos Dividendos",
        y="Ação",
        title="Soma dos Dividendos por Ação no Período",
    )

    graph_price_html = fig_price.to_html(full_html=False)
    graph_yield_html = fig_yield.to_html(full_html=False)

    return render_template(
        "dashboard/index.html",
        graph_price_html=graph_price_html,
        graph_yield_html=graph_yield_html,
        num_colunas=num_colunas,
        last_ipca=last_ipca,
        last_selic=last_selic,
    )


@main_bp.route("/analysis", methods=["GET", "POST"])
def analysis():
    allocation = None
    leftover = None
    total_portfolio_value = None
    markowitz_plot = None

    if request.method == "POST":
        try:
            total_portfolio_value = float(request.form["portfolio_value"])

            carteira = pd.read_csv(
                "./data/dados_adj_close.csv",
                sep=";",
                encoding="utf-8",
                parse_dates=["Date"],
                index_col="Date",
            )
            ultima_linha = carteira.iloc[-1]
            ultimos_precos = ultima_linha.drop(labels=["IBOV"], errors="ignore").to_dict()

            df_selic = pd.read_csv("./data/dados_selic.csv", sep=";", encoding="utf-8")
            last_selic = df_selic["valor"].iloc[-1]

            allocation, leftover, total_value = analises(carteira, total_portfolio_value)
            colunas_ativos = [c for c in carteira.columns if c not in ["IBOV", "^BVSP", "Unnamed: 0"]]
            markowitz_plot = plot_markowitz(carteira, colunas_ativos, risk_free_rate=last_selic / 100)

            return render_template(
                "analysis.html",
                allocation=allocation,
                leftover=leftover,
                total_portfolio_value=total_value,
                markowitz_plot=markowitz_plot,
                last_selic=last_selic,
                ultimos_precos=ultimos_precos,
            )
        except Exception as e:
            return render_template("analysis.html", error_message="Erro ao processar a análise: " + str(e))

    return render_template(
        "analysis.html",
        allocation=allocation,
        leftover=leftover,
        total_portfolio_value=total_portfolio_value,
        markowitz_plot=markowitz_plot,
    )