import asyncio

import pandas as pd
import pytest

from poptimizer.data import moex
from poptimizer.store import CLOSE, TURNOVER


def test_securities_with_reg_number():
    result = moex.securities_with_reg_number()
    assert isinstance(result, pd.Index)
    assert result.size > 259
    assert "AGRO" not in result
    assert "YNDX" not in result
    assert "BANEP" in result


def test_lot_size_all():
    df = moex.lot_size()

    assert isinstance(df, pd.Series)
    assert len(df) > 200

    assert df.index[0] == "ABRD"
    assert df.iat[0] == 10

    assert df.iat[-1] == 1000
    assert df.index[-1] == "ZVEZ"

    assert df["AKRN"] == 1
    assert df["KBTK"] == 10
    assert df["MOEX"] == 10
    assert df["MRSB"] == 10000
    assert df["MTSS"] == 10
    assert df["SNGSP"] == 100
    assert df["TTLK"] == 10000
    assert df["PMSBP"] == 10


def test_lot_size_some():
    df = moex.lot_size(("RTKM", "SIBN", "MRSB"))

    assert isinstance(df, pd.Series)
    assert len(df) == 3

    assert df["RTKM"] == 10
    assert df["SIBN"] == 10
    assert df["MRSB"] == 10000


def test_index():
    df = moex.index(pd.Timestamp("2018-12-24"))
    assert isinstance(df, pd.Series)
    assert len(df) > 3750
    assert df.index[0] == pd.Timestamp("2003-02-26")
    assert df.index[-1] == pd.Timestamp("2018-12-24")
    assert df["2003-02-26"] == 335.67
    assert df["2018-03-02"] == 3273.16
    assert df["2018-03-16"] == 3281.58
    assert df["2018-12-24"] == 3492.91


def test_no_data():
    """Некоторые бумаги не имеют котировок.

    Дополнительная проверка, что эта ситуация обрабатывается без ошибок.
    """
    # noinspection PyProtectedMember
    quotes_list = asyncio.run(moex._quotes(("KSGR", "KMTZ", "TRFM")))
    for df in quotes_list:
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == [CLOSE, TURNOVER]


def test_multi_tickers():
    """Некоторые бумаги со старой историей торговались одновременно под несколькими тикерами.

    Дополнительная проверка, что у данных уникальный возрастающий индекс.
    """
    # noinspection PyProtectedMember
    quotes_list = asyncio.run(moex._quotes(("PRMB", "OGKB")))
    for df in quotes_list:
        assert isinstance(df, pd.DataFrame)
        assert df.index.is_unique
        assert df.index.is_monotonic_increasing


def test_prices():
    df = moex.prices(("AKRN", "GMKN", "KBTK"), pd.Timestamp("2018-12-06"))
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 3000
    assert df.shape[1] == 3
    assert df.index[-1] == pd.Timestamp("2018-12-06")

    assert df.loc["2006-10-20", "AKRN"] == pytest.approx(834.93)
    assert df.loc["2018-09-10", "AKRN"] == pytest.approx(4528)

    assert df.loc["2018-09-07", "GMKN"] == pytest.approx(11200)
    assert df.loc["2018-12-06", "GMKN"] == pytest.approx(12699)

    assert df.loc["2018-03-12", "KBTK"] == pytest.approx(145)
    assert df.loc["2010-05-24", "KBTK"] == pytest.approx(180)


def test_zero_prices():
    df = moex.prices(("AKRN", "KAZTP"), pd.Timestamp("2018-12-14"))
    assert df.loc["2012-03-12", "KAZTP"] == pytest.approx(46.011)
    assert df.loc["2012-03-15", "KAZTP"] == pytest.approx(47.101)


def test_turnovers():
    df = moex.turnovers(("PMSBP", "RTKM"), pd.Timestamp("2018-12-05"))
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 3000
    assert df.shape[1] == 2
    assert df.index[-1] == pd.Timestamp("2018-12-05")

    assert df.loc["2003-10-08", "PMSBP"] == pytest.approx(0)
    assert df.loc["2018-10-10", "PMSBP"] == pytest.approx(148056)

    assert df.loc["2003-10-09", "RTKM"] == pytest.approx(1485834851.93)
    assert df.loc["2018-12-05", "RTKM"] == pytest.approx(117397440.3)
