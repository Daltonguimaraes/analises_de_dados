import pandas as pd
import numpy as np
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
from pypfopt import expected_returns, risk_models, CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.expected_returns import mean_historical_return

def analises(carteira, total_portfolio_value):
    # --- Leitura de dados ---
    selic = pd.read_csv('./data/dados_selic.csv', sep=';', encoding='utf-8')
    carteira = pd.read_csv(
        './data/dados_adj_close.csv', sep=';', encoding='utf-8', parse_dates=['Date'], index_col='Date')
    returns = carteira.pct_change().dropna()

    # Visualização inicial
    print(returns.head(), carteira.head())

    # --- Lista de ativos (sem benchmark) ---
    benchmark = '^BVSP'
    colunas_ativos = [col for col in carteira.columns if col not in [benchmark, 'Unnamed: 0']]
    ativos = returns[colunas_ativos]

    # --- Análise de risco (Beta em relação ao benchmark) ---
    benchmark_returns = returns[benchmark]
    for acao in colunas_ativos:
        dados_validos = pd.concat([benchmark_returns, returns[acao]], axis=1).dropna()
        dados_validos = dados_validos.replace([np.inf, -np.inf], np.nan).dropna()

        X = dados_validos[benchmark].values.reshape(-1, 1)
        y = dados_validos[acao].values.reshape(-1, 1)
        beta = LinearRegression().fit(X, y).coef_[0][0]
        print(f'Beta de {acao}: {round(beta, 2)}')

    # --- Estatísticas da carteira ---
    n = len(colunas_ativos)
    pesos = np.full(n, 1 / n)
    print(f'Peso igual por ativo: {pesos[0]:.2%}')

    variancias = ativos.var() * 246
    variancia_ponderada = np.dot(pesos, variancias)
    print(f'Variância anual ponderada: {variancia_ponderada:.6f}')

    matriz_cov = ativos.cov() * 246
    variancia_portfolio = np.dot(pesos.T, np.dot(matriz_cov, pesos))
    desvio_padrao_portfolio = np.sqrt(variancia_portfolio)
    print(f'Variância total (com covariância): {variancia_portfolio:.6f}')
    print(f'Desvio padrão anual: {desvio_padrao_portfolio:.6f}')

    # --- Risco não sistemático ---
    sub = variancias[0] - np.sum(variancias[1:])
    risco_nao_sistematico = variancia_portfolio - sub
    print(f'Subtração: {sub:.6f}')
    print(f'Risco não sistemático: {risco_nao_sistematico:.6f}')

    # --- Índice de Sharpe ---
    taxa_livre_risco = selic['valor'].iloc[-1] / 100
    retorno_medio_diario = (returns[colunas_ativos].mean() @ pesos)
    retorno_anual = retorno_medio_diario * 246
    volatilidade_anual = np.sqrt(variancia_portfolio)
    sharpe_ratio = (retorno_anual - taxa_livre_risco) / volatilidade_anual

    print(f'Retorno anual: {retorno_anual:.6f}')
    print(f'Taxa livre de risco (Selic): {taxa_livre_risco:.6f}')
    print(f'Índice de Sharpe: {sharpe_ratio:.4f}')

    # --- Fronteira Eficiente de Markowitz ---
    mu = expected_returns.mean_historical_return(carteira[colunas_ativos])
    s = risk_models.sample_cov(carteira[colunas_ativos])
    s = (s + s.T) / 2  # Forçar simetria

    ef = EfficientFrontier(mu, s)
    pesos_otimizados = ef.min_volatility()
    print('Pesos otimizados (mínima volatilidade):')
    print(pesos_otimizados)

    # Calcular a alocação de ativos para um determinado valor de portfólio:
    latest_prices = get_latest_prices(carteira[colunas_ativos])
    da = DiscreteAllocation(ef.clean_weights(), latest_prices, total_portfolio_value=total_portfolio_value)

    allocation, leftover = da.lp_portfolio()
    print("Alocação discreta de ativos:")
    print(allocation)
    print("Fundos restantes: R$ {:.2f}".format(leftover))
    
    return allocation, leftover, total_portfolio_value

def plot_markowitz(carteira, colunas_ativos):
    mu = mean_historical_return(carteira, colunas_ativos)
    S = CovarianceShrinkage(carteira, colunas_ativos).ledoit_wolf()

    ef = EfficientFrontier(mu, S)

    risks = []
    returns = []

    for target_volatility in np.linspace(0.05, 0.50, 50):
        ef = EfficientFrontier(mu, S)
        try:
            ef.efficient_risk(target_volatility)
            ret, std, _ = ef.portfolio_performance(verbose=False)
            print(f"Volatilidade: {target_volatility:.2f} | Retorno: {ret:.4f} | Risco: {std:.4f}")
            returns.append(ret)
            risks.append(std)
        except:
            print(f"Erro para volatilidade {target_volatility:.2f}: {ef}")
            continue

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=risks,
        y=returns,
        mode='lines+markers',
        name='Fronteira Eficiente',
        line=dict(color='blue', width=2),
        marker=dict(size=5, color='blue')
    ))

    fig.update_layout(
        title='Fronteira Eficiente de Markowitz',
        xaxis_title='Risco (Desvio Padrão)',
        yaxis_title='Retorno Esperado',
        template='plotly_white',
        width=800,
        height=500
    )
    return fig.to_html(full_html=False)
