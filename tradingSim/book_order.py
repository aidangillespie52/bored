from enum import Enum
from dataclasses import dataclass, field
import uuid
import time

@dataclass
class Fill:
    price: float
    qty: float
    
def generate_id() -> str:
    return str(uuid.uuid4())
    
class BookOrderStatus(Enum):
    FILLED = 0
    PARTIAL = 1
    RESTING = 2
    
class BookOrderType(Enum):
    BUY = 0
    SELL = 1
    
@dataclass
class BookOrder:
    ticker: str
    price: float
    qty: float
    type_: BookOrderType
    
    # auto info
    fills: list[Fill] = field(default_factory=list)
    id: str = field(default_factory=generate_id)
    timestamp: float = field(default_factory=time.time)
    
    def add_fill(self, f: Fill) -> None:
        if self.status == BookOrderStatus.FILLED:
            raise RuntimeError("Order has already been filled.")
        
        print('Fill received:', f)
        self.fills.append(f)
    
    @property
    def status(self) -> BookOrderStatus:
        if len(self.fills) == 0:
            return BookOrderStatus.RESTING

        if self.remaining_qty == 0:
            return BookOrderStatus.FILLED

        return BookOrderStatus.PARTIAL
    
    @property
    def filled_qty(self) -> float:
        if self.fills:
            return sum(map(lambda x: x.qty, self.fills))
        
        return 0

    @property
    def remaining_qty(self) -> float:
        return self.qty - self.filled_qty
    
    @property
    def avg_fill_price(self) -> float:
        if self.filled_qty:
            return sum(map(lambda o: o.qty*o.price, self.fills)) / self.filled_qty

        return None
    
    def __str__(self) -> str:
        avg_fill = (
            f"{self.avg_fill_price:.2f}" 
            if self.avg_fill_price is not None else "—"
        )
        return (
            f"Order[{self.id}] {self.type_.name} {self.ticker}\n"
            f"@ {self.price:.2f} x {self.qty:.2f}\n"
            f"(status={self.status.name},\n"
            f"filled={self.filled_qty:.2f},\n"
            f"remaining={self.remaining_qty:.2f},\n"
            f"avg_fill={avg_fill})\n"
        )
        
if __name__ == '__main__':
    e = BookOrder(
        'SPY',
        3000,
        BookOrderType.BUY,
    )

    e.add_fill(Fill(23.20, 1000))
    e.add_fill(Fill(30, 500))
    e.add_fill(Fill(30, 1500))