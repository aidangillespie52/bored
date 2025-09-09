from enum import Enum
from dataclasses import dataclass, field
import uuid
from typing import List

def generate_id() -> str:
    return str(uuid.uuid4())
    
class ReportStatus(Enum):
    FILLED = 0
    PARTIAL = 1
    RESTING = 2

@dataclass
class Order:
    price: float
    qty: float

@dataclass
class ExecutionReport:
    ticker: str
    total_qty: float
    fills: list = field(default_factory=list)
    id: str = field(default_factory=generate_id)

    
    def add_fill(self, o: Order) -> None:
        if self.status == ReportStatus.FILLED:
            raise RuntimeError("Order has already been filled.")
        
        print('Order received:', o)
        self.fills.append(o)
    
    @property
    def status(self) -> ReportStatus:
        if len(self.fills) == 0:
            return ReportStatus.RESTING

        if self.remaining_qty == 0:
            return ReportStatus.FILLED

        return ReportStatus.PARTIAL
    
    @property
    def filled_qty(self) -> float:
        if self.fills:
            return sum(map(lambda x: x.qty, self.fills))

    @property
    def remaining_qty(self) -> float:
        filled_qty = self.filled_qty
        return self.total_qty - filled_qty
    
    @property
    def avg_fill_price(self) -> float:
        return sum(map(lambda o: o.qty*o.price, self.fills)) / self.filled_qty

if __name__ == '__main__':
    e = ExecutionReport(
        ticker='SPY',
        total_qty=3000,
    )

    e.add_fill(Order(23.20, 1000))
    print(e.avg_fill_price)

    e.add_fill(Order(30, 500))
    print(e.avg_fill_price)

    e.add_fill(Order(30, 1500))
    print(e.avg_fill_price)
    
    print(e.status)