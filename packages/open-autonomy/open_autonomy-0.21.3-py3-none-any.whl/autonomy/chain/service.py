# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023-2025 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Helper functions to manage on-chain services"""

import binascii
import time
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, cast

from aea.configurations.data_types import PublicId
from aea.crypto.base import Crypto, LedgerApi
from hexbytes import HexBytes

from autonomy.chain.base import ServiceState, registry_contracts
from autonomy.chain.config import ChainType, ContractConfigs
from autonomy.chain.constants import (
    ERC20_CONTRACT,
    GNOSIS_SAFE_PROXY_FACTORY_CONTRACT,
    GNOSIS_SAFE_SAME_ADDRESS_MULTISIG_CONTRACT,
    MULTISEND_CONTRACT,
    RECOVERY_MODULE_CONTRACT,
    SAFE_MULTISIG_WITH_RECOVERY_MODULE_CONTRACT,
    SERVICE_MANAGER_CONTRACT,
    SERVICE_REGISTRY_CONTRACT,
    SERVICE_REGISTRY_TOKEN_UTILITY_CONTRACT,
)
from autonomy.chain.exceptions import (
    ChainInteractionError,
    InstanceRegistrationFailed,
    RecoverServiceMultisigFailed,
    ServiceDeployFailed,
    ServiceRegistrationFailed,
    TerminateServiceFailed,
    UnbondServiceFailed,
)
from autonomy.chain.mint import transact
from autonomy.chain.tx import TxSettler


NULL_ADDRESS = "0x0000000000000000000000000000000000000000"
DEFAULT_FALLBACK_HANDLER = "0xf48f2b2d2a534e402487b3ee7c18c33aec0fe5e4"
DEFAULT_DEPLOY_PAYLOAD = "0x0000000000000000000000000000000000000000{fallback_handler}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
DEFAULT_DEPLOY_PAYLOAD_WITH_RECOVERY = "0x000000000000000000000000{fallback_handler}"

ServiceInfo = Tuple[int, str, bytes, int, int, int, int, List[int]]


class MultiSendOperation(Enum):
    """Operation types."""

    CALL = 0
    DELEGATE_CALL = 1


def get_deployment_payload(fallback_handler: Optional[str] = None) -> str:
    """Calculates deployment payload."""
    return (
        DEFAULT_DEPLOY_PAYLOAD.format(
            fallback_handler=(fallback_handler or DEFAULT_FALLBACK_HANDLER)[2:]
        )
        + int(time.time()).to_bytes(32, "big").hex()
    )


def get_deployment_with_recovery_payload(fallback_handler: Optional[str] = None) -> str:
    """Calculates deployment payload."""
    return (
        DEFAULT_DEPLOY_PAYLOAD_WITH_RECOVERY.format(
            fallback_handler=(fallback_handler or DEFAULT_FALLBACK_HANDLER)[2:]
        )
        + int(time.time()).to_bytes(32, "big").hex()
    )


def get_agent_instances(
    ledger_api: LedgerApi, chain_type: ChainType, token_id: int
) -> Dict:
    """
    Get the list of agent instances.

    :param ledger_api: `aea.crypto.LedgerApi` object for interacting with the chain
    :param chain_type: Chain type
    :param token_id: Token ID pointing to the on-chain service
    :returns: number of agent instances and the list of registered addressed
    """

    return registry_contracts.service_registry.get_agent_instances(
        ledger_api=ledger_api,
        contract_address=ContractConfigs.get(SERVICE_REGISTRY_CONTRACT.name).contracts[
            chain_type
        ],
        service_id=token_id,
    )


def get_service_info(
    ledger_api: LedgerApi, chain_type: ChainType, token_id: int
) -> ServiceInfo:
    """
    Returns service info.

    :param ledger_api: `aea.crypto.LedgerApi` object for interacting with the chain
    :param chain_type: Chain type
    :param token_id: Token ID pointing to the on-chain service
    :returns: security deposit, multisig address, IPFS hash for config,
            threshold, max number of agent instances, number of agent instances,
            service state, list of cannonical agents
    """

    return registry_contracts.service_registry.get_service_information(
        ledger_api=ledger_api,
        contract_address=ContractConfigs.get(SERVICE_REGISTRY_CONTRACT.name).contracts[
            chain_type
        ],
        token_id=token_id,
    )


