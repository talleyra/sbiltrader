import config
import requests as req
import json
import pandas as pd
from datetime import date, timedelta
from time import sleep
from siuba import group_by, mutate, select, summarize, _, arrange, filter

def terna_token():

    token = req.post(
        url = "https://api.terna.it/transparency/oauth/accessToken",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data = {
            'client_id':     config.terna_client,
            'client_secret': config.terna_secret,
            'grant_type': 'client_credentials'
        }
    )

    resp_decoded = token.content.decode('utf-8')
    resp_data    = json.loads(resp_decoded)
    access_token = resp_data['access_token']
    bearer_token = "Bearer " + access_token

    sleep(2)
    
    return bearer_token

# new function

def macrozonal_imbalance(date_from, date_to, daily = True, quartorario = False, macrozone = None):
    """_summary_

    Args:
        date_from (_type_): _description_
        date_to (_type_): _description_
        daily (bool, optional): _description_. Defaults to True.
        quartorario (bool, optional): _description_. Defaults to False.
        macrozone (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    # Granularity
    if not quartorario:
        granularity = "Orario"
    else:
        granularity = "Quarto Orario"


    if daily:
        type     = "daily-macrozonal-imbalance"
        dict_key = "daily_macrozonal_imbalance"
    else:
        type     = "preliminary-macrozonal-imbalance"
        dict_key = "preliminary_macrozonal_imbalance"
    # Base URL of the API
    base_url = f"https://api.terna.it/market-and-fees/v1.0/{type}"

    # format datetime
    date_from = date_from.strftime("%d/%m/%Y")
    date_to   = date_to.strftime("%d/%m/%Y")

    sleep(2)
    token = terna_token()
    sleep(2)

    # Headers
    headers = {
        'Authorization': token,
         'Accept': 'application/json'
    }

    # Parameters
    params = {
        "dateFrom": date_from,
        "dateTo":   date_to,
        "dataType": granularity
    }


    # Send a GET request to the API
    response = req.get(base_url, params=params, headers=headers)

    data_json = response.json()
    data = pd.DataFrame(data_json[dict_key])
    
    data = (
    data >>
        mutate(
            publication_date = pd.to_datetime(data['publication_date']),
            reference_date   = pd.to_datetime(data['reference_date']),
            imbalance        = pd.to_numeric(data['zonal_aggregate_unbalance_MWh']),
            exchanges        = pd.to_numeric(data['exchanges_MWh']),
            foreign          = pd.to_numeric(data['foreign_MWh']),
        ) >>
        select(
            _.publication_date,
            _.reference_date, 
            _.imbalance,
            _.exchanges,
            _.foreign,
            _.macrozone
        )
    )

    if macrozone is not None:
        data = (
            data >> 
                filter(_.macrozone == macrozone)
        )

    return data
   


# prices

def imbalance_prices(date_from, date_to, daily = True, quartorario = False, macrozone = None):
    
    # Granularity
    if not quartorario:
        granularity = "Orario"
    else:
        granularity = "Quarto Orario"

    if daily:
        type     = "daily-prices"
        dict_key = "daily_prices" 
    else: 
        type     = "preliminary-prices"
        dict_key = "preliminary_prices"

    # Base URL of the API
    base_url = f"https://api.terna.it/market-and-fees/v1.0/{type}"

    # format datetime
    date_from = date_from.strftime("%d/%m/%Y")
    date_to   = date_to.strftime("%d/%m/%Y")

    token = terna_token()

    # Headers
    headers = {
        'Authorization': token,
        'Accept': 'application/json'
    }

    # Parameters
    params = {
        "dateFrom": date_from,
        "dateTo":   date_to,
        "dataType": granularity
    }


    # Send a GET request to the API
    response = req.get(base_url, params=params, headers=headers)

    if response.status_code != 200:
        print("error")
        print(response.content)

    data_json = response.json()
    data = pd.DataFrame(data_json[dict_key])

    data = (
        data >>
            mutate(
                publication_date = pd.to_datetime(data["publication_date"]),
                reference_date   = pd.to_datetime(data["reference_date"]),
                imbalance_price = pd.to_numeric(data["unbalance_price_EURxMWh"])
            ) >>
            select(
                _.publication_date,
                _.reference_date,
                _.macrozone,
                _.imbalance_price
            )
    )
    
    if macrozone is not None:
        data = (
            data >> 
                filter(_.macrozone == macrozone)
        )

    return data
   



def get_total_load(date_from, date_to, bidding_zone = "NORD"):
    

    # Base URL of the API
    base_url = f"https://api.terna.it/transparency/v1.0/gettotalload"

    # format datetime
    date_from = date_from.strftime("%d/%m/%Y")
    date_to   = date_to.strftime("%d/%m/%Y")

    sleep(2)
    token = terna_token()
    sleep(2)
    # Headers
    headers = {
        'Authorization': token
    }

    # Parameters
    params = {
        "dateFrom": date_from,
        "dateTo":   date_to,
        "biddingZone": bidding_zone
    }


    # Send a GET request to the API
    response = req.get(base_url, params=params, headers=headers)
    data_json = response.json()
    data = pd.DataFrame(data_json['totalLoad'])
    
    return data
   
