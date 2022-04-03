import pandas as pd
from tinkoff.invest import Client, CandleInterval
from tinkoff.invest.token import TOKEN
from datetime import datetime, timedelta


def parse_response(response) -> pd.DataFrame:
    df = pd.DataFrame([{
        'Имя': i.name,
        'Тикер': i.ticker,
        'figi': i.figi,
        'isin': i.isin,
        'Биржа': i.exchange,
        'Режим торгов': i.class_code,
        'Валюта': i.currency,
        'Лот': i.lot,
        'Страна': i.country_of_risk
      } for i in response.instruments])
    return df

def get_all_instruments() -> pd.DataFrame:
    with Client(TOKEN) as client:
        shares = parse_response(client.instruments.shares())
        etfs = parse_response(client.instruments.etfs())
        bonds = parse_response(client.instruments.bonds())
        return pd.concat([shares, etfs, bonds]).set_index('Тикер')

def cast_money(v):
    """
    https://tinkoff.github.io/investAPI/faq_custom_types/
    :param v:
    :return:
    """
    return v.units + v.nano / 1e9 # nano - 9 нулей

def get_candles(figi : str, tmin: datetime, tmax: datetime = datetime.utcnow()) -> pd.DataFrame:
    res = []
    tmin = pd.to_datetime(tmin, unit="D", utc=True)
    with Client(TOKEN) as client:
        while True:
            r = client.market_data.get_candles(
                figi=figi,
                from_= tmax - timedelta(days=200),
                to=tmax,
                interval=CandleInterval.CANDLE_INTERVAL_DAY
            )

            df = pd.DataFrame([{
                'Время': c.time,
                'Объём': c.volume,
                'Цена открытия': cast_money(c.open),
                'Цена закрытия': cast_money(c.close),
                'Максимальная цена': cast_money(c.high),
                'Минимальная цена': cast_money(c.low),
                } for c in r.candles])
            res.append(df)

            tmax = pd.to_datetime(df.iloc[0,:]['Время'], unit="D", utc=True)
            if tmax < tmin:
                break

        return pd.concat(res).sort_values('Время')
