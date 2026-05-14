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
    sub = variancias.iloc[0] - np.sum(variancias.iloc[1:])
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

def plot_markowitz(carteira, colunas_ativos, risk_free_rate=0.0):
    # Use apenas colunas numéricas dos ativos e limpe valores inválidos
    prices = carteira[colunas_ativos].apply(pd.to_numeric, errors='coerce')
    prices = prices.replace([np.inf, -np.inf], np.nan).dropna(how='any')

    mu = mean_historical_return(prices, frequency=246)
    S = CovarianceShrinkage(prices, frequency=246).ledoit_wolf()

    # Descobrir limites viáveis de risco para evitar erros de "minimum volatility"
    risks = []
    returns = []

    ef_min = EfficientFrontier(mu, S)
    ef_min.min_volatility()
    _, min_vol, _ = ef_min.portfolio_performance(verbose=False)

    # Usar o maior desvio padrão de um ativo como limite superior seguro
    max_vol = float(np.sqrt(np.max(np.diag(S.values))))

    if max_vol <= min_vol:
        max_vol = min_vol * 1.5

    for target_volatility in np.linspace(min_vol * 1.001, max_vol, 50):
        ef = EfficientFrontier(mu, S)
        try:
            ef.efficient_risk(target_volatility)
            ret, std, _ = ef.portfolio_performance(verbose=False)
            print(f"Volatilidade: {target_volatility:.2f} | Retorno: {ret:.4f} | Risco: {std:.4f}")
            returns.append(ret)
            risks.append(std)
        except Exception as e:
            print(f"Erro para volatilidade {target_volatility:.2f}: {e}")
            continue

    # Portfólio ótimo (máximo Sharpe) para construir a reta do portfólio ótimo (CAL)
    ef_tan = EfficientFrontier(mu, S)
    try:
        ef_tan.max_sharpe(risk_free_rate=risk_free_rate)
        ret_tan, vol_tan, _ = ef_tan.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
    except Exception as e:
        ret_tan, vol_tan = None, None
        print(f"Erro ao calcular portfólio ótimo (max Sharpe): {e}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=risks,
        y=returns,
        mode='lines+markers',
        name='Fronteira Eficiente',
        line=dict(color='blue', width=2),
        marker=dict(size=5, color='blue')
    ))

    # Reta do portfólio ótimo (Capital Allocation Line)
    if ret_tan is not None and vol_tan is not None and vol_tan > 0:
        max_risk = max(risks) if risks else vol_tan
        cal_x = np.linspace(0, max_risk, 50)
        slope = (ret_tan - risk_free_rate) / vol_tan
        cal_y = risk_free_rate + slope * cal_x
        fig.add_trace(go.Scatter(
            x=cal_x,
            y=cal_y,
            mode='lines',
            name='Reta do Portfólio Ótimo (CAL)',
            line=dict(color='red', width=2, dash='dash')
        ))

    fig.update_layout(
        title='Fronteira Eficiente de Markowitz',
        xaxis_title='Risco (Desvio Padrão)',
        yaxis_title='Retorno Esperado',
        template='plotly_white',
        height=500
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})
