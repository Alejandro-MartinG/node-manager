import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.db.models import Base, Server, Wallet, Balance

load_dotenv()

class DBService:
    def __init__(self, database_path, session=None):
        if not database_path:
            database_path = os.getenv('DB_PATH')

        expanded_path = os.path.expanduser(database_path)
        directory = os.path.dirname(expanded_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        database_path = f'sqlite:///{expanded_path}'

        self.engine = create_engine(database_path, echo=True)

        print(database_path)

        if not session:
            engine = create_engine(database_path, echo=True)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            session = Session()

        self.session = session

    def add_server(self, name, ip, active, username, password, role, os_version, blockchains):
        new_server = Server(
            name=name,
            ip=ip,
            active=active,
            username=username,
            password=password,
            role=role,
            os_version=os_version,
            blockchains=blockchains
        )
        self.session.add(new_server)
        self.session.commit()
        return new_server

    def add_server_list(self, server_list):
        for server_data in server_list:
            self.add_server(
                name=server_data['name'],
                ip=server_data['ip'],
                active=server_data['active'],
                username=server_data['username'],
                password=server_data['password'],
                role=server_data['role'],
                os_version=server_data['os_version'],
                blockchains=server_data['blockchains']
            )
        return True

    def get_server_by_name(self, server_name):
        return self.session.query(Server).filter_by(name=server_name).first()

    def get_server_by_id(self, server_id):
        return self.session.get(Server, server_id)

    def list_servers(self):
        return self.session.query(Server).all()


    def add_wallet(self, address, name, password, mnemonic, blockchain):
        new_wallet = Wallet(
            address=address,
            name=name,
            password=password,
            mnemonic=mnemonic,
            blockchain=blockchain
        )
        self.session.add(new_wallet)
        self.session.commit()
        return new_wallet

    def get_wallet_by_id(self, wallet_id):
        return self.session.get(Wallet, wallet_id)

    def list_wallets(self):
        return self.session.query(Wallet).all()


    def add_balance(self, wallet_id, free, staked, blockchain):
        new_balance = Balance(
            wallet_id=wallet_id,
            free=free,
            staked=staked,
            blockchain=blockchain,
            date=datetime.now()
        )
        self.session.add(new_balance)
        self.session.commit()
        return new_balance

    def get_balance_by_id(self, balance_id):
        return self.session.get(Balance, balance_id)

    def get_balance_by_wallet(self, wallet_name: str):
        wallet = self.session.query(Wallet).filter_by(name=wallet_name).first()
        if wallet is None:
            return None

        balance = self.session.query(Balance).filter_by(wallet_id=wallet.id).first()
        return balance

    def list_balances(self):
        return self.session.query(Balance).all()