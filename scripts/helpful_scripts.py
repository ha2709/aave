from brownie import (\
    network, \
    config, accounts,
    
)  
# from brownie  import DECIMAL
# from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development","ganache-local"]
 

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        return accounts[0]
    else:
        return accounts.add(config['wallets']['from_key'])
