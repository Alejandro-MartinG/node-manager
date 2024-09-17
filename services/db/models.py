import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

load_dotenv()
secret_key = os.getenv('SALT')

Base = declarative_base()

class Server(Base):
    __tablename__ = 'servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    username = Column(String, nullable=False)
    password = Column(StringEncryptedType(String, secret_key, AesEngine, 'pkcs5'))
    role = Column(String)
    owner = Column(String)
    provider = Column(String)
    os_version = Column(String)
    blockchains = Column(String)  # It can be a list or a foreing key

    def __repr__(self):
        return f"<Server(name='{self.name}', ip='{self.ip}', owner={self.owner}, active={self.active})>"

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(StringEncryptedType(String, secret_key, AesEngine, 'pkcs5'))
    mnemonic = Column(StringEncryptedType(String, secret_key, AesEngine, 'pkcs5'))
    blockchain = Column(String, nullable=False)

    def __repr__(self):
        return f"<Wallet(address='{self.address}', name='{self.name}', blockchain='{self.blockchain}')>"

class Balance(Base):
    __tablename__ = 'balances'
    
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    free = Column(Float, nullable=False, default=0.0)
    staked = Column(Float, nullable=False, default=0.0)
    blockchain = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)

    wallet = relationship("Wallet", back_populates="balances")

    def __repr__(self):
        return f"<Balance(wallet_id={self.wallet_id}, free={self.free}, staked={self.staked}, blockchain='{self.blockchain}, date='{self.date}')>"

Wallet.balances = relationship("Balance", order_by=Balance.id, back_populates="wallet")
