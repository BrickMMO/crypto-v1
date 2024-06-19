import random
import time
import hashlib
from web3 import Web3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Connect to Alchemy Sepolia network
alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/_e6Iju4ygOOaYET4C9UnhJL8vtkdaUcr"
web3 = Web3(Web3.HTTPProvider(alchemy_url))

# Check if connected to the network
if not web3.is_connected():
    logging.error("Failed to connect to the Ethereum network")
    exit()

# Contract address and ABI
contract_address = "0xBA77c807d15da4E64260CCDD0F8d849249B407bC"
contract_abi = [{"inputs":[{"internalType":"uint256","name":"_interval","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"tokenAddress","type":"address"}],"name":"TokenAddressSet","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"TokensWithdrawn","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"bytes32","name":"codeHash","type":"bytes32"}],"name":"ValidationCodeSet","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"interval","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"WithdrawSettingsUpdated","type":"event"},{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"}],"name":"setTokenAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes32","name":"codeHash","type":"bytes32"}],"name":"setValidationCode","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_interval","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"setWithdrawSettings","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdrawAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"withdrawInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"code","type":"string"}],"name":"withdrawTokens","outputs":[],"stateMutability":"nonpayable","type":"function"}]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Ethereum account details
owner_address = "0x5f8585DcE6cf33e2d63a4BaaE6E224c0F4bfbFcD"
private_key = "b47f0a6afb7d15b98f4a85970b1b458d321d2a2b93ce3abe8437c52269ab4a7b"

def check_balance(address):
    balance = web3.eth.get_balance(address)
    logging.info(f"Balance of {address}: {Web3.from_wei(balance, 'ether')} ETH")
    return balance

def generate_validation_code():
    return str(random.randint(100000, 999999))

#Encrypt the validation code 
def hash_code(code):
    return Web3.to_hex(Web3.solidity_keccak(['string'], [code]))

def send_code_to_smart_contract(user_address, code):
    try:
        check_balance(owner_address)  # Check balance before sending transaction
        hashed_code = hash_code(code) # Encrypt the validation code
        nonce = web3.eth.get_transaction_count(owner_address, "pending")
        txn = contract.functions.setValidationCode(user_address, hashed_code).build_transaction({
            'chainId': 11155111,  # Sepolia
            'gas': 2000000,
            'gasPrice': Web3.to_wei('30', 'gwei'),
            'nonce': nonce,
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logging.info(f"Transaction hash: {web3.to_hex(tx_hash)}")
    except Exception as e:
        logging.error(f"An error occurred while setting validation code: {e}")

def set_token_address(token_address):
    try:
        check_balance(owner_address)
        nonce = web3.eth.get_transaction_count(owner_address, "pending")
        txn = contract.functions.setTokenAddress(token_address).build_transaction({
            'chainId': 11155111,
            'gas': 2000000,
            'gasPrice': web3.to_wei('30', 'gwei'), 
            'nonce': nonce,
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logging.info(f"Transaction hash for setting token address: {web3.to_hex(tx_hash)}")
    except Exception as e:
        logging.error(f"An error occurred while setting token address: {e}")

def main():
    user_address = "0x227BAcef86D6eD56815bceE6E548031DBb521dc1" 
    token_address = "0x86334641030EE6a4401399560c2e5612DEee394E" 
    while True:
        code = generate_validation_code()
        logging.info(f"Generated validation code: {code}")
        send_code_to_smart_contract(user_address, code)
        time.sleep(300)  # 300 seconds

if __name__ == "__main__":
    main()
