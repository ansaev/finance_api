from typing import Optional

from decimal import Decimal
from fastapi import FastAPI, Depends
from fastapi_asyncpg import configure_asyncpg
from pydantic import BaseModel

from wallet.repo import Repo
from wallet.wallet import WalletService

app = FastAPI()
db = configure_asyncpg(app, "postgresql://finance:finance@0.0.0.0:5432/finance")


# TODO: remove before using on prod
@db.on_init
async def initialize_db(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS wallet (
            id serial primary key,
            balance decimal not null,
            created_at time not null
        );
        """)
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS transaction (
            id serial primary key,
            amount decimal not null,
            from_wallet integer,
            to_wallet integer not null,
            created_at time not null
        );
        """)


@app.get("/wallets/{wallet_id}")
async def get_wallet(wallet_id, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    wallet_id = int(wallet_id)
    wallet = await service.get_wallet(wallet_id)
    if wallet is None:
        return {"status": 404, "error": "not found"}
    return wallet.dict()

@app.post("/wallets")
async def create_wallet(db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        wallet = await service.create_wallet()
        return wallet.dict()
    except Exception as ex:
        return {"status": 500, "error": ex.__str__()}


class TopUpForm(BaseModel):
    amount: Decimal

@app.post("/wallets/{wallet_id}/top-up")
async def top_up_wallet(wallet_id, form: TopUpForm, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        transaction = await service.top_up_wallet(int(wallet_id), form.amount)
        return transaction.dict()
    except Exception as ex:
        return {"status": 500, "error": ex.__str__()}

class TransferForm(BaseModel):
    amount: Decimal
    to_wallet: int

@app.post("/wallets/{wallet_id}/transfer")
async def top_up_wallet(wallet_id, form: TransferForm, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        transaction = await service.transfer(int(wallet_id), form.to_wallet, form.amount)
        return transaction.dict()
    except Exception as ex:
        return {"status": 500, "error": ex.__str__()}