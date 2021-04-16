from decimal import *
from domain.repo import WaletRepoInterface
from domain.wallet import Wallet, Transaction


class WalletService:
    def __init__(self, repo: WaletRepoInterface):
        self.repo = repo

    async def get_wallet(self, wallet_id:int) -> Wallet:
        return await self.repo.get_wallet(wallet_id=wallet_id)

    async def create_wallet(self) -> Wallet:
        return await self.repo.create_wallet()

    async def top_up_wallet(self, wallet_id: int, amount:Decimal) -> Transaction:
        return  await self.repo.transfer(from_acc=None, to_acc=wallet_id, amount=amount)

    async def transfer(self, from_acc: int, to_acc: int, amount: Decimal) -> Transaction:
        return await self.repo.transfer(from_acc=from_acc, to_acc=to_acc, amount=amount)
