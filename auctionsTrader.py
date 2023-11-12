import pandas as pd
import numpy  as np
from numpy.random import randn 
import math
import random

sigma = 1
mu    = 10

mgp_prices = sigma * randn(24) + mu
mi1_prices = sigma * randn(24) + mu
mi2_prices = sigma * randn(24) + mu
mi3_prices = sigma * randn(24) + mu
mgp_prices = mgp_prices.round(2)
mi1_prices = mi1_prices.round(2)
mi2_prices = mi2_prices.round(2)
mi3_prices = mi3_prices.round(2)

position_to_close = np.repeat(5.0, 24)

auction_prices = {
    'mgp': mgp_prices,
    'mi1': mi1_prices,
    'mi2': mi2_prices,
    'mi3': mi3_prices
}

class auctionsTrader:
    
    def __init__(
        self,
        auction_prices,
        position_to_close
        #mi3_prices lets just avoid mi3 prices for a moment
        ):
        
        self.auction_prices    = auction_prices  
        self.position_to_close = position_to_close
        self.cost = 0
        
    def print_postion_to_close(self):
        print(self.position_to_close)
        
        
    def print_sum_of_imbalance(self):
        print("sum of imbalance")
        print(self.position_to_close.sum())
        
    def insert_bid(self, hour, qty, price, market):
        clearing_price = self.auction_prices[market][hour]
        if price > clearing_price:
            self.position_to_close[hour] = position_to_close[hour] - qty
            print(f'bid hour {hour} filled @ {clearing_price:.2f}')
            self.cost += qty * clearing_price
    
    def run_mgp_session(self, price, share):
        for hour, value in enumerate(self.position_to_close):
            self.insert_bid(
                hour = hour, 
                qty = share * position_to_close[hour], 
                price = price, 
                market = 'mgp'
                )
    
    def run_mi_session(self, market, share, markup, reference_market):
        for hour, value in enumerate(self.position_to_close):
            self.insert_bid(
                hour = hour,
                qty = share * position_to_close[hour],
                price = self.auction_prices[reference_market][hour] * (1 + markup),
                market=market
            )


instance = auctionsTrader(
    auction_prices=auction_prices, 
    position_to_close=position_to_close
    )

instance.run_mgp_session(price = 10, share = 0.5)
instance.print_postion_to_close()
instance.run_mi_session(market='mi1', share = 0.3, markup=0.03, reference_market='mgp')
instance.print_postion_to_close()
instance.run_mi_session(market='mi2', share = 1, markup=0.1, reference_market='mgp')
instance.print_postion_to_close()
instance.print_sum_of_imbalance()
