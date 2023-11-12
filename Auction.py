import pandas as pd
import xml.etree.ElementTree as ET
import rich
import siuba as su
from siuba import _
from plotnine import ggplot, aes, geom_line, geom_hline, geom_point
import numpy as np


class Auction:
    
    def __init__(self, file, zone):
        
        self.file = file
        self.zone = zone
        self.data = self.read_file()
        self.sell_orders, self.buy_orders = self.split_buy_sell_orders()
        
    def read_file(self):
        
        root = ET.parse(self.file)
        data = []

        for domanda_offerta in root.findall('.//DomandaOfferta'):
            row_data = {}
            for element in domanda_offerta:
                row_data[element.tag] = element.text
            data.append(row_data)

        parsed_data = pd.DataFrame(data)
        
        parsed_data['ZonaMercato'] = parsed_data['ZonaMercato'].str.split(";")
        zone_df = parsed_data[parsed_data['ZonaMercato'].apply(lambda x: self.zone in x)]

        parsed_df = (
            zone_df >>
                su.mutate(
                Data = pd.to_datetime(zone_df['Data'], format='%Y%m%d'),
                Ora=pd.to_numeric(zone_df['Ora']),
                PrezzoZonale=pd.to_numeric(zone_df['PrezzoZonale']),
                Quantita=pd.to_numeric(zone_df['Quantita']),
                Prezzo=pd.to_numeric(zone_df['Prezzo'])
                )
        )
        
        parsed_df.columns = parsed_df.columns.str.lower()
        
        return parsed_df
    
    def split_buy_sell_orders(self):
        
        sell_orders = self.data[self.data['tipo'] == 'OFF']
        buy_orders  = self.data[self.data['tipo'] == 'BID']
        
        return sell_orders, buy_orders
        
    def single_hour_data(self, hour):
        
        sell_orders = (
            self.sell_orders >>
                su.filter(_.ora == hour) >>
                su.arrange(_.prezzo) >>
                su.mutate(cqty = _.quantita.cumsum())
        )

        buy_orders = (
            self.buy_orders >>
                su.filter(_.ora == hour) >>
                su.arrange( - _.prezzo) >>
                su.mutate(cqty = _.quantita.cumsum())
        )
        
        orders = {
            'buy_orders' : buy_orders,
            'sell_orders': sell_orders
        }
        
        return orders
    
    def plot_orders(self, hour, lens = None):
                
        orders = self.single_hour_data(hour = hour)

        sell_orders = orders['sell_orders']
        buy_orders = orders['buy_orders']

        if lens is not None:
            sell_orders = (
                sell_orders >>
                su.filter(abs(_.prezzo - _.prezzozonale) < lens)
            )
            
            buy_orders = (
                buy_orders  >>
                    su.filter(abs(_.prezzo - _.prezzozonale) < lens)
                )
            
        plt = (
            ggplot() + 
                geom_line(sell_orders, aes(x = "cqty", y = "prezzo"))+
                geom_point(sell_orders, aes(x = "cqty", y = "prezzo"))+
                geom_line(buy_orders, aes(x = "cqty", y = "prezzo"), color = "red")+
                geom_point(buy_orders, aes(x = "cqty", y = "prezzo"), color = "red")+
                geom_hline(yintercept = buy_orders['prezzozonale'].iloc[0])
        )
        
        return plt
    
    def sensitivity(self, hour, type = "sell", start = -200.0, to = 200.0, by = 20):
        
        data = auction.single_hour_data(hour = hour)

        if type == "sell":    
            orders = data['sell_orders']
            orders['acc'] = np.where(orders['prezzo'] <= orders['prezzozonale'], 'acc', 'not')
            idx = orders[orders['acc'] == 'acc']['prezzo'].idxmax()
            
        if type == "buy":
            orders = data['buy_orders']
            orders['acc'] = np.where(orders['prezzo'] >= orders['prezzozonale'], 'acc', 'not')
            idx = orders[orders['acc'] == 'acc']['prezzo'].idxmin()
            
        marginal_order = orders.loc[idx]
        print(marginal_order)
        cumqty = orders.loc[idx].cqty
        print(cumqty)
        
        def step_interpolate_prezzo(cumqty):
            index = np.searchsorted(orders['cqty'], cumqty) - 1
            return orders['prezzo'].iloc[index]

        cqty_values = np.arange(start, to, by) + marginal_order.cqty

        for cqty in cqty_values:
            prezzo = step_interpolate_prezzo(cqty)
            print(f"cqty: {cqty:.2f}, diffqty: {cqty - marginal_order.cqty}, step-interpolated prezzo={prezzo:.2f}, diff: {prezzo - marginal_order.prezzo:.2f}")




        
file = "./TuttoIpex20230101_20230102/20230101MI-A1DomandaOfferta.xml"
zone = 'NORD'

auction = Auction(file = file, zone = zone)


auction.sensitivity(hour = 5, start = -100.0, to = 100.0, by = 10)