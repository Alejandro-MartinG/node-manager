import uuid
from typing import Dict, List
from services.db.db_service import DBService
from services.node.node_role import NodeRole
import hashlib
from getpass import getpass

class Node:
    def __init__(
            self,
            id: uuid.UUID,
            name: str,
            ip: str,
            username: str,
            password: str,
            role: NodeRole,
            os_version: str,
            owner: str,
            blockchains: List[str] = [] ,
            active: bool = False,
            execution_type: str = "remote",
            port = 22,
            db_manager: DBService = None,
    ):
        self.id = id
        self.name = name
        self.ip = ip
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.os_version = os_version
        self.blockchains = set(blockchains)
        self.owner = owner
        self.port = port
        self.execution_type = execution_type
        self.db_manager = db_manager
        self.active = active

    def __repr__(self):
        return f"ID: {self.id}, Name: {self.name}, IP: {self.ip}, User: {self.username}, Role: {self.role}, Os_version: {self.os_version}, Owner: {self.owner}, Execution_mode: {self.execution_type}, Active: {self.active}"

    def add_blockchain(self, blockchain: str):
        self.blockchains.add(blockchain)

    def remove_blockchain(self, blockchain: str):
        self.blockchains.discard(blockchain)

    def get_ssh_login_params(self) -> Dict[str, str]:
        return self.ip, self.username, self.password

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
