from collections import deque
from dataclasses import dataclass
import uuid

@dataclass
class Order:
    price: float
    volume: float

class OrderBook:
    def __init__(self):
        self.bids: dict[float: deque] = {}
        self.asks: dict[float: deque] = {}
        self.order_reports: dict[str: ExecutionReport]
        
    def check_cross(self):
        max_bid = max(self.bids)
        min_ask = min(self.asks)
        
        # exit if no prices have entered
        if not min_ask or not max_bid:
            return
        
        # exit if prices don't cross        
        if min_ask > max_bid:
            return

        bid_order = self.bids[max_bid].pop()
        ask_order = self.bids[min_ask].pop()
        
        # TODO: implement filling shares until cross isn't true
        if ask_order.volume > bid_order.volume:
            ask_order.volume -= bid_order.volume
                    
    async def place_limit_buy(self, o: Order):
        price = o.price
        if not self.bids.get(price):
            self.bids[price] = deque()
        
        self.bids[price].append(o)
        
        self.check_cross()
        
        return await self.check_order(o)
        
    async def place_limit_sell(self, o: Order):
        price = o.price
        if not self.asks.get(price):
            self.asks[price] = deque()
            
        self.asks[price].append(o)
        
        self.check_cross()