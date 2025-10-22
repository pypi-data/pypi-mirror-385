#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import socket
from typing import Any, List

from eth_typing import ChecksumAddress, HexStr

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.types.node import FairNode, NodeId, Port
from skale.utils import helper


class Nodes(BaseContract):
    def __get_raw(self, node_id: NodeId) -> List[Any]:
        return list(self.contract.functions.getNode(node_id).call())

    def get(self, node_id: NodeId) -> FairNode:
        return self._to_node(self.__get_raw(node_id))

    def get_id(self, address: ChecksumAddress) -> NodeId:
        return self.contract.functions.getNodeId(address).call()

    def get_by_address(self, address: ChecksumAddress) -> FairNode:
        node_id = self.get_id(address)
        return self.get(node_id)

    def get_passive_node_ids_for_address(self, node_address: ChecksumAddress) -> list[NodeId]:
        return self.contract.functions.getPassiveNodeIdsForAddress(node_address).call()

    def get_passive_node_ids(self) -> list[NodeId]:
        return self.contract.functions.getPassiveNodeIds().call()

    def get_active_node_ids(self) -> list[NodeId]:
        return self.contract.functions.getActiveNodeIds().call()

    def active_node_exists(self, node_id: NodeId) -> bool:
        return self.contract.functions.activeNodeExists(node_id).call()

    def passive_node_exists(self, node_id: NodeId) -> bool:
        return self.contract.functions.passiveNodeExists(node_id).call()

    def get_owner_change_request(self, node_id: NodeId) -> ChecksumAddress:
        return self.contract.functions.ownerChangeRequests(node_id).call()

    def committee_contract(self) -> ChecksumAddress:
        return self.contract.functions.committeeContract().call()

    def _to_node(self, untyped_node: List[Any]) -> FairNode:
        return FairNode(
            id=untyped_node[0],
            ip=bytes(untyped_node[1]),
            ip_str=socket.inet_ntoa(untyped_node[1]),
            domain_name=untyped_node[2],
            address=ChecksumAddress(untyped_node[3]),
            port=Port(untyped_node[4]),
            name=f'node-{untyped_node[0]}',
        )

    def decode_public_key(self, raw_public_key: list[bytes]) -> HexStr:
        key_bytes = raw_public_key[0] + raw_public_key[1]
        return self.skale.web3.to_hex(key_bytes)

    @transaction_method
    def register_active(self, ip: str, port: Port):
        ip_bytes = socket.inet_aton(ip)
        pk_parts_bytes = helper.split_public_key(self.skale.wallet.public_key)
        return self.contract.functions.registerNode(ip_bytes, pk_parts_bytes, port)

    @transaction_method
    def register_passive(self, ip: str, port: Port):
        ip_bytes = socket.inet_aton(ip)
        return self.contract.functions.registerPassiveNode(ip_bytes, port)

    @transaction_method
    def request_change_owner(self, node_id: NodeId, new_owner: ChecksumAddress):
        return self.contract.functions.requestChangeOwner(node_id, new_owner)

    @transaction_method
    def confirm_owner_change(self, node_id: NodeId):
        return self.contract.functions.confirmOwnerChange(node_id)

    @transaction_method
    def set_domain_name(self, node_id: NodeId, domain_name: str):
        return self.contract.functions.setDomainName(node_id, domain_name)

    @transaction_method
    def set_ip_address(self, node_id: NodeId, ip: str, port: Port):
        ip_bytes = socket.inet_aton(ip)
        return self.contract.functions.setIpAddress(node_id, ip_bytes, port)

    @transaction_method
    def set_committee(self, committee_address: ChecksumAddress):
        return self.contract.functions.setCommittee(committee_address)

    @transaction_method
    def delete_node(self, node_id: NodeId):
        return self.contract.functions.deleteNode(node_id)

    @transaction_method
    def delete_node_by_foundation(self, node_id: NodeId):
        return self.contract.functions.deleteNodeByFoundation(node_id)

    def get_public_key(self, node_id: NodeId) -> HexStr:
        raw_public_key = self.contract.functions.getPublicKey(node_id).call()
        return self.decode_public_key(raw_public_key)
