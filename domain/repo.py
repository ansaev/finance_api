from _pydecimal import Decimal
from abc import ABC, abstractmethod
from typing import Optional

from domain.wallet import Wallet


class WaletRepoInterface(ABC):
   @abstractmethod
   async def get_wallet(self, wallet_id) -> Wallet:
       pass
   @abstractmethod
   async def create_wallet(self) -> Wallet:
       pass
   @abstractmethod
   async def transfer(self, from_acc: Optional[int], to_acc: int, amount: Decimal):
       pass