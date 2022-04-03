from datetime import datetime
import pandas as pd


def import_positions_from_xls(xls : str) -> pd.DataFrame:
    report = pd.read_excel(xls)
    rows = []
    positions = report.index[report.iloc[:, 2] == 'Время'].to_list()
    for i in positions:
        ticker = report.iloc[i - 8, 0]
        j = i + 2
        while j < len(report):  # Перебираем все транзакции
            transaction = report.iloc[j, :]
            if (type(transaction[0]) is not datetime):
                break
            price = transaction[9]
            amount = transaction[12]
            cost = price * amount
            rows.append({'№ Сделки': transaction[5],
                         'Тикер': ticker,
                         'Время': transaction[2],
                         'Операция': transaction[8],
                         'Цена': price,
                         'Количество': amount,
                         'Стоимость': cost})
            j += 1

    columns = ['№ Сделки', 'Тикер', 'Время', 'Операция', 'Цена', 'Количество', 'Стоимость']
    return pd.DataFrame(rows, columns=columns).set_index('№ Сделки')