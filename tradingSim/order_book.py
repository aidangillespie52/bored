from collections import deque
from book_order import BookOrder, BookOrderType, Fill
import numpy as np
import pandas as pd
import mplfinance as mpf
import random
import time
from datetime import datetime

class OrderBook:
    def __init__(self):
        self.bids: dict[float: deque] = {}
        self.asks: dict[float: deque] = {}
        self.trades: list[tuple[float, float, float]] = []  
        
    def check_cross(self):
        while True:
            pop_both = False
            
            if not self.bids or not self.asks:
                return
            
            
            max_bid = max(self.bids)
            min_ask = min(self.asks)
            
            if not self.bids[max_bid] or not self.asks[min_ask]:
                if self.bids.get(max_bid) and not self.bids[max_bid]:
                    del self.bids[max_bid]
                if self.asks.get(min_ask) and not self.asks[min_ask]:
                    del self.asks[min_ask]
                return
            
            # exit if prices don't cross        
            if min_ask > max_bid:
                return

            bid_order: BookOrder = self.bids[max_bid][0]
            ask_order: BookOrder = self.asks[min_ask][0]
            
            qty = min(bid_order.remaining_qty, ask_order.remaining_qty)
            exec_price = max_bid if bid_order.timestamp < ask_order.timestamp else min_ask
            
            bid_order.add_fill(Fill(price=exec_price, qty=qty))
            ask_order.add_fill(Fill(price=exec_price, qty=qty))
            
            if bid_order.remaining_qty <= 1e-12:
                self.bids[max_bid].popleft()
                if not self.bids[max_bid]:
                    del self.bids[max_bid]

            if ask_order.remaining_qty <= 1e-12:
                self.asks[min_ask].popleft()
                if not self.asks[min_ask]:
                    del self.asks[min_ask]
            
            self.trades.append((time.time(), exec_price, qty))
            
    def place_limit_order(self, order: BookOrder):
        price = order.price
        target_dict = None
        
        if order.type_ == BookOrderType.BUY:
            target_dict = self.bids
        else:
            target_dict = self.asks
                
        if not target_dict.get(price):
            target_dict[price] = deque()
        
        target_dict[price].append(order)
        
        self.check_cross()
    
    def place_market_order(self, order: BookOrder):
        qty_remaining = order.qty
        fills = []

        if order.type_ == BookOrderType.BUY:
            # consume from the ask side (lowest prices first)
            while qty_remaining > 1e-12 and self.asks:
                best_ask = min(self.asks)
                ask_queue = self.asks[best_ask]
                ask_order = ask_queue[0]

                trade_qty = min(qty_remaining, ask_order.remaining_qty)
                exec_price = best_ask

                # fill both
                order.add_fill(Fill(price=exec_price, qty=trade_qty))
                ask_order.add_fill(Fill(price=exec_price, qty=trade_qty))
                self.trades.append((time.time(), exec_price, trade_qty))
                fills.append((exec_price, trade_qty))

                qty_remaining -= trade_qty

                if ask_order.remaining_qty <= 1e-12:
                    ask_queue.popleft()
                    if not ask_queue:
                        del self.asks[best_ask]

        else:  # SELL
            # consume from the bid side (highest prices first)
            while qty_remaining > 1e-12 and self.bids:
                best_bid = max(self.bids)
                bid_queue = self.bids[best_bid]
                bid_order = bid_queue[0]

                trade_qty = min(qty_remaining, bid_order.remaining_qty)
                exec_price = best_bid

                order.add_fill(Fill(price=exec_price, qty=trade_qty))
                bid_order.add_fill(Fill(price=exec_price, qty=trade_qty))
                self.trades.append((time.time(), exec_price, trade_qty))
                fills.append((exec_price, trade_qty))

                qty_remaining -= trade_qty

                if bid_order.remaining_qty <= 1e-12:
                    bid_queue.popleft()
                    if not bid_queue:
                        del self.bids[best_bid]

        return fills