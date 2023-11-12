from SbilTrader import SbilTrader
import siuba as su
from siuba import _
import pandas as pd

instance = SbilTrader()


imb = (
    instance.data_quartorario_preliminare >>
    su.select(
        _.reference_date, _.imbalance
    )
    )

prices = (
    instance.prices_quartorario_daily >> 
    su.select(_.reference_date, _.imbalance_price)
          )

comb = su.left_join(imb, prices, on = "reference_date") >> su.arrange(_.reference_date)
clean_comb = comb.dropna() >> su.mutate(sign = su.if_else(_.imbalance > 0, 1, -1))

clean_comb.iloc[0]