from enum import Enum
from dataclasses import dataclass

class ReportStatus(Enum):
    FILLED = 0
    PARTIAL = 1
    RESTING = 2
    
@dataclass
class ExecutionReport:
    status: ReportStatus
    filled_qty: float
    remaining_qty: float
    avg_fill_price: float
    fills: list
    
    # add more if needed