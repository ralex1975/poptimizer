import numpy as np
import pandas as pd
import pytest

from poptimizer import config
from poptimizer.config import POptimizerError
from poptimizer.portfolio import portfolio
from poptimizer.portfolio.portfolio import CASH, PORTFOLIO

PARAMS = dict(
    date="2018-03-19",
    cash=1000,
    positions=dict(GAZP=6820, VSMO=145, TTLK=1_230_000),
    value=3_699_111,
)


def test_portfolio(monkeypatch):
    monkeypatch.setattr(config, "TURNOVER_PERIOD", 7)
    monkeypatch.setattr(config, "TURNOVER_CUT_OFF", 0.6)

    port = portfolio.Portfolio(**PARAMS)

    assert "Дата - 2018-03-19" in str(port)
    assert port.date == pd.Timestamp("2018-03-19")
    assert port.index.tolist() == ["GAZP", "TTLK", "VSMO", CASH, PORTFOLIO]
    assert np.allclose(port.shares, [6820, 1_230_000, 145, 1000, 1])
    assert np.allclose(port.lot_size, [10, 10000, 1, 1, 1])
    assert np.allclose(port.lots, [682, 123, 145, 1000, 1])
    assert np.allclose(port.price, [139.91, 0.1525, 17630, 1, 3_699_111])
    assert np.allclose(port.value, [954_186, 187_575, 2_556_350, 1000, 3_699_111])
    assert np.allclose(
        port.weight,
        [
            0.257_950_085_844_95,
            0.050_708_129_601_95,
            0.691_071_449_329_312,
            0.000_270_335_223_788,
            1,
        ],
    )
    assert np.allclose(port.turnover_factor, [1, 0, 0.693_130_358_498_49, 1, 1])


def test_portfolio_wrong_value():
    with pytest.raises(POptimizerError) as error:
        PARAMS["value"] = 123
        portfolio.Portfolio(**PARAMS)
    assert "Введенная стоимость портфеля 123" in str(error.value)


def test_portfolio_wrong_date():
    PARAMS["date"] = "2018-12-09"
    with pytest.raises(POptimizerError) as error:
        portfolio.Portfolio(**PARAMS)
    assert "Для даты 2018-12-09 отсутствуют исторические котировки" == str(error.value)
