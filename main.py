from decimal import Decimal

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi_asyncpg import configure_asyncpg
from pydantic import BaseModel

from domain.wallet import Transaction, Wallet
from wallet.repo import Repo
from wallet.wallet import WalletService

app = FastAPI(title="Finance API", description="Test project, wallets, transfers, balances",version="1.0.0", )
db = configure_asyncpg(app, "postgresql://finance:finance@0.0.0.0:5432/finance")


tags_metadata = [
    {
        "name": "wallets",
        "description": "Operations with wallets. Top-up, create, transfer, get.",
    },
]

# TODO: remove before using on prod
@db.on_init
async def initialize_db(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS wallet (
            id serial primary key,
            balance decimal not null,
            created_at timestamp not null
        );
        """)
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS transaction (
            id serial primary key,
            amount decimal not null,
            from_wallet integer,
            to_wallet integer not null,
            created_at timestamp not null
        );
        """)


@app.get("/wallets/{wallet_id}", tags=["wallets",], response_model=Wallet)
async def get_wallet(wallet_id, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    wallet_id = int(wallet_id)
    wallet = await service.get_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return wallet.dict()


@app.post("/wallets", tags=["wallets",], response_model=Wallet)
async def create_wallet(db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        wallet = await service.create_wallet()
        return wallet.dict()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex.__str__())


class TopUpForm(BaseModel):
    amount: Decimal


@app.post("/wallets/{wallet_id}/top-up", tags=["wallets",], response_model=Transaction)
async def top_up_wallet(wallet_id, form: TopUpForm, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        transaction = await service.top_up_wallet(int(wallet_id), form.amount)
        return transaction.dict()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex.__str__())


class TransferForm(BaseModel):
    amount: Decimal
    to_wallet: int


@app.post("/wallets/{wallet_id}/transfer", tags=["wallets",], response_model=Transaction)
async def transfer(wallet_id, form: TransferForm, db=Depends(db.connection)):
    repo = Repo(db)
    service = WalletService(repo)

    try:
        transaction = await service.transfer(int(wallet_id), form.to_wallet, form.amount)
        return transaction.dict()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex.__str__())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
