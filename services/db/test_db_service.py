import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.db.models import Base
from services.db.db_service import DBService

TEST_DATABASE_PATH = "sqlite:///:memory:"

# TODO: same test but using Object to fill the models

@pytest.fixture(scope="function")
def db_service():
    # Config test db
    engine = create_engine(TEST_DATABASE_PATH, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    db_service = DBService(database_path=TEST_DATABASE_PATH, session=session)
    yield db_service
    # Teardown: delete tables and close session
    Base.metadata.drop_all(engine)
    session.close()

# Servers
def test_add_server(db_service: DBService):
    server = db_service.add_server(
        name="Test Server",
        ip="192.168.1.1",
        active=True,
        username="admin",
        password="password",
        role="server",
        os_version="Ubuntu 18.04",
        blockchains="Bitcoin,Ethereum"
    )
    assert server is not None
    assert server.name == "Test Server"
    retrieved_server = db_service.get_server_by_id(server.id)
    assert retrieved_server is not None
    assert retrieved_server.name == "Test Server"

    retrieved_server_by_name = db_service.get_server_by_name(server.name)
    assert retrieved_server_by_name is not None
    assert retrieved_server.name == "Test Server"
    assert server.name == retrieved_server.name

def test_get_server_by_id_not_found(db_service: DBService):
    # Try to get and non existence server
    server = db_service.get_server_by_id(999)
    assert server is None

# Wallets
def test_add_wallet(db_service):
    wallet = db_service.add_wallet(
        address="0x123",
        name="Test Wallet",
        password="wallet_password",
        mnemonic="test mnemonic",
        blockchain="Ethereum"
    )
    assert wallet is not None
    assert wallet.name == "Test Wallet"
    # Verify that the wallet can be retrieve from db
    retrieved_wallet = db_service.get_wallet_by_id(wallet.id)
    assert retrieved_wallet is not None
    assert retrieved_wallet.name == "Test Wallet"

# Balances
def test_add_balance(db_service):
    wallet = db_service.add_wallet(
        address="0x123",
        name="Test Wallet",
        password="wallet_password",
        mnemonic="test mnemonic",
        blockchain="Ethereum"
    )
    balance = db_service.add_balance(
        wallet_id=wallet.id,
        free=100.0,
        staked=50.0,
        blockchain="Ethereum"
    )
    assert balance is not None
    assert balance.free == 100.0
    retrieved_balance = db_service.get_balance_by_id(balance.id)
    assert retrieved_balance is not None
    assert retrieved_balance.free == 100.0

def test_add_server_missing_fields(db_service):
    with pytest.raises(TypeError):
        db_service.add_server(
            name="Incomplete Server",
            ip="192.168.1.2",
            active=True,
            username="admin",
            # password is missing
            role="server",
            os_version="Ubuntu 20.04",
            blockchains="Bitcoin,Ethereum"
        )

def test_list_servers_empty(db_service):
    servers = db_service.list_servers()
    assert servers == []

def test_list_servers_with_data(db_service):
    db_service.add_server(
        name="Server One",
        ip="192.168.1.1",
        active=True,
        username="admin",
        password="password",
        role="server",
        os_version="Ubuntu 18.04",
        blockchains="Bitcoin,Ethereum"
    )
    db_service.add_server(
        name="Server Two",
        ip="192.168.1.2",
        active=False,
        username="user",
        password="password",
        role="backup",
        os_version="Ubuntu 20.04",
        blockchains="Bitcoin"
    )
    servers = db_service.list_servers()
    assert len(servers) == 2
    assert servers[0].name == "Server One"
    assert servers[1].name == "Server Two"

def test_list_wallets_empty(db_service):
    wallets = db_service.list_wallets()
    assert wallets == []

def test_list_wallets_with_data(db_service):
    db_service.add_wallet(
        address="0x123",
        name="Wallet One",
        password="password",
        mnemonic="mnemonic one",
        blockchain="Ethereum"
    )
    db_service.add_wallet(
        address="0x456",
        name="Wallet Two",
        password="password",
        mnemonic="mnemonic two",
        blockchain="Bitcoin"
    )
    wallets = db_service.list_wallets()
    assert len(wallets) == 2
    assert wallets[0].name == "Wallet One"
    assert wallets[1].name == "Wallet Two"

def test_list_balances_empty(db_service):
    balances = db_service.list_balances()
    assert balances == []

def test_list_balances_with_data(db_service):
    wallet = db_service.add_wallet(
        address="0x123",
        name="Wallet One",
        password="password",
        mnemonic="mnemonic one",
        blockchain="Ethereum"
    )
    db_service.add_balance(
        wallet_id=wallet.id,
        free=100.0,
        staked=50.0,
        blockchain="Ethereum"
    )
    db_service.add_balance(
        wallet_id=wallet.id,
        free=200.0,
        staked=100.0,
        blockchain="Bitcoin"
    )
    balances = db_service.list_balances()
    assert len(balances) == 2
    assert balances[0].free == 100.0
    assert balances[1].free == 200.0

def test_add_wallet_duplicate_address(db_service):
    db_service.add_wallet(
        address="0x123",
        name="Wallet One",
        password="password",
        mnemonic="mnemonic one",
        blockchain="Ethereum"
    )
    with pytest.raises(Exception):  # TODO: add exception types
        db_service.add_wallet(
            address="0x123",  # Duplicated address 
            name="Wallet Two",
            password="password",
            mnemonic="mnemonic two",
            blockchain="Bitcoin"
        )
