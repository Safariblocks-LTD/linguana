// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title LinguanaRewards
 * @dev Smart contract for managing USDC rewards on Base L2
 * @notice This contract handles escrow and distribution of USDC rewards for validated audio contributions
 */
contract LinguanaRewards is Ownable, ReentrancyGuard, Pausable {
    IERC20 public immutable usdc;
    
    uint256 public totalFunded;
    uint256 public totalDistributed;
    uint256 public totalContributors;
    
    struct Work {
        address contributor;
        uint256 amount;
        bool released;
        uint256 timestamp;
        string clipId;
    }
    
    mapping(bytes32 => Work) public works;
    mapping(address => uint256) public contributorEarnings;
    mapping(address => uint256) public contributorWorkCount;
    
    event Funded(address indexed funder, uint256 amount);
    event WorkSubmitted(bytes32 indexed workId, address indexed contributor, uint256 amount, string clipId);
    event WorkReleased(bytes32 indexed workId, address indexed contributor, uint256 amount);
    event EmergencyWithdraw(address indexed owner, uint256 amount);
    
    /**
     * @dev Constructor
     * @param _usdcAddress Address of USDC token on Base L2
     */
    constructor(address _usdcAddress) {
        require(_usdcAddress != address(0), "Invalid USDC address");
        usdc = IERC20(_usdcAddress);
    }
    
    /**
     * @dev Fund the reward pool with USDC
     * @param amount Amount of USDC to fund
     */
    function fund(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(usdc.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        totalFunded += amount;
        emit Funded(msg.sender, amount);
    }
    
    /**
     * @dev Submit work for a contributor (called by backend)
     * @param workId Unique identifier for the work
     * @param contributor Address of the contributor
     * @param amount Reward amount in USDC
     * @param clipId Audio clip ID
     */
    function submitWork(
        bytes32 workId,
        address contributor,
        uint256 amount,
        string calldata clipId
    ) external onlyOwner nonReentrant whenNotPaused {
        require(contributor != address(0), "Invalid contributor address");
        require(amount > 0, "Amount must be greater than 0");
        require(works[workId].contributor == address(0), "Work already exists");
        require(usdc.balanceOf(address(this)) >= amount, "Insufficient balance");
        
        works[workId] = Work({
            contributor: contributor,
            amount: amount,
            released: false,
            timestamp: block.timestamp,
            clipId: clipId
        });
        
        if (contributorWorkCount[contributor] == 0) {
            totalContributors++;
        }
        contributorWorkCount[contributor]++;
        
        emit WorkSubmitted(workId, contributor, amount, clipId);
    }
    
    /**
     * @dev Release reward to contributor after validation
     * @param workId Unique identifier for the work
     */
    function releaseWork(bytes32 workId) external onlyOwner nonReentrant whenNotPaused {
        Work storage work = works[workId];
        require(work.contributor != address(0), "Work does not exist");
        require(!work.released, "Work already released");
        require(usdc.balanceOf(address(this)) >= work.amount, "Insufficient balance");
        
        work.released = true;
        contributorEarnings[work.contributor] += work.amount;
        totalDistributed += work.amount;
        
        require(usdc.transfer(work.contributor, work.amount), "Transfer failed");
        
        emit WorkReleased(workId, work.contributor, work.amount);
    }
    
    /**
     * @dev Batch release multiple works
     * @param workIds Array of work IDs to release
     */
    function batchReleaseWorks(bytes32[] calldata workIds) external onlyOwner nonReentrant whenNotPaused {
        for (uint256 i = 0; i < workIds.length; i++) {
            bytes32 workId = workIds[i];
            Work storage work = works[workId];
            
            if (work.contributor != address(0) && !work.released) {
                work.released = true;
                contributorEarnings[work.contributor] += work.amount;
                totalDistributed += work.amount;
                
                require(usdc.transfer(work.contributor, work.amount), "Transfer failed");
                emit WorkReleased(workId, work.contributor, work.amount);
            }
        }
    }
    
    /**
     * @dev Get work details
     * @param workId Unique identifier for the work
     */
    function getWork(bytes32 workId) external view returns (
        address contributor,
        uint256 amount,
        bool released,
        uint256 timestamp,
        string memory clipId
    ) {
        Work memory work = works[workId];
        return (
            work.contributor,
            work.amount,
            work.released,
            work.timestamp,
            work.clipId
        );
    }
    
    /**
     * @dev Get contributor stats
     * @param contributor Address of the contributor
     */
    function getContributorStats(address contributor) external view returns (
        uint256 earnings,
        uint256 workCount
    ) {
        return (
            contributorEarnings[contributor],
            contributorWorkCount[contributor]
        );
    }
    
    /**
     * @dev Get contract balance
     */
    function getBalance() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }
    
    /**
     * @dev Get remaining pool balance
     */
    function getRemainingBalance() external view returns (uint256) {
        return totalFunded - totalDistributed;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdraw (only owner, when paused)
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(uint256 amount) external onlyOwner whenPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(usdc.balanceOf(address(this)) >= amount, "Insufficient balance");
        
        require(usdc.transfer(owner(), amount), "Transfer failed");
        emit EmergencyWithdraw(owner(), amount);
    }
}
