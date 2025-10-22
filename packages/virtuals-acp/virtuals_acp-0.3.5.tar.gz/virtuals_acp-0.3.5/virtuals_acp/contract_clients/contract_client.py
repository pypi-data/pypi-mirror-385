import math
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List

from eth_account import Account
from web3 import Web3

from virtuals_acp.alchemy import AlchemyAccountKit
from virtuals_acp.configs.configs import ACPContractConfig, BASE_MAINNET_CONFIG
from virtuals_acp.contract_clients.base_contract_client import BaseAcpContractClient
from virtuals_acp.exceptions import ACPError
from virtuals_acp.models import ACPJobPhase, MemoType, FeeType


class ACPContractClient(BaseAcpContractClient):
    def __init__(
        self,
        wallet_private_key: str,
        agent_wallet_address: str,
        entity_id: int,
        config: ACPContractConfig = BASE_MAINNET_CONFIG,
    ):
        super().__init__(agent_wallet_address, config)
        self.account = Account.from_key(wallet_private_key)
        self.entity_id = entity_id
        self.alchemy_kit = AlchemyAccountKit(
            config, agent_wallet_address, entity_id, self.account, config.chain_id
        )

    def _get_random_nonce(self, bits: int = 152) -> int:
        """Generate a random bigint nonce."""
        bytes_len = bits // 8
        random_bytes = secrets.token_bytes(bytes_len)
        return int.from_bytes(random_bytes, byteorder="big")

    def _send_user_operation(self, trx_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.alchemy_kit.handle_user_operation(trx_data)

    def get_job_id(
        self, response: Dict[str, Any], client_address: str, provider_address: str
    ) -> int:
        logs: List[Dict[str, Any]] = response.get("receipts", [])[0].get("logs", [])

        decoded_create_job_logs = [
            self.contract.events.JobCreated().process_log(
                {
                    "topics": log["topics"],
                    "data": log["data"],
                    "address": log["address"],
                    "logIndex": 0,
                    "transactionIndex": 0,
                    "transactionHash": "0x0000",
                    "blockHash": "0x0000",
                    "blockNumber": 0,
                }
            )
            for log in logs
            if log["topics"][0] == self.job_created_event_signature_hex
        ]

        if len(decoded_create_job_logs) == 0:
            raise Exception("No logs found for JobCreated event")

        created_job_log = next(
            (
                log
                for log in decoded_create_job_logs
                if log["args"]["provider"] == provider_address
                and log["args"]["client"] == client_address
            ),
            None,
        )

        if not created_job_log:
            raise Exception(
                "No logs found for JobCreated event with provider and client addresses"
            )

        return int(created_job_log["args"]["jobId"])

    def create_job(
        self,
        provider_address: str,
        evaluator_address: str,
        expire_at: datetime,
        payment_token_address: str,
        budget_base_unit: int,
        metadata: str = "",
    ) -> Dict[str, Any]:
        try:
            provider_address = Web3.to_checksum_address(provider_address)
            evaluator_address = Web3.to_checksum_address(evaluator_address)
            expire_timestamp = math.floor(expire_at.timestamp())

            data = self._build_user_operation(
                "createJob", [provider_address, evaluator_address, expire_timestamp]
            )
            tx_response = self._send_user_operation(data)
            job_id = self.get_job_id(
                tx_response, self.agent_wallet_address, provider_address
            )

            self.set_budget_with_payment_token(
                job_id, budget_base_unit, payment_token_address
            )

            return tx_response
        except Exception as e:
            raise ACPError("Failed to create job", e)

    def create_payable_memo(
        self,
        job_id: int,
        content: str,
        amount_base_unit: int,
        recipient: str,
        fee_amount_base_unit: int,
        fee_type: FeeType,
        next_phase: ACPJobPhase,
        memo_type: MemoType,
        expired_at: datetime,
        token: Optional[str] = None,
        secured: bool = True,
    ) -> Dict[str, Any]:
        try:
            token_address = token or self.config.base_fare.contract_address
            data = self._build_user_operation(
                "createPayableMemo",
                [
                    job_id,
                    content,
                    token_address,
                    amount_base_unit,
                    Web3.to_checksum_address(recipient),
                    fee_amount_base_unit,
                    fee_type.value,
                    memo_type.value,
                    next_phase.value,
                    math.floor(expired_at.timestamp()),
                ],
            )

            return self._send_user_operation(data)
        except Exception as e:
            raise ACPError("Failed to create payable memo", e)

    def create_job_with_account(
        self,
        account_id: int,
        provider_address: str,
        evaluator_address: str,
        budget_base_unit: int,
        payment_token_address: str,
        expired_at: datetime,
    ) -> Dict[str, Any]:
        raise ACPError("Not Supported")

    def update_account_metadata(self, account_id: int, metadata: str) -> Dict[str, Any]:
        raise ACPError("Not Supported")
