"""
Production-ready base agent for ChaosChain protocol interactions.

This module provides the foundational ChaosAgent class that handles
ERC-8004 registry interactions, identity management, and core protocol operations.
"""

import json
import os
from typing import Dict, Optional, Any, Tuple
from web3 import Web3
from web3.contract import Contract
from rich import print as rprint

from .types import NetworkConfig, AgentID, TransactionHash, ContractAddresses
from .exceptions import (
    AgentRegistrationError, 
    NetworkError, 
    ContractError,
    ConfigurationError
)
from .wallet_manager import WalletManager


class ChaosAgent:
    """
    Base class for ChaosChain agents interacting with ERC-8004 registries.
    
    Provides core functionality for agent identity management, contract interactions,
    and protocol operations across multiple blockchain networks.
    
    Attributes:
        agent_domain: Domain where the agent's identity is hosted
        wallet_manager: Wallet manager for transaction handling
        network: Target blockchain network
        agent_id: On-chain agent identifier (set after registration)
    """
    
    def __init__(self, agent_name: str, agent_domain: str, wallet_manager: WalletManager, 
                 network: NetworkConfig = NetworkConfig.BASE_SEPOLIA):
        """
        Initialize the ChaosChain base agent.
        
        Args:
            agent_name: Name of the agent for wallet lookup
            agent_domain: Domain where agent's identity is hosted
            wallet_manager: Wallet manager instance
            network: Target blockchain network
        """
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.wallet_manager = wallet_manager
        self.network = network
        self.agent_id: Optional[AgentID] = None
        
        # Get wallet address from manager using provided agent name
        self.address = wallet_manager.get_wallet_address(self.agent_name)
        
        # Initialize Web3 connection
        self.w3 = wallet_manager.w3
        self.chain_id = wallet_manager.chain_id
        
        # Load contract addresses and initialize contracts
        self._load_contract_addresses()
        self._load_contracts()
        
        rprint(f"[green]🌐 Connected to {self.network} (Chain ID: {self.chain_id})[/green]")
    
    def _load_contract_addresses(self):
        """
        Load deployed ERC-8004 v1.0 contract addresses.
        
        These are the official ERC-8004 v1.0 contracts deployed on testnets.
        Source: /Users/sumeet/Desktop/erc-8004-contracts/contracts
        """
        # Network-specific configuration with actual deployed addresses
        contract_addresses = {
            NetworkConfig.BASE_SEPOLIA: {
                'identity_registry': '0x8004AA63c570c570eBF15376c0dB199918BFe9Fb',
                'reputation_registry': '0x8004bd8daB57f14Ed299135749a5CB5c42d341BF',
                'validation_registry': '0x8004C269D0A5647E51E121FeB226200ECE932d55',
                'usdc_token': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
                'treasury': '0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70'
            },
            NetworkConfig.ETHEREUM_SEPOLIA: {
                'identity_registry': '0x8004a6090Cd10A7288092483047B097295Fb8847',
                'reputation_registry': '0x8004B8FD1A363aa02fDC07635C0c5F94f6Af5B7E',
                'validation_registry': '0x8004CB39f29c09145F24Ad9dDe2A108C1A2cdfC5',
                'usdc_token': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
                'treasury': '0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70'
            },
            NetworkConfig.OPTIMISM_SEPOLIA: {
                'identity_registry': '0x8004aa7C931bCE1233973a0C6A667f73F66282e7',  # Linea Sepolia
                'reputation_registry': '0x8004bd8483b99310df121c46ED8858616b2Bba02',  # Linea Sepolia
                'validation_registry': '0x8004c44d1EFdd699B2A26e781eF7F77c56A9a4EB',  # Linea Sepolia
                'usdc_token': '0x5fd84259d66Cd46123540766Be93DFE6D43130D7',
                'treasury': '0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70'
            },
            # NetworkConfig.MODE_TESTNET: {
            #     'identity_registry': '0x0000000000000000000000000000000000000000',  # Not yet deployed
            #     'reputation_registry': '0x0000000000000000000000000000000000000000',
            #     'validation_registry': '0x0000000000000000000000000000000000000000',
            #     'usdc_token': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
            #     'treasury': '0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70'
            # },
            # NetworkConfig.ZEROG_TESTNET: {
            #     'identity_registry': '0x0000000000000000000000000000000000000000',  # Not yet deployed
            #     'reputation_registry': '0x0000000000000000000000000000000000000000',
            #     'validation_registry': '0x0000000000000000000000000000000000000000',
            #     'usdc_token': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
            #     'treasury': '0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70'
            # }
        }
        
        network_contracts = contract_addresses.get(self.network)
        if not network_contracts:
            raise ConfigurationError(f"No deployed contracts configured for network: {self.network}")
        
        self.contract_addresses = ContractAddresses(
            identity_registry=network_contracts['identity_registry'],
            reputation_registry=network_contracts['reputation_registry'], 
            validation_registry=network_contracts['validation_registry'],
            network=self.network
        )
    
    def _load_contracts(self):
        """Load contract instances with embedded ABIs."""
        try:
            # Embedded minimal ABIs - no external files needed
            identity_abi = self._get_identity_registry_abi()
            reputation_abi = self._get_reputation_registry_abi()
            validation_abi = self._get_validation_registry_abi()
            
            rprint(f"[green]📋 Contracts ready for {self.network.value}[/green]")
            
            # Create contract instances
            self.identity_registry = self.w3.eth.contract(
                address=self.contract_addresses.identity_registry,
                abi=identity_abi
            )
            
            self.reputation_registry = self.w3.eth.contract(
                address=self.contract_addresses.reputation_registry,
                abi=reputation_abi
            )
            
            self.validation_registry = self.w3.eth.contract(
                address=self.contract_addresses.validation_registry,
                abi=validation_abi
            )
            
        except Exception as e:
            raise ContractError(f"Failed to load contracts: {str(e)}")
    
    def _get_identity_registry_abi(self) -> list:
        """
        Get embedded Identity Registry ABI for ERC-8004 v1.0.
        
        v1.0 uses ERC-721 with URIStorage extension. Key changes:
        - register() functions replace newAgent()
        - Agents are ERC-721 NFTs with tokenURI
        - ownerOf() to get agent owner
        - tokenURI() to get registration file
        """
        return [
            # ERC-8004 v1.0 Registration Functions
            {
                "inputs": [
                    {"name": "tokenURI_", "type": "string"},
                    {
                        "name": "metadata",
                        "type": "tuple[]",
                        "components": [
                            {"name": "key", "type": "string"},
                            {"name": "value", "type": "bytes"}
                        ]
                    }
                ],
                "name": "register",
                "outputs": [{"name": "agentId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenURI_", "type": "string"}],
                "name": "register",
                "outputs": [{"name": "agentId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "register",
                "outputs": [{"name": "agentId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            # ERC-721 Standard Functions
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "ownerOf",
                "outputs": [{"name": "owner", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "tokenURI",
                "outputs": [{"name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "tokenId", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "tokenId", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "operator", "type": "address"},
                    {"name": "approved", "type": "bool"}
                ],
                "name": "setApprovalForAll",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "getApproved",
                "outputs": [{"name": "operator", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "operator", "type": "address"}
                ],
                "name": "isApprovedForAll",
                "outputs": [{"name": "approved", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            # Metadata Functions
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "key", "type": "string"},
                    {"name": "value", "type": "bytes"}
                ],
                "name": "setMetadata",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "key", "type": "string"}
                ],
                "name": "getMetadata",
                "outputs": [{"name": "value", "type": "bytes"}],
                "stateMutability": "view",
                "type": "function"
            },
            # Additional Functions
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "newUri", "type": "string"}
                ],
                "name": "setAgentUri",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            # Events
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "tokenURI", "type": "string"},
                    {"indexed": True, "name": "owner", "type": "address"}
                ],
                "name": "Registered",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": True, "name": "indexedKey", "type": "string"},
                    {"indexed": False, "name": "key", "type": "string"},
                    {"indexed": False, "name": "value", "type": "bytes"}
                ],
                "name": "MetadataSet",
                "type": "event"
            },
            # ERC-721 Standard Events
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": True, "name": "tokenId", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "owner", "type": "address"},
                    {"indexed": True, "name": "approved", "type": "address"},
                    {"indexed": True, "name": "tokenId", "type": "uint256"}
                ],
                "name": "Approval",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "owner", "type": "address"},
                    {"indexed": True, "name": "operator", "type": "address"},
                    {"indexed": False, "name": "approved", "type": "bool"}
                ],
                "name": "ApprovalForAll",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "newUri", "type": "string"},
                    {"indexed": True, "name": "updatedBy", "type": "address"}
                ],
                "name": "UriUpdated",
                "type": "event"
            }
        ]
    
    def _get_reputation_registry_abi(self) -> list:
        """
        Get embedded Reputation Registry ABI for ERC-8004 v1.0.
        
        v1.0 uses cryptographic signatures (EIP-191/ERC-1271) for feedback authorization.
        Key changes:
        - giveFeedback() with signature-based authorization
        - On-chain scores (0-100) with tags
        - revokeFeedback() support
        - appendResponse() for audit trails
        """
        return [
            # Core Functions
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "score", "type": "uint8"},
                    {"name": "tag1", "type": "bytes32"},
                    {"name": "tag2", "type": "bytes32"},
                    {"name": "feedbackUri", "type": "string"},
                    {"name": "feedbackHash", "type": "bytes32"},
                    {"name": "feedbackAuth", "type": "bytes"}
                ],
                "name": "giveFeedback",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "feedbackIndex", "type": "uint64"}
                ],
                "name": "revokeFeedback",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "clientAddress", "type": "address"},
                    {"name": "feedbackIndex", "type": "uint64"},
                    {"name": "responseUri", "type": "string"},
                    {"name": "responseHash", "type": "bytes32"}
                ],
                "name": "appendResponse",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            # Read Functions
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "clientAddresses", "type": "address[]"},
                    {"name": "tag1", "type": "bytes32"},
                    {"name": "tag2", "type": "bytes32"}
                ],
                "name": "getSummary",
                "outputs": [
                    {"name": "count", "type": "uint64"},
                    {"name": "averageScore", "type": "uint8"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "clientAddress", "type": "address"},
                    {"name": "index", "type": "uint64"}
                ],
                "name": "readFeedback",
                "outputs": [
                    {"name": "score", "type": "uint8"},
                    {"name": "tag1", "type": "bytes32"},
                    {"name": "tag2", "type": "bytes32"},
                    {"name": "isRevoked", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "clientAddresses", "type": "address[]"},
                    {"name": "tag1", "type": "bytes32"},
                    {"name": "tag2", "type": "bytes32"},
                    {"name": "includeRevoked", "type": "bool"}
                ],
                "name": "readAllFeedback",
                "outputs": [
                    {"name": "clients", "type": "address[]"},
                    {"name": "scores", "type": "uint8[]"},
                    {"name": "tag1s", "type": "bytes32[]"},
                    {"name": "tag2s", "type": "bytes32[]"},
                    {"name": "revokedStatuses", "type": "bool[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}],
                "name": "getClients",
                "outputs": [{"name": "clientList", "type": "address[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "clientAddress", "type": "address"}
                ],
                "name": "getLastIndex",
                "outputs": [{"name": "lastIndex", "type": "uint64"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getIdentityRegistry",
                "outputs": [{"name": "registry", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            # Events
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": True, "name": "clientAddress", "type": "address"},
                    {"indexed": False, "name": "score", "type": "uint8"},
                    {"indexed": True, "name": "tag1", "type": "bytes32"},
                    {"indexed": False, "name": "tag2", "type": "bytes32"},
                    {"indexed": False, "name": "feedbackUri", "type": "string"},
                    {"indexed": False, "name": "feedbackHash", "type": "bytes32"}
                ],
                "name": "NewFeedback",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": True, "name": "clientAddress", "type": "address"},
                    {"indexed": False, "name": "feedbackIndex", "type": "uint64"},
                    {"indexed": True, "name": "responder", "type": "address"},
                    {"indexed": False, "name": "responseUri", "type": "string"},
                    {"indexed": False, "name": "responseHash", "type": "bytes32"}
                ],
                "name": "ResponseAppended",
                "type": "event"
            }
        ]
    
    def _get_validation_registry_abi(self) -> list:
        """
        Get embedded Validation Registry ABI for ERC-8004 v1.0.
        
        v1.0 uses URI-based validation with off-chain evidence storage.
        Key changes:
        - validationRequest() uses validatorAddress instead of validatorAgentId
        - requestUri and requestHash for off-chain evidence
        - validationResponse() uses requestHash with response (0-100)
        - Support for multiple responses per request (progressive validation)
        """
        return [
            # Core Functions
            {
                "inputs": [
                    {"name": "validatorAddress", "type": "address"},
                    {"name": "agentId", "type": "uint256"},
                    {"name": "requestUri", "type": "string"},
                    {"name": "requestHash", "type": "bytes32"}
                ],
                "name": "validationRequest",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "requestHash", "type": "bytes32"},
                    {"name": "response", "type": "uint8"},
                    {"name": "responseUri", "type": "string"},
                    {"name": "responseHash", "type": "bytes32"},
                    {"name": "tag", "type": "bytes32"}
                ],
                "name": "validationResponse",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            # Read Functions
            {
                "inputs": [{"name": "requestHash", "type": "bytes32"}],
                "name": "getValidationStatus",
                "outputs": [
                    {"name": "validatorAddress", "type": "address"},
                    {"name": "agentId", "type": "uint256"},
                    {"name": "response", "type": "uint8"},
                    {"name": "responseHash", "type": "bytes32"},
                    {"name": "tag", "type": "bytes32"},
                    {"name": "lastUpdate", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "validatorAddresses", "type": "address[]"},
                    {"name": "tag", "type": "bytes32"}
                ],
                "name": "getSummary",
                "outputs": [
                    {"name": "count", "type": "uint64"},
                    {"name": "avgResponse", "type": "uint8"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}],
                "name": "getAgentValidations",
                "outputs": [{"name": "requestHashes", "type": "bytes32[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "validatorAddress", "type": "address"}],
                "name": "getValidatorRequests",
                "outputs": [{"name": "requestHashes", "type": "bytes32[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getIdentityRegistry",
                "outputs": [{"name": "registry", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            # Events
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "validatorAddress", "type": "address"},
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "requestUri", "type": "string"},
                    {"indexed": True, "name": "requestHash", "type": "bytes32"}
                ],
                "name": "ValidationRequest",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "validatorAddress", "type": "address"},
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": True, "name": "requestHash", "type": "bytes32"},
                    {"indexed": False, "name": "response", "type": "uint8"},
                    {"indexed": False, "name": "responseUri", "type": "string"},
                    {"indexed": False, "name": "responseHash", "type": "bytes32"},
                    {"indexed": False, "name": "tag", "type": "bytes32"}
                ],
                "name": "ValidationResponse",
                "type": "event"
            }
        ]
    
    
    def _generate_token_uri(self) -> str:
        """
        Generate ERC-8004 v1.0 compliant agent registration JSON.
        
        Returns inline data URI with registration metadata.
        This can be replaced with IPFS or HTTP endpoints in production.
        """
        registration_data = {
            "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
            "name": self.agent_name,
            "description": f"ChaosChain agent deployed at {self.agent_domain}",
            "image": "https://chaoscha.in/agent-avatar.png",  # Default avatar
            "endpoints": [
                {
                    "name": "agentWallet",
                    "endpoint": f"eip155:{self.chain_id}:{self.address}"
                }
            ],
            "registrations": [
                {
                    "agentId": 0,  # Will be filled after registration
                    "agentRegistry": f"eip155:{self.chain_id}:{self.contract_addresses.identity_registry}"
                }
            ],
            "supportedTrust": ["reputation", "crypto-economic"]
        }
        
        # Convert to inline data URI (can be replaced with IPFS in production)
        json_str = json.dumps(registration_data)
        return f"data:application/json;base64,{json_str}"
    
    def register_agent(
        self, 
        token_uri: Optional[str] = None,
        metadata: Optional[Dict[str, bytes]] = None
    ) -> Tuple[AgentID, TransactionHash]:
        """
        Register this agent on the ERC-8004 v1.0 IdentityRegistry.
        
        v1.0 uses ERC-721 based registration with tokenURI and optional metadata.
        
        Args:
            token_uri: Optional custom tokenURI. If not provided, generates default.
            metadata: Optional dict of on-chain metadata {key: value_bytes}.
                     Example: {"agentName": b"MyAgent", "agentWallet": address_bytes}
        
        Returns:
            Tuple of (agent_id, transaction_hash)
        """
        rprint(f"[yellow]🔧 Registering agent: {self.agent_name} ({self.agent_domain})[/yellow]")
        
        # v1.0: Check if already registered by iterating through tokens owned by this address
        # In v1.0, agents are ERC-721 NFTs
        try:
            # Try to get total agents to search through
            total_agents = self.identity_registry.functions.totalAgents().call()
            rprint(f"[blue]🔍 Checking {total_agents} existing agents for ownership...[/blue]")
            
            # Check if this wallet owns any agents
            for potential_id in range(1, min(total_agents + 1, 1000)):  # Limit search to 1000
                try:
                    owner = self.identity_registry.functions.ownerOf(potential_id).call()
                    if owner.lower() == self.address.lower():
                        self.agent_id = potential_id
                        rprint(f"[green]✅ Agent already registered with ID: {self.agent_id}[/green]")
                        return self.agent_id, "already_registered"
                except:
                    continue
                    
        except Exception as e:
            rprint(f"[blue]🔍 Could not check existing registrations: {e}[/blue]")
            pass
        
        try:
            # Generate tokenURI if not provided
            if token_uri is None:
                token_uri = self._generate_token_uri()
                rprint(f"[blue]📝 Generated tokenURI for registration[/blue]")
            
            # v1.0: Choose register function based on metadata
            if metadata:
                # Convert metadata dict to MetadataEntry[] array
                metadata_entries = [(key, value) for key, value in metadata.items()]
                rprint(f"[blue]📋 Registering with {len(metadata_entries)} metadata entries[/blue]")
                contract_call = self.identity_registry.functions['register(string,(string,bytes)[])'](
                    token_uri,
                    metadata_entries
                )
            else:
                # Use simple register(tokenURI) function
                contract_call = self.identity_registry.functions['register(string)'](token_uri)
            
            # Estimate gas
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
            
            rprint(f"[yellow]⛽ Gas estimate: {gas_estimate}, using limit: {gas_limit}[/yellow]")
            
            # Build transaction
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            
            # Sign and send transaction
            account = self.wallet_manager.wallets[self.agent_name]
            signed_txn = self.w3.eth.account.sign_transaction(transaction, account.key)
            
            rprint(f"[yellow]⏳ Waiting for transaction confirmation...[/yellow]")
            # Handle both old and new Web3.py versions
            raw_transaction = getattr(signed_txn, 'raw_transaction', getattr(signed_txn, 'rawTransaction', None))
            if raw_transaction is None:
                raise Exception("Could not get raw transaction from signed transaction")
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                # v1.0: Extract agent ID from Registered event logs
                try:
                    # Find the Registered event in logs
                    registered_event = self.identity_registry.events.Registered()
                    logs = registered_event.process_receipt(receipt)
                    if logs:
                        self.agent_id = logs[0]['args']['agentId']
                        rprint(f"[green]✅ Agent registered successfully with ID: {self.agent_id}[/green]")
                        rprint(f"[blue]📋 View on explorer: Transaction {tx_hash.hex()[:10]}...[/blue]")
                        return self.agent_id, tx_hash.hex()
                except Exception as log_error:
                    rprint(f"[yellow]⚠️  Could not parse event logs: {log_error}[/yellow]")
                    # Fallback: Check ownership to find agent ID
                    total_agents = self.identity_registry.functions.totalAgents().call()
                    for potential_id in range(total_agents, max(0, total_agents - 10), -1):
                        try:
                            owner = self.identity_registry.functions.ownerOf(potential_id).call()
                            if owner.lower() == self.address.lower():
                                self.agent_id = potential_id
                                rprint(f"[green]✅ Agent registered with ID: {self.agent_id}[/green]")
                                return self.agent_id, tx_hash.hex()
                        except:
                            continue
                    
                    raise AgentRegistrationError("Registration succeeded but could not determine agent ID")
            else:
                raise AgentRegistrationError("Transaction failed")
                
        except Exception as e:
            error_msg = str(e)
            rprint(f"[red]❌ Registration failed: {error_msg}[/red]")
            
            # Check for specific error types
            if "insufficient funds" in error_msg.lower():
                rprint(f"[yellow]💰 Insufficient ETH for gas fees in wallet: {self.address}[/yellow]")
                rprint(f"[blue]Please fund this wallet using Base Sepolia faucet:[/blue]")
                rprint(f"[blue]https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet[/blue]")
            
            raise AgentRegistrationError(f"Failed to register {self.agent_domain}: {error_msg}")
    
    def get_agent_id(self) -> Optional[AgentID]:
        """
        Get the agent's on-chain ID (ERC-8004 v1.0).
        
        v1.0: Agents are ERC-721 NFTs. Check if this wallet owns any agent tokens.
        
        Returns:
            Agent ID if registered, None otherwise
        """
        if self.agent_id:
            return self.agent_id
        
        try:
            # v1.0: Check if this wallet owns any agents by iterating through tokens
            total_agents = self.identity_registry.functions.totalAgents().call()
            
            # Check ownership of recent agents first (more efficient)
            for potential_id in range(total_agents, max(0, total_agents - 100), -1):
                try:
                    owner = self.identity_registry.functions.ownerOf(potential_id).call()
                    if owner.lower() == self.address.lower():
                        self.agent_id = potential_id
                        return self.agent_id
                except:
                    continue
            
            # If not found in recent agents, check older ones
            for potential_id in range(1, min(max(0, total_agents - 100), 100)):
                try:
                    owner = self.identity_registry.functions.ownerOf(potential_id).call()
                    if owner.lower() == self.address.lower():
                        self.agent_id = potential_id
                        return self.agent_id
                except:
                    continue
                    
        except Exception as e:
            rprint(f"[yellow]⚠️  Could not check agent ownership: {e}[/yellow]")
        
        return None
    
    def set_agent_metadata(self, key: str, value: bytes) -> TransactionHash:
        """
        Set on-chain metadata for this agent (ERC-8004 v1.0).
        
        Per ERC-8004 spec: "The registry extends ERC-721 by adding getMetadata() 
        and setMetadata() functions for optional extra on-chain agent metadata."
        
        Examples of keys: "agentWallet", "agentName", custom application keys.
        
        Args:
            key: Metadata key (string)
            value: Metadata value as bytes
        
        Returns:
            Transaction hash
            
        Raises:
            AgentRegistrationError: If agent is not registered
            ContractError: If transaction fails
        """
        if not self.agent_id:
            raise AgentRegistrationError("Agent must be registered before setting metadata")
        
        try:
            rprint(f"[yellow]📝 Setting metadata '{key}' for agent #{self.agent_id}[/yellow]")
            
            # v1.0: setMetadata(uint256 agentId, string key, bytes value)
            contract_call = self.identity_registry.functions.setMetadata(
                self.agent_id,
                key,
                value
            )
            
            # Build and send transaction
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            gas_limit = int(gas_estimate * 1.2)
            
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            
            # Sign and send
            account = self.wallet_manager.wallets[self.agent_name]
            signed_txn = self.w3.eth.account.sign_transaction(transaction, account.key)
            
            raw_transaction = getattr(signed_txn, 'raw_transaction', getattr(signed_txn, 'rawTransaction', None))
            if raw_transaction is None:
                raise Exception("Could not get raw transaction from signed transaction")
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Metadata '{key}' set successfully[/green]")
                return tx_hash.hex()
            else:
                raise ContractError("Metadata update transaction failed")
                
        except Exception as e:
            error_msg = str(e)
            rprint(f"[red]❌ Failed to set metadata: {error_msg}[/red]")
            raise ContractError(f"Failed to set metadata '{key}': {error_msg}")
    
    def get_agent_metadata(self, key: str, agent_id: Optional[int] = None) -> bytes:
        """
        Get on-chain metadata for an agent (ERC-8004 v1.0).
        
        Per ERC-8004 spec: "The registry extends ERC-721 by adding getMetadata() 
        and setMetadata() functions for optional extra on-chain agent metadata."
        
        Args:
            key: Metadata key to retrieve
            agent_id: Agent ID to query. If None, uses this agent's ID.
        
        Returns:
            Metadata value as bytes
            
        Raises:
            AgentRegistrationError: If querying own agent and not registered
            ContractError: If metadata retrieval fails
        """
        target_agent_id = agent_id if agent_id is not None else self.agent_id
        
        if target_agent_id is None:
            raise AgentRegistrationError("Agent ID required (either register or provide agent_id parameter)")
        
        try:
            # v1.0: getMetadata(uint256 agentId, string key) returns (bytes value)
            metadata_value = self.identity_registry.functions.getMetadata(
                target_agent_id,
                key
            ).call()
            
            rprint(f"[green]✅ Retrieved metadata '{key}' for agent #{target_agent_id}[/green]")
            return metadata_value
            
        except Exception as e:
            error_msg = str(e)
            rprint(f"[yellow]⚠️  Could not retrieve metadata '{key}': {error_msg}[/yellow]")
            raise ContractError(f"Failed to get metadata '{key}' for agent #{target_agent_id}: {error_msg}")
    
    def request_validation(
        self, 
        validator_address: str, 
        request_uri: str, 
        request_hash: Optional[str] = None
    ) -> TransactionHash:
        """
        Request validation from another agent (ERC-8004 v1.0).
        
        v1.0: Uses validator addresses and URI-based evidence storage.
        
        Args:
            validator_address: Ethereum address of the validator (not agent ID)
            request_uri: URI pointing to validation request data (IPFS, HTTP, etc.)
            request_hash: Optional KECCAK-256 hash of request data (auto-generated if not provided)
            
        Returns:
            Transaction hash
        """
        try:
            if not self.agent_id:
                raise ContractError("Agent must be registered before requesting validation")
            
            # Generate request hash if not provided
            if request_hash is None:
                import hashlib
                # Generate unique hash from validator, agent, URI, and timestamp
                hash_input = f"{validator_address}{self.agent_id}{request_uri}{self.w3.eth.block_number}"
                request_hash_bytes = hashlib.sha256(hash_input.encode()).digest()
                request_hash = '0x' + request_hash_bytes.hex()
            
            # Convert hash to bytes32 if needed
            if isinstance(request_hash, str):
                if request_hash.startswith('0x'):
                    request_hash_bytes = bytes.fromhex(request_hash[2:])
                else:
                    request_hash_bytes = bytes.fromhex(request_hash)
            else:
                request_hash_bytes = request_hash
            
            # Ensure 32 bytes
            if len(request_hash_bytes) != 32:
                raise ValueError("Request hash must be 32 bytes")
            
            rprint(f"[yellow]📋 Requesting validation from {validator_address[:10]}...[/yellow]")
            
            # v1.0: validationRequest(validatorAddress, agentId, requestUri, requestHash)
            contract_call = self.validation_registry.functions.validationRequest(
                validator_address,
                self.agent_id,
                request_uri,
                request_hash_bytes
            )
            
            # Build and send transaction
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            
            account = self.wallet_manager.wallets[self.agent_name]
            signed_txn = self.w3.eth.account.sign_transaction(transaction, account.key)
            raw_transaction = getattr(signed_txn, 'raw_transaction', getattr(signed_txn, 'rawTransaction', None))
            if raw_transaction is None:
                raise Exception("Could not get raw transaction from signed transaction")
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Validation request submitted: {tx_hash.hex()[:10]}...[/green]")
                return tx_hash.hex()
            else:
                raise ContractError("Validation request transaction failed")
                
        except Exception as e:
            raise ContractError(f"Failed to request validation: {str(e)}")
    
    def submit_validation_response(
        self,
        request_hash: str,
        response: int,
        response_uri: str = "",
        response_hash: Optional[str] = None,
        tag: str = ""
    ) -> TransactionHash:
        """
        Submit a validation response (ERC-8004 v1.0).
        
        v1.0: Uses requestHash from the validation request and supports URIs for evidence.
        
        Args:
            request_hash: Hash of the validation request
            response: Validation response (0-100, where 0=failed, 100=passed)
            response_uri: Optional URI pointing to validation evidence
            response_hash: Optional KECCAK-256 hash of response data
            tag: Optional tag for categorization
            
        Returns:
            Transaction hash
        """
        try:
            # Validate response range
            response = min(100, max(0, int(response)))
            
            # Convert request hash to bytes32
            if isinstance(request_hash, str):
                if request_hash.startswith('0x'):
                    request_hash_bytes = bytes.fromhex(request_hash[2:])
                else:
                    request_hash_bytes = bytes.fromhex(request_hash)
            else:
                request_hash_bytes = request_hash
            
            # Ensure 32 bytes
            if len(request_hash_bytes) != 32:
                raise ValueError("Request hash must be 32 bytes")
            
            # Convert response hash to bytes32 if provided
            response_hash_bytes = b'\x00' * 32  # Default empty hash
            if response_hash:
                if isinstance(response_hash, str):
                    if response_hash.startswith('0x'):
                        response_hash_bytes = bytes.fromhex(response_hash[2:])
                    else:
                        response_hash_bytes = bytes.fromhex(response_hash)
                else:
                    response_hash_bytes = response_hash
            
            # Convert tag to bytes32
            tag_bytes = b'\x00' * 32  # Default empty tag
            if tag:
                tag_encoded = tag.encode()[:32]  # Truncate to 32 bytes if needed
                tag_bytes = tag_encoded + b'\x00' * (32 - len(tag_encoded))  # Pad with zeros
            
            rprint(f"[yellow]✍️  Submitting validation response: {response}/100[/yellow]")
            
            # v1.0: validationResponse(requestHash, response, responseUri, responseHash, tag)
            contract_call = self.validation_registry.functions.validationResponse(
                request_hash_bytes,
                response,
                response_uri,
                response_hash_bytes,
                tag_bytes
            )
            
            # Build and send transaction
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            
            account = self.wallet_manager.wallets[self.agent_name]
            signed_txn = self.w3.eth.account.sign_transaction(transaction, account.key)
            raw_transaction = getattr(signed_txn, 'raw_transaction', getattr(signed_txn, 'rawTransaction', None))
            if raw_transaction is None:
                raise Exception("Could not get raw transaction from signed transaction")
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Validation response submitted: {tx_hash.hex()[:10]}...[/green]")
                return tx_hash.hex()
            else:
                raise ContractError("Validation response transaction failed")
            
        except Exception as e:
            raise ContractError(f"Failed to submit validation response: {str(e)}")

    def generate_feedback_authorization(
        self,
        agent_id: AgentID,
        client_address: str,
        index_limit: int,
        expiry: int
    ) -> bytes:
        """
        Generate EIP-191 signed feedback authorization (ERC-8004 v1.0).
        
        This signature allows a client to submit feedback to an agent's reputation.
        The agent owner signs to authorize the client to give feedback up to a certain index.
        
        Args:
            agent_id: Target agent ID receiving feedback
            client_address: Address of the client giving feedback
            index_limit: Maximum feedback index this authorization permits
            expiry: Unix timestamp when authorization expires
            
        Returns:
            Signed feedbackAuth bytes for use in giveFeedback()
        """
        try:
            # Pack the FeedbackAuth struct (7 fields)
            # As per ERC-8004 v1.0 spec: (agentId, clientAddress, indexLimit, expiry, chainId, identityRegistry, signerAddress)
            feedback_auth_data = self.w3.solidity_keccak(
                ['uint256', 'address', 'uint64', 'uint256', 'uint256', 'address', 'address'],
                [
                    agent_id,
                    client_address,
                    index_limit,
                    expiry,
                    self.chain_id,
                    self.contract_addresses.identity_registry,
                    self.address  # signer address (agent owner)
                ]
            )
            
            # EIP-191 personal sign format
            message_hash = self.w3.solidity_keccak(
                ['string', 'bytes32'],
                ['\x19Ethereum Signed Message:\n32', feedback_auth_data]
            )
            
            # Sign with agent's private key
            account = self.wallet_manager.wallets[self.agent_name]
            # Use sign_message for LocalAccount (web3.py)
            from eth_account.messages import encode_defunct
            signed_message = account.sign_message(encode_defunct(hexstr=message_hash.hex()))
            signature_bytes = bytes(signed_message.signature)  # Already 65 bytes (r + s + v)
            
            # Pack struct data + signature (224 bytes + 65 bytes = 289 bytes)
            struct_bytes = (
                agent_id.to_bytes(32, 'big') +
                bytes.fromhex(client_address[2:].zfill(40)) +
                index_limit.to_bytes(8, 'big') +
                bytes(24) +  # Padding for uint64 in uint256 slot
                expiry.to_bytes(32, 'big') +
                self.chain_id.to_bytes(32, 'big') +
                bytes.fromhex(self.contract_addresses.identity_registry[2:].zfill(40)) +
                bytes.fromhex(self.address[2:].zfill(40))
            )
            
            return struct_bytes + signature_bytes
            
        except Exception as e:
            raise ContractError(f"Failed to generate feedback authorization: {str(e)}")
    
    def give_feedback(
        self,
        agent_id: AgentID,
        score: int,
        feedback_auth: bytes,
        tag1: str = "",
        tag2: str = "",
        file_uri: str = "",
        file_hash: Optional[str] = None
    ) -> TransactionHash:
        """
        Submit feedback for another agent (ERC-8004 v1.0).
        
        v1.0: Uses cryptographic signatures for feedback authorization.
        The agent owner must have pre-authorized this feedback via generate_feedback_authorization().
        
        Args:
            agent_id: Target agent ID receiving feedback
            score: Feedback score (0-100)
            feedback_auth: Signed authorization from agent owner
            tag1: Optional first tag for categorization
            tag2: Optional second tag for categorization
            file_uri: Optional URI to detailed feedback data (IPFS, 0G Storage, etc.)
            file_hash: Optional KECCAK-256 hash of file content
            
        Returns:
            Transaction hash
        """
        try:
            # Validate score
            score = min(100, max(0, int(score)))
            
            # Convert tags to bytes32
            tag1_bytes = b'\x00' * 32
            if tag1:
                tag1_encoded = tag1.encode()[:32]
                tag1_bytes = tag1_encoded + b'\x00' * (32 - len(tag1_encoded))
            
            tag2_bytes = b'\x00' * 32
            if tag2:
                tag2_encoded = tag2.encode()[:32]
                tag2_bytes = tag2_encoded + b'\x00' * (32 - len(tag2_encoded))
            
            # Convert file hash to bytes32 if provided
            file_hash_bytes = b'\x00' * 32
            if file_hash:
                if isinstance(file_hash, str):
                    if file_hash.startswith('0x'):
                        file_hash_bytes = bytes.fromhex(file_hash[2:])
                    else:
                        file_hash_bytes = bytes.fromhex(file_hash)
            
            rprint(f"[yellow]💬 Submitting feedback: {score}/100 for agent #{agent_id}[/yellow]")
            
            # v1.0: giveFeedback(agentId, score, tag1, tag2, fileuri, filehash, feedbackAuth)
            contract_call = self.reputation_registry.functions.giveFeedback(
                agent_id,
                score,
                tag1_bytes,
                tag2_bytes,
                file_uri,
                file_hash_bytes,
                feedback_auth
            )
            
            # Build and send transaction
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            
            account = self.wallet_manager.wallets[self.agent_name]
            signed_txn = self.w3.eth.account.sign_transaction(transaction, account.key)
            raw_transaction = getattr(signed_txn, 'raw_transaction', getattr(signed_txn, 'rawTransaction', None))
            if raw_transaction is None:
                raise Exception("Could not get raw transaction from signed transaction")
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Feedback submitted: {tx_hash.hex()[:10]}...[/green]")
                return tx_hash.hex()
            else:
                raise ContractError("Feedback submission failed")
                
        except Exception as e:
            raise ContractError(f"Failed to submit feedback: {str(e)}")
    
    def create_feedback_with_payment(
        self,
        agent_id: AgentID,
        score: int,
        feedback_auth: bytes,
        payment_proof: Optional['PaymentProof'] = None,
        tag1: str = "",
        tag2: str = "",
        skill: Optional[str] = None,
        task: Optional[str] = None,
        capability: Optional[str] = None,
        mcp_tool_name: Optional[str] = None,
        **additional_fields
    ) -> Tuple[str, str]:
        """
        Create ERC-8004 v1.0 compliant feedback JSON with optional payment proof.
        
        This is a convenience method that:
        1. Generates the feedback JSON structure per ERC-8004 v1.0 spec
        2. Optionally includes x402 payment proof
        3. Uploads to storage (IPFS/0G)
        4. Returns (file_uri, file_hash) ready for give_feedback()
        
        Args:
            agent_id: Target agent ID receiving feedback
            score: Feedback score (0-100)
            feedback_auth: Signed authorization from agent owner
            payment_proof: Optional PaymentProof from payment execution
            tag1: Optional first tag for categorization
            tag2: Optional second tag for categorization
            skill: Optional A2A skill identifier
            task: Optional A2A task identifier
            capability: Optional MCP capability ("prompts", "resources", "tools", "completions")
            mcp_tool_name: Optional MCP tool/prompt/resource name
            **additional_fields: Any additional custom fields
        
        Returns:
            Tuple of (file_uri, file_hash) ready for give_feedback()
        
        Example:
            # Execute payment
            payment_proof = sdk.x402_manager.execute_agent_payment(
                from_agent="Alice",
                to_agent="Bob",
                amount_usdc=10.0,
                service_description="Data analysis"
            )
            
            # Create feedback with payment proof (automatic formatting!)
            uri, hash = agent.create_feedback_with_payment(
                agent_id=server_agent_id,
                score=100,
                feedback_auth=auth,
                payment_proof=payment_proof,  # ✅ Automatically ERC-8004 v1.0 compliant
                skill="data-analysis",
                task="market-research"
            )
            
            # Submit feedback (URI already includes payment proof!)
            agent.give_feedback(agent_id, score, auth, file_uri=uri, file_hash=hash)
        """
        from datetime import datetime, timezone
        import json
        import hashlib
        
        # Build ERC-8004 v1.0 compliant feedback structure
        feedback_data = {
            # MUST fields (per ERC-8004 v1.0 spec)
            "agentRegistry": f"eip155:{self.network.value.chain_id}:{self.identity_registry.address}",
            "agentId": int(agent_id),
            "clientAddress": f"eip155:{self.network.value.chain_id}:{self.address}",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "feedbackAuth": feedback_auth.hex() if isinstance(feedback_auth, bytes) else feedback_auth,
            "score": min(100, max(0, int(score))),
        }
        
        # MAY fields (optional per spec)
        if tag1:
            feedback_data["tag1"] = tag1
        if tag2:
            feedback_data["tag2"] = tag2
        if skill:
            feedback_data["skill"] = skill
        if task:
            feedback_data["task"] = task
        if capability:
            feedback_data["capability"] = capability
        if mcp_tool_name:
            feedback_data["name"] = mcp_tool_name
        
        # ✅ Add payment proof if provided (ERC-8004 v1.0 compliant format)
        if payment_proof:
            # Extract addresses from payment proof
            from_address = self.address  # Client wallet
            
            # Get to_address from payment proof
            to_address = payment_proof.to_agent if hasattr(payment_proof, 'to_agent') else "unknown"
            if hasattr(payment_proof, 'receipt_data') and isinstance(payment_proof.receipt_data, dict):
                to_address = payment_proof.receipt_data.get('to_address', to_address)
            
            # Get network/chain ID
            chain_id = str(self.network.value.chain_id)
            if hasattr(payment_proof, 'network'):
                if isinstance(payment_proof.network, str):
                    # Extract chain ID from network string if present
                    if ':' in payment_proof.network:
                        chain_id = payment_proof.network.split(':')[-1]
                elif hasattr(payment_proof.network, 'value') and hasattr(payment_proof.network.value, 'chain_id'):
                    chain_id = str(payment_proof.network.value.chain_id)
            
            feedback_data["proof_of_payment"] = {
                "fromAddress": from_address,
                "toAddress": to_address,
                "chainId": chain_id,
                "txHash": payment_proof.transaction_hash  # ✅ On-chain verifiable
            }
            
            rprint(f"[cyan]💳 Including payment proof: {payment_proof.transaction_hash[:10]}...[/cyan]")
        
        # Add any additional custom fields
        feedback_data.update(additional_fields)
        
        # Convert to JSON
        feedback_json = json.dumps(feedback_data, indent=2)
        
        rprint(f"[yellow]📝 Creating feedback JSON ({len(feedback_json)} bytes)[/yellow]")
        
        # Upload to storage (IPFS or 0G)
        try:
            # Import storage provider if not already available
            from .providers.storage import LocalIPFSStorage
            
            # Create storage provider if needed
            if not hasattr(self, '_feedback_storage'):
                self._feedback_storage = LocalIPFSStorage()
            
            storage_result = self._feedback_storage.put(
                feedback_json.encode('utf-8'),
                mime="application/json"
            )
            
            if not storage_result.success:
                raise Exception(f"Storage failed: {storage_result.error}")
            
            # Compute file hash (KECCAK-256 for ERC-8004 v1.0 compatibility)
            file_hash = '0x' + hashlib.sha3_256(feedback_json.encode('utf-8')).hexdigest()
            
            rprint(f"[green]✅ Feedback uploaded: {storage_result.uri}[/green]")
            rprint(f"[cyan]   Hash: {file_hash[:20]}...[/cyan]")
            
            return storage_result.uri, file_hash
            
        except Exception as e:
            raise Exception(f"Failed to create feedback with payment: {str(e)}")
    
    @property
    def wallet_address(self) -> str:
        """Get the agent's wallet address."""
        return self.address