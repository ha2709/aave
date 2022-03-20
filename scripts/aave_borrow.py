from brownie import network, config
from .helpful_scripts import *
from .get_weth import *
from web3 import Web3

amount = Web3.toWei(0.000001,"ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, erc20_address, account )
    print("Depositing ...")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from":account})
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow !")
    dai_eth_price_feed = config["networks"][network.show_active()]["dai_eth_price_feed"]
    dai_eth_price = get_asset_price(dai_eth_price_feed)
    amount_dai_to_borrow = (1/dai_eth_price) * (borrowable_eth*.05)
    # convert to dai borrowable
    print(f"We are going to borrow {amount_dai_to_borrow} DAI ")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(dai_address,
        Web3.toWei(amount_dai_to_borrow,"ether"),
        1,
        0,
        account.address,
        {"from":account}
        )
    borrow_tx.wait(1)
    print(" We are borrow some DAI")
    get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)
    print("You just deposited, borrowed, and repayed with Aave ...")

def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from":account},
    )
    repay_tx.wait(1)
    print("Repaid !")

def get_asset_price(price_feed_address):
    #ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]

    print(f"The DAI/ETH price is {latest_price}")
    converted_latest_price = Web3.fromWei(latest_price,"ether")
    print(f"{converted_latest_price}")
    return float(converted_latest_price)

def get_borrowable_data(lending_pool, account):
    (
        total_collateral_ETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor
    )= lending_pool.getUserAccountData(account.address)
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    total_collateral_ETH = Web3.fromWei(total_collateral_ETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH,"ether")
    print(f"You have {total_collateral_ETH} worth of ETH Deposited")
    print(f"You can borrow {availableBorrowsETH} worth of ETH Borrow")
    print(f"You have {totalDebtETH} worth of ETH Debt")
    return (float(availableBorrowsETH), float(totalDebtETH))

def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token ...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from":account})
    tx.wait(1)
    # ABI
    # Address 
    pass 

def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    #ABI
    #Address - Check 
    lending_pool = interface.ILendingPool(lending_pool_address)    
    return lending_pool