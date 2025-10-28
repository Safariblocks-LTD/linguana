LINGUANA SMART CONTRACTS
========================

This directory contains Solidity smart contracts for managing USDC rewards on Base L2.

CONTRACT: LinguanaRewards.sol
-----------------------------
Purpose: Escrow and distribute USDC rewards for validated audio contributions

Key Functions:
- fund(amount): Add USDC to reward pool
- submitWork(workId, contributor, amount, clipId): Register validated work
- releaseWork(workId): Release reward to contributor
- batchReleaseWorks(workIds[]): Release multiple rewards in one transaction

DEPLOYMENT INSTRUCTIONS
-----------------------

1. Install Dependencies:
   npm install --save-dev hardhat @openzeppelin/contracts

2. Create hardhat.config.js:
   require("@nomicfoundation/hardhat-toolbox");
   
   module.exports = {
     solidity: "0.8.20",
     networks: {
       baseSepolia: {
         url: "https://sepolia.base.org",
         accounts: [process.env.PRIVATE_KEY],
         chainId: 84532
       },
       base: {
         url: "https://mainnet.base.org",
         accounts: [process.env.PRIVATE_KEY],
         chainId: 8453
       }
     }
   };

3. Compile Contract:
   npx hardhat compile

4. Deploy to Base Sepolia (Testnet):
   npx hardhat run scripts/deploy.js --network baseSepolia
   
   USDC on Base Sepolia: 0x036CbD53842c5426634e7929541eC2318f3dCF7e

5. Deploy to Base Mainnet:
   npx hardhat run scripts/deploy.js --network base
   
   USDC on Base Mainnet: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

6. Verify Contract:
   npx hardhat verify --network baseSepolia <CONTRACT_ADDRESS> <USDC_ADDRESS>

USAGE FROM DJANGO BACKEND
--------------------------
The rewards/blockchain.py module interacts with this contract:

1. Fund pool:
   - Admin transfers USDC to contract address
   - Call fund() function with amount

2. Submit work:
   - Backend calls submitWork() after consensus reached
   - Stores workId (clip ID hash) on-chain

3. Release reward:
   - Backend calls releaseWork() to transfer USDC to contributor
   - Or use batchReleaseWorks() for multiple releases

CONTRACT ADDRESSES
------------------
Base Sepolia (Testnet):
- USDC: 0x036CbD53842c5426634e7929541eC2318f3dCF7e
- LinguanaRewards: <deploy and add here>

Base Mainnet:
- USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
- LinguanaRewards: <deploy and add here>

SECURITY CONSIDERATIONS
-----------------------
- Contract is Ownable (only backend wallet can submit/release work)
- ReentrancyGuard prevents reentrancy attacks
- Pausable for emergency situations
- Emergency withdraw only when paused
- All USDC transfers use SafeERC20 patterns

GAS OPTIMIZATION
----------------
- Use batchReleaseWorks() for multiple releases
- Estimated gas per release: ~50,000-70,000
- Base L2 has low gas fees (~$0.01-0.05 per transaction)

TESTING
-------
Create test file: test/LinguanaRewards.test.js
Run tests: npx hardhat test

MONITORING
----------
- Monitor contract balance
- Track totalFunded vs totalDistributed
- Alert if balance drops below threshold
- Log all transactions for audit trail