def get_token_deposit_amount(
    ledger_api: LedgerApi,
    chain_type: ChainType,
    service_id: int,
    agent_id: Optional[int] = None,
) -> int:
    """Returns service info."""
    if agent_id is None:
        *_, (agent_id, *_) = get_service_info(
            ledger_api=ledger_api, chain_type=chain_type, token_id=service_id
        )
    return registry_contracts.service_registry_token_utility.get_agent_bond(
        ledger_api=ledger_api,
        contract_address=ContractConfigs.get(
            SERVICE_REGISTRY_TOKEN_UTILITY_CONTRACT.name
        ).contracts[chain_type],
        service_id=service_id,
        agent_id=agent_id,
    ).get("bond")


def get_activate_registration_amount(
    ledger_api: LedgerApi,
    chain_type: ChainType,
    service_id: int,
    agents: List[int],
) -> int:
    """Get activate registration amount."""
    agent_to_deposit = {}
    amount = 0
    for agent in agents:
        if agent not in agent_to_deposit:
            agent_to_deposit[agent] = get_token_deposit_amount(
                ledger_api=ledger_api,
                chain_type=chain_type,
                service_id=service_id,
                agent_id=agent,
            )
        amount += agent_to_deposit[agent]
    return amount


def is_service_token_secured(
    ledger_api: LedgerApi,
    chain_type: ChainType,
    service_id: int,
) -> bool:
    """Check if the service is token secured."""
    response = (
        registry_contracts.service_registry_token_utility.is_token_secured_service(
            ledger_api=ledger_api,
            contract_address=ContractConfigs.get(
                SERVICE_REGISTRY_TOKEN_UTILITY_CONTRACT.name
            ).contracts[chain_type],
            service_id=service_id,
        )
    )
    return response["is_token_secured_service"]


def approve_erc20_usage(  # pylint: disable=too-many-locals
    ledger_api: LedgerApi,
    crypto: Crypto,
    chain_type: ChainType,
    spender: str,
    amount: int,
    sender: str,
    dry_run: bool = False,
    timeout: Optional[float] = None,
    retries: Optional[int] = None,
    sleep: Optional[float] = None,
) -> None:
    """Approve ERC20 token usage."""
    contract_address = ContractConfigs.get(name=ERC20_CONTRACT.name).contracts[
        chain_type
    ]

    kwargs = dict(
        spender=spender,
        amount=amount,
        sender=sender,
    )
    tx_settler = TxSettler(
        chain_type=chain_type,
        ledger_api=ledger_api,
        crypto=crypto,
        tx_builder=lambda: registry_contracts.erc20.get_approve_tx(
            ledger_api=ledger_api,
            contract_address=contract_address,
            raise_on_try=True,
            **kwargs,
        ),
        timeout=timeout,
        retries=retries,
        sleep=sleep,
    )
    tx_settler.transact(dry_run=dry_run)
    if dry_run:  # pragma: nocover
        print("=== Dry run output ===")
        print("Method: " + str(registry_contracts.erc20.get_approve_tx).split(" ")[2])
        print(f"Contract: {contract_address}")
        print("Kwargs: ")
        for key, val in kwargs.items():
            print(f"    {key}: {val}")
        print("Transaction: ")
        for key, val in (tx_settler.tx_dict or {}).items():
            print(f"    {key}: {val}")
        return

    tx_settler.settle().verify_events(
        contract=registry_contracts.get_contract(ERC20_CONTRACT).get_instance(
            ledger_api=ledger_api,
            contract_address=contract_address,
        ),
        event_name="Approval",
        expected_event_arg_name="spender",
        expected_event_arg_value=spender,
    )


