from dagster import Definitions, asset, Config, define_asset_job, AssetIn
from app.models.search import Getdata
from app.models.read_data import Lerdados
import pandas as pd

class TickerConfig(Config):
    tickers: list[str]

@asset
def raw_market_data(config: TickerConfig) -> pd.DataFrame:
    """Extrai dados brutos do Yahoo Finance e Banco Central."""
    inv = Getdata(list_actions=config.tickers)
    df_raw = inv.symbols()
    inv.getipca()
    inv.getselic()
    return df_raw

@asset
def ticker_list(raw_market_data: pd.DataFrame) -> list:
    """Extrai a lista única de tickers dos dados brutos."""
    return raw_market_data['acao'].unique().tolist()

@asset
def processed_prices(raw_market_data: pd.DataFrame, ticker_list: list):
    """Transforma dados de preços (Adj Close) e salva o CSV final."""
    ler_dados = Lerdados()
    df_prices = ler_dados.transformacao(ticker_list, raw_market_data)
    # O arquivo já é salvo dentro do método transformacao em ./data/dados_adj_close.csv
    return True

@asset
def processed_dividends(raw_market_data: pd.DataFrame, ticker_list: list):
    """Transforma dados de dividendos e salva o CSV final."""
    ler_dados = Lerdados()
    df_div = ler_dados.dividendos(ticker_list, raw_market_data)
    # O arquivo já é salvo dentro do método dividendos em ./data/dados_dividendos.csv
    return True

# Job que engloba toda a linhagem
market_data_job = define_asset_job(
    name="market_data_job", 
    selection=["raw_market_data", "ticker_list", "processed_prices", "processed_dividends"]
)

defs = Definitions(
    assets=[raw_market_data, ticker_list, processed_prices, processed_dividends],
    jobs=[market_data_job]
)
