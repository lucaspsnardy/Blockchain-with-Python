# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
import subprocess 
from constants import *
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import *
from web3 import Web3
from eth_account import Account 


# Load and set environment variables
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1.8545"))
mnemonic=os.getenv("mnemonic", "inmate nice scare kit decade asset border faint attract upon seat endorse")

load_dotenv()

print(mnemonic)

# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    """Use the subprocess library to call the php file script from Python"""
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json' 
    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
   
    keys = json.loads(output)
    return  keys

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"eth", "btc-test", "btc"}
numderive = 3

# Setting the dictionarry
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(os.getenv('mnemonic'), coin, numderive=3)

# Creating a private keys object
eth_PrivateKey = keys["eth"][0]['privkey']
btc_PrivateKey = keys['btc-test'][0]['privkey']


print(json.dumps(eth_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(btc_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(keys, indent=4, sort_keys=True

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    """Convert the privkey string in a child key to an account object that bit or web3.py can use to transact"""
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
eth_acc = priv_key_to_account(ETH,eth_PrivateKey)
btc_acc = priv_key_to_account(BTCTEST,btc_PrivateKey)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_trx(coin, account, recipient, amount):
    """create the raw, unsigned transaction that contains all metadata needed to transact"""
    global trx_data
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        trx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return trx_data

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_trx(coin, account, recipient, amount):
    """call create_trx, sign the transaction, then send it to the designated network"""
    if coin == "eth": 
        trx_eth = create_trx(coin,account, recipient, amount)
        sign = account.signTransaction(trx_eth)
        result = w3.eth.sendRawTransaction(sign.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        trx_btctest= create_trx(coin,account,recipient,amount)
        sign_trx_btctest = account.sign_transaction(trx_btctest)
        from bit.network import NetworkAPI
        NetworkAPI.broadcast_tx_testnet(sign_trx_btctest)       
        return sign_trx_btctest