class ServiceManager:
    """Service manager."""

    def __init__(
        self,
        ledger_api: LedgerApi,
        crypto: Crypto,
        chain_type: ChainType,
        dry_run: bool = False,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        sleep: Optional[float] = None,
    ) -> None:
        """Initialize object."""
        self.ledger_api = ledger_api
        self.crypto = crypto
        self.chain_type = chain_type
        self.timeout = timeout
        self.retries = retries
        self.sleep = sleep
        self.dry_run = dry_run

    def _transact(
        self,
        method: Callable,
        kwargs: Dict,
        build_tx_ctr_public_id: PublicId,
        event: str,
        service_id: int,
        exception: Exception,
        event_ctr_public_id: PublicId = SERVICE_REGISTRY_CONTRACT,
    ) -> None:
        """Auxiliary method to execute and verify transactions."""
        contract_address = ContractConfigs.get(build_tx_ctr_public_id.name).contracts[
            self.chain_type
        ]
        tx_settler = TxSettler(
            ledger_api=self.ledger_api,
            crypto=self.crypto,
            chain_type=self.chain_type,
            tx_builder=lambda: method(
                ledger_api=self.ledger_api,
                contract_address=contract_address,
                raise_on_try=True,
                **kwargs,
            ),
            timeout=self.timeout,
            retries=self.retries,
            sleep=self.sleep,
        ).transact(dry_run=self.dry_run)

        if self.dry_run:
            print("=== Dry run output ===")
            print("Method: " + str(method).split(" ")[2])
            print(f"Contract: {contract_address}")
            print("Kwargs: ")
            for key, val in kwargs.items():
                print(f"    {key}: {val}")
            print("Transaction: ")
            for key, val in (tx_settler.tx_dict or {}).items():
                print(f"    {key}: {val}")
            return

        try:
            tx_settler.settle().verify_events(
                contract=registry_contracts.get_contract(
                    event_ctr_public_id
                ).get_instance(
                    ledger_api=self.ledger_api,
                    contract_address=ContractConfigs.get(
                        event_ctr_public_id.name
                    ).contracts[self.chain_type],
                ),
                event_name=event,
                expected_event_arg_name="serviceId",
                expected_event_arg_value=service_id,
            )
        except ChainInteractionError as e:
            raise exception from e

    def get_service_info(self, token_id: int) -> ServiceInfo:
        """
        Returns service info.

        :param token_id: Token ID pointing to the on-chain service
        :returns: security deposit, multisig address, IPFS hash for config,
                threshold, max number of agent instances, number of agent instances,
                service state, list of cannonical agents
        """

        return get_service_info(
            ledger_api=self.ledger_api,
            chain_type=self.chain_type,
            token_id=token_id,
        )

    def activate(self, service_id: int) -> None:
        """
        Activate service.

        Once you have minted the service on-chain, you'll have to activate the service
        before you can proceed further.

        :param service_id: Service ID retrieved after minting a service
        """

        (
            cost_of_bond,
            *_,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise ServiceRegistrationFailed("Service does not exist")

        if service_state != ServiceState.PRE_REGISTRATION.value:
            raise ServiceRegistrationFailed("Service must be inactive")

        self._transact(
            method=registry_contracts.service_manager.get_activate_registration_transaction,
            build_tx_ctr_public_id=SERVICE_MANAGER_CONTRACT,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
                security_deposit=cost_of_bond,
            ),
            event="ActivateRegistration",
            service_id=service_id,
            exception=ServiceRegistrationFailed("Could not verify activation event"),
        )

    def register_instance(
        self,
        service_id: int,
        instances: List[str],
        agent_ids: List[int],
    ) -> None:
        """
        Register instance.

        Once you have a service with an active registration, you can register agent
        which will be a part of the service deployment. Using this method you can
        register maximum N amounts per agents, N being the number of slots for an agent
        with agent id being `agent_id`.

        Make sure the instance address you provide is not already a part of any service
        and not as same as the service owner.

        :param service_id: Service ID retrieved after minting a service
        :param instances: Address of the agent instance
        :param agent_ids: Agent ID of the agent that you want this instance to be a part
                        of when deployed
        """

        if len(agent_ids) != len(instances):
            raise InstanceRegistrationFailed(
                "Number of agent instances and agent IDs needs to be same"
            )

        (
            cost_of_bond,
            *_,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise InstanceRegistrationFailed("Service does not exist")

        if service_state != ServiceState.ACTIVE_REGISTRATION.value:
            raise InstanceRegistrationFailed("Service needs to be in active state")

        security_deposit = cost_of_bond * len(agent_ids)
        self._transact(
            method=registry_contracts.service_manager.get_register_instance_transaction,
            build_tx_ctr_public_id=SERVICE_MANAGER_CONTRACT,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
                instances=instances,
                agent_ids=agent_ids,
                security_deposit=security_deposit,
            ),
            event="RegisterInstance",
            service_id=service_id,
            exception=InstanceRegistrationFailed("Could not verify registration event"),
        )

    def deploy(
        self,
        service_id: int,
        fallback_handler: Optional[str] = None,
        reuse_multisig: bool = False,
        use_recovery_module: bool = False,
    ) -> None:
        """
        Deploy service.

        Using this method you can deploy a service on-chain once you have activated
        the service and registered the required agent instances.

        :param service_id: Service ID retrieved after minting a service
        :param fallback_handler: Fallback handler address for gnosis safe multisig
        :param reuse_multisig: Use multisig from the previous deployment
        :param use_recovery_module: Use multisig with recovery module
        """

        (
            *_,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise ServiceDeployFailed("Service does not exist")

        if service_state != ServiceState.FINISHED_REGISTRATION.value:
            raise ServiceDeployFailed(
                "Service needs to be in finished registration state"
            )

        if reuse_multisig:
            if not use_recovery_module:
                _deployment_payload, error = get_reuse_multisig_payload(
                    ledger_api=self.ledger_api,
                    crypto=self.crypto,
                    chain_type=self.chain_type,
                    service_id=service_id,
                )
                if _deployment_payload is None:
                    raise ServiceDeployFailed(error)

                deployment_payload = _deployment_payload

                gnosis_safe_multisig = ContractConfigs.get(
                    GNOSIS_SAFE_SAME_ADDRESS_MULTISIG_CONTRACT.name
                ).contracts[self.chain_type]
            else:
                _deployment_payload, error = get_reuse_multisig_with_recovery_payload(
                    ledger_api=self.ledger_api,
                    crypto=self.crypto,
                    chain_type=self.chain_type,
                    service_id=service_id,
                )
                if _deployment_payload is None:
                    raise ServiceDeployFailed(error)

                deployment_payload = _deployment_payload

                gnosis_safe_multisig = ContractConfigs.get(
                    RECOVERY_MODULE_CONTRACT.name
                ).contracts[self.chain_type]
        else:  # Deploy a new multisig
            if not use_recovery_module:
                deployment_payload = get_deployment_payload(
                    fallback_handler=fallback_handler
                )

                gnosis_safe_multisig = ContractConfigs.get(
                    GNOSIS_SAFE_PROXY_FACTORY_CONTRACT.name
                ).contracts[self.chain_type]
            else:
                deployment_payload = get_deployment_with_recovery_payload(
                    fallback_handler=fallback_handler
                )
                gnosis_safe_multisig = ContractConfigs.get(
                    SAFE_MULTISIG_WITH_RECOVERY_MODULE_CONTRACT.name
                ).contracts[self.chain_type]

        self._transact(
            method=registry_contracts.service_manager.get_service_deploy_transaction,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
                gnosis_safe_multisig=gnosis_safe_multisig,
                deployment_payload=deployment_payload,
            ),
            build_tx_ctr_public_id=SERVICE_MANAGER_CONTRACT,
            event="DeployService",
            service_id=service_id,
            exception=ServiceDeployFailed("Could not verify the deploy event."),
        )

    def terminate(self, service_id: int) -> None:
        """
        Terminate service.

        Using this method you can terminate a service on-chain once you have activated
        the service and registered the required agent instances.

        :param service_id: Service ID retrieved after minting a service
        """

        (
            *_,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise TerminateServiceFailed("Service does not exist")

        if service_state == ServiceState.PRE_REGISTRATION.value:
            raise TerminateServiceFailed("Service not active")

        if service_state == ServiceState.TERMINATED_BONDED.value:
            raise TerminateServiceFailed("Service already terminated")

        self._transact(
            method=registry_contracts.service_manager.get_terminate_service_transaction,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
            ),
            build_tx_ctr_public_id=SERVICE_MANAGER_CONTRACT,
            event="TerminateService",
            service_id=service_id,
            exception=TerminateServiceFailed("Could not verify the terminate event."),
        )

    def unbond(self, service_id: int) -> None:
        """
        Unbond service.

        Using this method you can unbond a service on-chain once you have terminated
        the service.

        :param service_id: Service ID retrieved after minting a service
        """

        (
            *_,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise UnbondServiceFailed("Service does not exist")

        if service_state != ServiceState.TERMINATED_BONDED.value:
            raise UnbondServiceFailed("Service needs to be in terminated-bonded state")

        self._transact(
            method=registry_contracts.service_manager.get_unbond_service_transaction,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
            ),
            build_tx_ctr_public_id=SERVICE_MANAGER_CONTRACT,
            event="OperatorUnbond",
            service_id=service_id,
            exception=UnbondServiceFailed("Could not verify the unbond event."),
        )

    def recover_multisig(self, service_id: int) -> None:
        """
        Recover the service multisig.

        This method allows the service owner to reclaim the multisig wallet from the
        previous deployment if it was not properly transferred by the agents after
        service termination.

        Service multisig recovery is only possible if:
            - The original deployment was performed with the `--use-recovery-module` flag.
            - The service is currently in the `PRE_REGISTRATION` state (i.e., all operators have unbonded).


        :param service_id: Service ID retrieved after minting a service
        """

        (
            _,
            multisig_address,
            _,
            _,
            _,
            _,
            service_state,
            _,
        ) = self.get_service_info(token_id=service_id)

        if service_state == ServiceState.NON_EXISTENT.value:
            raise RecoverServiceMultisigFailed("Service does not exist")

        if service_state != ServiceState.PRE_REGISTRATION.value:
            raise RecoverServiceMultisigFailed("Service not in PRE_REGISTRATION state")

        if multisig_address == NULL_ADDRESS:
            raise RecoverServiceMultisigFailed(
                "Cannot recover multisig: No previous deployment exist."
            )

        multisig_owners = registry_contracts.gnosis_safe.get_owners(
            ledger_api=self.ledger_api,
            contract_address=multisig_address,
        ).get("owners")

        if multisig_owners == [self.crypto.address]:
            raise RecoverServiceMultisigFailed(
                f"The address {self.crypto.address} is already the only owner of the multisig."
            )

        recovery_module_address = ContractConfigs.get(
            RECOVERY_MODULE_CONTRACT.name
        ).contracts[self.chain_type]
        is_recovery_module_enabled = registry_contracts.gnosis_safe.is_module_enabled(
            ledger_api=self.ledger_api,
            contract_address=multisig_address,
            module_address=recovery_module_address,
        ).get("enabled")

        if not is_recovery_module_enabled:
            raise RecoverServiceMultisigFailed(
                "Cannot recover multisig: Recovery module is not enabled."
            )

        self._transact(
            method=registry_contracts.recovery_module.get_recover_access_transaction,
            kwargs=dict(
                owner=self.crypto.address,
                service_id=service_id,
            ),
            build_tx_ctr_public_id=RECOVERY_MODULE_CONTRACT,
            event="AccessRecovered",
            service_id=service_id,
            exception=RecoverServiceMultisigFailed(
                "Could not verify the recover access event."
            ),
            event_ctr_public_id=RECOVERY_MODULE_CONTRACT,
        )


