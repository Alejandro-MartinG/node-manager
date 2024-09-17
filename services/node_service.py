import os
import json
from typing import Dict, Optional, List
from registry import Registry
from services.node.node import Node
from services.node.node_role import NodeRole


class NodeService():
    SEEDS_PATH = os.getenv("SEEDS_PATH")

    def __init__(self):
        self.db_manager = Registry.get('db_service')
        self.nodes: Dict[str, Node] = {}

    def load_nodes_from_seeds(self, seeds_path=SEEDS_PATH):
        print("Reading nodes json...")
        self.node_list = self.read_json(seeds_path)
        print("\n")
        print(self.node_list)
        print("\n")
        self.create_nodes(self.node_list)

    def load_nodes_from_db(self, server_list):
        print("\nLoading node list...")
        if (server_list != None):
            for server in server_list:
                node_id = server['id']
                self.nodes = self.db_manager.get_server_by_id(node_id)
        else:
            self.nodes = self.db_manager.get_all_servers()

    def read_json(self, filename):
        data = None
        with open(filename, 'rb') as file:
            data = json.load(file)
        return data

    def create_node(self, name: str, ip: str, username: str, password: str, role: str, os: str, owner: str, blockchains: List[str], ) -> Node:
        node = Node(name, name, ip, username, password, role, os, owner, blockchains, db_manager=self.db_manager)
        self.nodes[name] = node
        return node

    def create_nodes(self, node_list):
        print("\nLoading node list...")

        for server in node_list:
            if (self.get_node_by_ip(server['ip']) is None): 
                self.create_node(server['name'], server['ip'], server['user'], server['password'], server['role'], server['so'], server['owner'], blockchains=server['blockchains'])

        print("Nodes loaded correctly.")
        print(f"{self.list_nodes()}")

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_node_ids(self) -> List[Node]:
        return list(self.nodes.keys())

    def get_node_by_ip(self, ip: str) -> Optional[Node]:
        for node in self.nodes.values():
            if node.ip == ip:
                return node
        return None

    def get_nodes_by_name(self, names: List[str]) -> List[Node]:
        return [node for node in self.nodes.values() if node.name in names]

    def list_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def get_nodes_with_blockchain(self, blockchain: str) -> List[Node]:
        return [node for node in self.nodes.values() if blockchain in node.blockchains]

    def get_nodes_without_blockchain(self, blockchain: str) -> List[Node]:
        return [node for node in self.nodes.values() if blockchain not in node.blockchains]

    def update_node_blockchains(self, node_id: str, blockchains: List[str]):
        node = self.nodes.get(node_id)
        if node:
            node.blockchains = set(blockchains)

    def get_active_nodes(self) -> List[Node]:
        return [node for node in self.nodes.values() if node.active]

    def get_nodes_by_role(self, role: NodeRole) -> List[Node]:
        return [node for node in self.nodes.values() if node.role == role]

    def activate_node(self, node_id: str):
        node = self.nodes.get(node_id)
        if node:
            node.active = True

    def deactivate_node(self, node_id: str):
        node = self.nodes.get(node_id)
        if node:
            node.active = False
