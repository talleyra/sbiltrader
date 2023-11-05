
from datetime import date, timedelta, datetime
import terna
import config
from siuba import group_by, mutate, select, summarize, _, arrange, filter, count
import siuba as su
import pandas as pd
import entsoe_methods
import entsoe


class SbilTrader:

    def __init__(
            self,
            lookback  = 10,
            macrozone = "NORD",
            data_quartorario_preliminare = None,
            prices_quartorario_preliminare = None,
            data_quartorario_daily = None,
            prices_quartorario_daily = None,
            mgp       = None,
            scheduled_exchanges = None,
            physical_flows = None,
            load_forecast = None,
            load_forecasts_neighbours = None
    ):
        self.lookback = lookback
        self.macrozone = macrozone

        # all data we need -
        # sbil / prices / mgp / .... in the office easier

        self.data_quartorario_preliminare = terna.macrozonal_imbalance(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            daily = False,
            quartorario = True,
            macrozone = self.macrozone
        )

        self.prices_quartorario_preliminare = terna.imbalance_prices(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            daily     = False,
            quartorario = False,
            macrozone = self.macrozone
        )

        self.data_quartorario_daily = terna.macrozonal_imbalance(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            daily = True,
            quartorario = True,
            macrozone = self.macrozone
        )

        self.prices_quartorario_daily = terna.imbalance_prices(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            daily = True,
            quartorario = True,
            macrozone = self.macrozone
        )

        self.prices_preliminare_orario = terna.imbalance_prices(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            daily = True,
            quartorario = False,
            macrozone = self.macrozone
        )

        # mgp prices
        self.mgp = entsoe_methods.mgp(zone = self.macrozone, lookback=self.lookback)
        # scheduled exchanges
        self.scheduled_exchanges = entsoe_methods.scheduled_exchanges(area=entsoe.Area.IT_NORD, lookback=self.lookback)
        # physical flows cross border
        self.physical_flows = entsoe_methods.physical_flows(area = entsoe.Area.IT_NORD, lookback=self.lookback)
        # own load forecast
        self.load_forecast = entsoe_methods.load_and_forecast(area = entsoe.Area.IT_NORD, lookback=self.lookback)
        # load forecasts neighbours
        self.load_forecasts_neighbours = entsoe_methods.load_and_forecast_neighbours(area = entsoe.Area.IT_NORD, lookback=self.lookback)
        ## get probability for horizon on axis 
        # - based on current sign
        # - based on 24 lags
        # - based on level of imbalance and the probability of changing
        # - based on a model random forest

        ## get price estimation
        # - price based on mgp


instance = SbilTrader()


import pytimetk as tk
import siuba as su

qo = su.filter(instance.data_quartorario_daily, _.macrozone == "NORD")

from plotnine import ggplot, aes, geom_line

(
    qo >>
    ggplot() + 
    geom_line(aes(x = "reference_date", y = "imbalance"))
)

dprep = su.select(qo, _.reference_date, _.imbalance)


dprep['ma1'] = dprep['imbalance'].diff().rolling(8).mean()
dprep['ma2'] = dprep['imbalance'].rolling(16).mean()

import numpy as np

newdf = dprep.dropna()
stat = (
     newdf >>
        mutate(
            strategy = su.if_else(
                _.ma1 >= _.ma2, "lungo", "corto"
            )
        )
)


stat[400:450]

import pandera as pa

pa.infer_schema(instance.data_quartorario_daily).to_yaml()
