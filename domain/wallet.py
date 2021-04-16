from _decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Wallet(BaseModel):
    id: int
    balance: Decimal
    created_at: datetime


class Transaction(BaseModel):
    id: int
    from_wallet: Optional[int]
    to_wallet: int
    amount: Decimal
    created_at: datetime
