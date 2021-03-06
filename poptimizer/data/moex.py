"""Основные функции агрегации данных по котировкам акций."""
import asyncio
from typing import Tuple, Optional, List

import numpy as np
import pandas as pd

from poptimizer import store

__all__ = ["lot_size", "prices", "turnovers", "securities_with_reg_number", "index"]


async def _securities(tickers: Optional[Tuple[str, ...]] = None) -> pd.Series:
    """Информация о размере лотов для тикеров.

    :param tickers:
        Перечень тикеров, для которых нужна информация. При отсутствии информация будет предоставлена
        для всех торгуемых бумаг.
    :return:
        Информация о размере лотов.
    """
    async with store.Client() as client:
        db = client.securities()
        df = await db.get()
    if tickers:
        return df.loc[list(tickers)]
    return df


def securities_with_reg_number() -> pd.Index:
    """Все ценные акции с регистрационным номером."""
    df = asyncio.run(_securities())
    return df.dropna(axis=0).index


def lot_size(tickers: Optional[Tuple[str, ...]] = None) -> pd.Series:
    """Информация о размере лотов для тикеров.

    :param tickers:
        Перечень тикеров, для которых нужна информация. При отсутствии информация будет предоставлена
        для всех торгуемых бумаг.
    :return:
        Информация о размере лотов.
    """
    df = asyncio.run(_securities(tickers))
    return df[store.LOT_SIZE]


async def _index() -> pd.DataFrame:
    """Загрузка данных по индексу полной доходности с учетом российских налогов - MCFTRR.

    :return:
        История цен закрытия индекса.
    """
    async with store.Client() as client:
        db = client.index()
        return await db.get()


def index(last_date: pd.Timestamp) -> pd.DataFrame:
    """Загрузка данных по индексу полной доходности с учетом российских налогов - MCFTRR.

    :param last_date:
        Последняя дата котировок.
    :return:
        История цен закрытия индекса.
    """
    df = asyncio.run(_index())
    return df[:last_date]


async def _quotes(tickers: Tuple[str, ...]) -> List[pd.DataFrame]:
    """Информация о котировках для заданных тикеров (цена закрытия и объем).

    :param tickers:
        Перечень тикеров, для которых нужна информация.
    :return:
        Список с котировками.
    """
    async with store.Client() as client:
        db = client.quotes(tickers)
        return await db.get()


def prices(tickers: tuple, last_date: pd.Timestamp) -> pd.DataFrame:
    """Дневные цены закрытия для указанных тикеров до указанной даты включительно.

    Пропуски заполнены предыдущими значениями.

    :param tickers:
        Тикеры, для которых нужна информация.
    :param last_date:
        Последняя дата цен закрытия.
    :return:
        Цены закрытия.
    """
    quotes_list = asyncio.run(_quotes(tickers))
    df = pd.concat([df[store.CLOSE] for df in quotes_list], axis=1)
    df = df.loc[:last_date]
    df.columns = tickers
    return df.replace(to_replace=[np.nan, 0], method="ffill")


def turnovers(tickers: tuple, last_date: pd.Timestamp) -> pd.DataFrame:
    """Дневные обороты для указанных тикеров до указанной даты включительно.

    Пропуски заполнены нулевыми значениями.

    :param tickers:
        Тикеры, для которых нужна информация.
    :param last_date:
        Последняя дата оборотов.
    :return:
        Обороты.
    """
    quotes_list = asyncio.run(_quotes(tickers))
    df = pd.concat([df[store.TURNOVER] for df in quotes_list], axis=1)
    df = df.loc[:last_date]
    df.columns = tickers
    return df.fillna(0, axis=0)
