import entsoe
from datetime import date, timedelta
from pandas import Timestamp
import config
import pandas as pd

def mgp(zone = "NORD", lookback = 10):

    if zone == "NORD":
        area_code = entsoe.Area.IT_NORD
    else: 
        area_code = entsoe.Area.IT_SUD

    client = entsoe.EntsoePandasClient(
        api_key=config.entsoe
    )

    date_from = date.today() + timedelta(days = - lookback)
    date_to   = date.today() + timedelta(days = 1)

    start_date = Timestamp(date_from, tz = "Europe/Berlin")
    end_date   = Timestamp(date_to, tz = "Europe/Berlin")

    prices = client.query_day_ahead_prices(
        country_code=area_code,
        start = start_date, end = end_date
    )

    df_index = prices.reset_index()
    df_index.columns = ["date", "prices"]

    return df_index

key = config.entsoe


client = entsoe.EntsoePandasClient(
    api_key=key
)



def scheduled_exchanges(area = entsoe.Area.IT_NORD, lookback = 10):

    zone_name = area.name
    neighbours = entsoe.mappings.NEIGHBOURS[zone_name]

    date_from = date.today() + timedelta(days = - lookback)
    date_to   = date.today() + timedelta(days = 1)

    start_date = Timestamp(date_from, tz = "Europe/Berlin")
    end_date   = Timestamp(date_to, tz = "Europe/Berlin")

    client = entsoe.EntsoePandasClient(
        api_key=config.entsoe
    )

    li = []

    for i in neighbours:
        print(i)
        try:
            data = client.query_scheduled_exchanges(
                country_code_from=area,
                country_code_to= entsoe.Area[i],
                start=start_date,
                end = end_date
            )

            data = data.reset_index()
            data.columns = ["date", "exchanges"]
            data["zone"] = i
            data["direction"] = "out"
            li.append(data)
        except: print("no data")

        try:
            data = client.query_scheduled_exchanges(
                country_code_from= entsoe.Area[i],
                country_code_to=area,
                start=start_date,
                end = end_date
            )
            data = data.reset_index()
            data.columns = ["date", "exchanges"]
            data["zone"] = i
            data["direction"] = "in"
            li.append(data)
        except: print("no data")

    complete_scheduled_exchanges = pd.concat(li)
    
    return complete_scheduled_exchanges





def physical_flows(area = entsoe.Area.IT_NORD, lookback = 10):

    zone_name = area.name
    neighbours = entsoe.mappings.NEIGHBOURS[zone_name]

    date_from = date.today() + timedelta(days = - lookback)
    date_to   = date.today() + timedelta(days = 1)

    start_date = Timestamp(date_from, tz = "Europe/Berlin")
    end_date   = Timestamp(date_to, tz = "Europe/Berlin")

    client = entsoe.EntsoePandasClient(
        api_key=config.entsoe
    )

    li = []

    for i in neighbours:
        print(i)
        try:
            data = client.query_crossborder_flows(
                country_code_from=area,
                country_code_to= entsoe.Area[i],
                start=start_date,
                end = end_date
            )

            data = data.reset_index()
            data.columns = ["date", "flows"]
            data["zone"] = i
            data["direction"] = "out"
            li.append(data)
        except: print("no data")

        try:
            data = client.query_crossborder_flows(
                country_code_from= entsoe.Area[i],
                country_code_to=area,
                start=start_date,
                end = end_date
            )
            data = data.reset_index()
            data.columns = ["date", "flows"]
            data["zone"] = i
            data["direction"] = "in"
            li.append(data)
        except: print("no data")

    complete_flows = pd.concat(li)
    
    return complete_flows





def load_and_forecast_neighbours(area = entsoe.Area.IT_NORD, lookback = 10):

    zone_name = area.name
    neighbours = entsoe.mappings.NEIGHBOURS[zone_name]

    date_from = date.today() + timedelta(days = - lookback)
    date_to   = date.today() + timedelta(days = 1)

    start_date = Timestamp(date_from, tz = "Europe/Berlin")
    end_date   = Timestamp(date_to, tz = "Europe/Berlin")

    client = entsoe.EntsoePandasClient(
        api_key=config.entsoe
    )

    li = []

    for i in neighbours:
        print(i)
        try:
            data = client.query_load_and_forecast(
                country_code=entsoe.Area.IT_NORD,
                start = start_date,
                end = end_date
            )

            data = data.reset_index()
            data.columns = ["date", "forecast", "actual"]
            data["zone"] = i
            li.append(data)
        except: print("no data")

    neighbour_loads = pd.concat(li)
    
    return neighbour_loads




def load_and_forecast(area = entsoe.Area.IT_NORD, lookback = 10):

   
    date_from = date.today() + timedelta(days = - lookback)
    date_to   = date.today() + timedelta(days = 1)

    start_date = Timestamp(date_from, tz = "Europe/Berlin")
    end_date   = Timestamp(date_to, tz = "Europe/Berlin")

    client = entsoe.EntsoePandasClient(
        api_key=config.entsoe
    )

    data = client.query_load_and_forecast(
        country_code=entsoe.Area.IT_NORD,
        start = start_date,
        end = end_date
    )

    data = data.reset_index()
    data.columns = ["date", "forecast", "actual"]
   
    return data

