
from datetime import date, timedelta, datetime
import terna
import config
from siuba import group_by, mutate, select, summarize, _, arrange, filter
import pandas as pd
import entsoe_methods
import entsoe


class SbilTrader:

    def __init__(
            self,
            lookback  = 10,
            macrozone = "NORD",
            mgp       = None
    ):
        self.lookback = lookback
        self.macrozone = macrozone

        # all data we need -
        # sbil / prices / mgp / .... in the office easier

        self.data_quartorario = terna.preliminary_macrozonal_imbalance(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            quartorario = True
        )
        self.prices_quartorario = terna.preliminary_prices(
            date_from = date.today() + timedelta(days = - self.lookback),
            date_to   = date.today() + timedelta(days = 1),
            quartorario = False
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

north = instance.data_quartorario >> filter(_.macrozone == "NORD")

## calculate time difference
north >> filter(north['reference_date'] == max(north['reference_date']))

current_time = datetime.now()
rounded_time = current_time.replace(minute=0, second=0, microsecond=0)
first_tradable_hour = rounded_time + timedelta(hours=2)

first_tradable_hour.strftime("%Y-%m-%d %H:%M:%S")