def get_reuse_multisig_payload(  # pylint: disable=too-many-locals
    ledger_api: LedgerApi,
    crypto: Crypto,
    chain_type: ChainType,
    service_id: int,
) -> Tuple[Optional[str], Optional[str]]:
    """Reuse multisig."""
    _, multisig_address, _, threshold, *_ = get_service_info(
        ledger_api=ledger_api,
        chain_type=chain_type,
        token_id=service_id,
    )
    if multisig_address == NULL_ADDRESS:
        return None, "Cannot reuse multisig, No previous deployment exist!"

    service_owner = crypto.address
    multisend_address = ContractConfigs.get(MULTISEND_CONTRACT.name).contracts[
        chain_type
    ]
    multisig_instance = registry_contracts.gnosis_safe.get_instance(
        ledger_api=ledger_api,
        contract_address=multisig_address,
    )

    # Verify if the service was terminated properly or not
    old_owners = multisig_instance.functions.getOwners().call()
    if len(old_owners) != 1 or service_owner not in old_owners:
        return (
            None,
            "Service was not terminated properly, the service owner should be the only owner of the safe",
        )

    # Build multisend tx to add new instances as owners
    txs = []
    new_owners = cast(
        List[str],
        get_agent_instances(
            ledger_api=ledger_api,
            chain_type=chain_type,
            token_id=service_id,
        ).get("agentInstances"),
    )

    for _owner in new_owners:
        txs.append(
            {
                "to": multisig_address,
                "data": HexBytes(
                    bytes.fromhex(
                        multisig_instance.encode_abi(
                            abi_element_identifier="addOwnerWithThreshold",
                            args=[_owner, 1],
                        )[2:]
                    )
                ),
                "operation": MultiSendOperation.CALL,
                "value": 0,
            }
        )

    txs.append(
        {
            "to": multisig_address,
            "data": HexBytes(
                bytes.fromhex(
                    multisig_instance.encode_abi(
                        abi_element_identifier="removeOwner",
                        args=[new_owners[0], service_owner, 1],
                    )[2:]
                )
            ),
            "operation": MultiSendOperation.CALL,
            "value": 0,
        }
    )

    txs.append(
        {
            "to": multisig_address,
            "data": HexBytes(
                bytes.fromhex(
                    multisig_instance.encode_abi(
                        abi_element_identifier="changeThreshold",
                        args=[threshold],
                    )[2:]
                )
            ),
            "operation": MultiSendOperation.CALL,
            "value": 0,
        }
    )

    multisend_tx = registry_contracts.multisend.get_multisend_tx(
        ledger_api=ledger_api,
        contract_address=multisend_address,
        txs=txs,
    )
    safe_tx_hash = registry_contracts.gnosis_safe.get_raw_safe_transaction_hash(
        ledger_api=ledger_api,
        contract_address=multisig_address,
        to_address=multisend_address,
        value=multisend_tx["value"],
        data=multisend_tx["data"],
        operation=1,
    ).get("tx_hash")
    approve_hash_tx = registry_contracts.gnosis_safe.get_approve_hash_tx(
        ledger_api=ledger_api,
        contract_address=multisig_address,
        tx_hash=safe_tx_hash,
        sender=crypto.address,
    )
    transact(
        ledger_api=ledger_api,
        crypto=crypto,
        tx=approve_hash_tx,
    )

    safe_tx_bytes = binascii.unhexlify(safe_tx_hash[2:])
    owner_to_signature = {
        crypto.address: crypto.sign_message(
            message=safe_tx_bytes,
            is_deprecated_mode=True,
        )[2:]
    }
    signature_bytes = registry_contracts.gnosis_safe.get_packed_signatures(
        owners=tuple(old_owners), signatures_by_owner=owner_to_signature
    )
    safe_exec_data = multisig_instance.encode_abi(
        abi_element_identifier="execTransaction",
        args=[
            multisend_address,  # to address
            multisend_tx["value"],  # value
            multisend_tx["data"],  # data
            1,  # operation
            0,  # safe tx gas
            0,  # bas gas
            0,  # safe gas price
            NULL_ADDRESS,  # gas token
            NULL_ADDRESS,  # refund receiver
            signature_bytes,  # signatures
        ],
    )
    payload = multisig_address + safe_exec_data[2:]
    return payload, None


def get_reuse_multisig_with_recovery_payload(  # pylint: disable=too-many-locals
    ledger_api: LedgerApi,
    crypto: Crypto,
    chain_type: ChainType,
    service_id: int,
) -> Tuple[Optional[str], Optional[str]]:
    """Reuse multisig."""
    _, multisig_address, _, _, *_ = get_service_info(
        ledger_api=ledger_api,
        chain_type=chain_type,
        token_id=service_id,
    )
    if multisig_address == NULL_ADDRESS:
        return None, "Cannot reuse multisig, No previous deployment exist!"

    service_owner = crypto.address

    multisig_owners = registry_contracts.gnosis_safe.get_owners(
        ledger_api=ledger_api,
        contract_address=multisig_address,
    ).get("owners")
    if len(multisig_owners) != 1 or service_owner not in multisig_owners:
        return (
            None,
            "Service was not terminated properly, the service owner should be the only owner of the safe",
        )

    payload = "0x" + int(service_id).to_bytes(32, "big").hex()
    return payload, None
