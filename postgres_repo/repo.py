from datetime import datetime
from _decimal import Decimal
from typing import Optional

from domain.wallet import Wallet, Transaction
from domain.repo import WaletRepoInterface


class Repo(WaletRepoInterface):
    def __init__(self, db):
        self.db = db

    async def transfer(self, from_acc: Optional[int], to_acc: int, amount: Decimal) -> Transaction:
        from_locked = False
        to_locked = False
        tx_id = 0
        created_at = datetime.now()

        if from_acc is not None and from_acc == to_acc:
            raise Exception("cannot transfer from account to the same account")

        async with self.db.transaction():
            try:
                # loc wallet`s balances
                await self.db.execute("SELECT pg_advisory_lock(id) FROM wallet WHERE id = $1;", to_acc)
                to_locked = True
                if from_acc is not None:
                    await self.db.execute("SELECT pg_advisory_lock(id) FROM wallet WHERE id = $1;", from_acc)
                    from_locked = True

                # check from balance
                from_wallet_balance = Decimal(0)
                if from_acc is not None:
                    from_wallet = await self.get_wallet(from_acc)
                    if from_wallet.balance < amount:
                        raise Exception("balance too low")
                    from_wallet_balance = from_wallet.balance

                # insert transaction
                await self.db.execute(
                    "INSERT INTO transaction (from_wallet, to_wallet, amount, created_at) values ($1, $2, $3, $4)",
                    from_acc, to_acc, amount, created_at
                )
                tx_id = await self.db.fetchval("SELECT currval(pg_get_serial_sequence('transaction','id'))")

                # change balances
                if from_acc is not None:
                    await self.db.execute(
                        "UPDATE wallet SET balance = $1 where id = $2", from_wallet_balance - amount, from_acc)
                await self.db.execute(
                    "UPDATE wallet SET balance = balance + $1 where id = $2", amount, to_acc)
            # unlock wallets
            finally:
                if from_locked:
                    await self.db.execute("SELECT pg_advisory_unlock(id) FROM wallet WHERE id = $1;", from_acc)
                if to_locked:
                    await self.db.execute("SELECT pg_advisory_unlock(id) FROM wallet WHERE id = $1;", to_acc)

        return Transaction(id=tx_id, amount=amount, created_at=created_at, from_wallet=from_acc, to_wallet=to_acc)

    async def create_wallet(self) -> Wallet:
        balance = Decimal(0)
        created_at = datetime.now()
        async with self.db.transaction():
            await self.db.execute("INSERT INTO wallet (balance, created_at) values ($1, $2)", balance, created_at)
            wallet_id = await self.db.fetchval("SELECT currval(pg_get_serial_sequence('wallet','id'))")
        return Wallet(id=wallet_id, balance=balance, created_at=created_at)

    async def get_wallet(self, wallet_id: int) -> Wallet:
        obj = await self.db.fetchrow("SELECT id, balance, created_at FROM wallet where id = $1", wallet_id)
        return obj if obj is None else Wallet(**dict(obj))
