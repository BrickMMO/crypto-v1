const { network, ethers } = require("hardhat")
const { networkConfig, developmentChains } = require("../helper-hardhat-config")
const { verify } = require("../utils/verify")
require("dotenv").config()

module.exports = async ({ getNamedAccounts, deployments }) => {
    const { deploy, log } = deployments
    const { deployer } = await getNamedAccounts()
    const chainId = network.config.chainId

    let ethUsdPriceFeedAddress
    if (chainId == 31337) {
        const ethUsdAggregator = await deployments.get("MockV3Aggregator")
        ethUsdPriceFeedAddress = ethUsdAggregator.address
    } else {
        ethUsdPriceFeedAddress = networkConfig[chainId]["ethUsdPriceFeed"]
    }

    log("----------------------------------------------------")
    log("Deploying TimedTokenDistributorHash and waiting for confirmations...")

    const withdrawInterval = 300 // 5 minutes in seconds
    const withdrawAmount = ethers.utils.parseUnits("10", 18) // Example amount (10 tokens with 18 decimals)
    const tokenAddress = "0x86334641030EE6a4401399560c2e5612DEee394E" // Update with your ERC20 token contract address

    const ttd = await deploy("TimedTokenDistributorHash", {
        from: deployer,
        args: [withdrawInterval, withdrawAmount], // pass the required arguments here
        log: true,
        // we need to wait if on a live network so we can verify properly
        waitConfirmations: network.config.blockConfirmations || 1,
    })

    log(`TimedTokenDistributorHash deployed at ${ttd.address}`)

    // Set the ERC20 token address
    const distributorContract = await ethers.getContractAt(
        "TimedTokenDistributorHash",
        ttd.address,
    )
    const tx = await distributorContract.setTokenAddress(tokenAddress)
    await tx.wait(1)
    log(`Token address set to ${tokenAddress}`)

    if (
        !developmentChains.includes(network.name) &&
        process.env.ETHERSCAN_API_KEY
    ) {
        await verify(ttd.address, [withdrawInterval, withdrawAmount])
    }
}

module.exports.tags = ["all", "ttd"]
