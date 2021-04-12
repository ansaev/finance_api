from _decimal import Decimal
from datetime import datetime
from typing import Optional


class Wallet():
    def __init__(self, id: int, balance: Decimal, created_at: datetime):
        self.id  = id
        self.balance = balance
        self.created_at = created_at

    def dict(self) -> dict:
        return {"id": self.id, "balance": self.balance, "created_at": self.created_at}

class Transaction():
    def __init__(self, id: int, from_wallet: Optional[int], to_wallet: int, amount: Decimal, created_at: datetime):
        self.id  = id
        self.amount = amount
        self.created_at = created_at
        self.from_wallet = from_wallet
        self.to_wallet = to_wallet

    def dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "created_at": self.created_at,
            "from_wallet": self.from_wallet,
            "to_wallet": self.to_wallet,
        }
