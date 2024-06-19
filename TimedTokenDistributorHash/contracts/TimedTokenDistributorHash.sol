// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

interface IERC20 {
    function transfer(
        address recipient,
        uint256 amount
    ) external returns (bool);
}

contract TimedTokenDistributorHash {
    address private owner;
    uint256 public withdrawInterval;
    uint256 public withdrawAmount;
    mapping(address => uint256) private lastWithdrawTime;
    mapping(address => bytes32) private validationCodes;
    IERC20 private token;

    event TokensWithdrawn(address indexed user, uint256 amount);
    event WithdrawSettingsUpdated(uint256 interval, uint256 amount);
    event ValidationCodeSet(address indexed user, bytes32 codeHash);
    event TokenAddressSet(address tokenAddress);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 _interval, uint256 _amount) {
        owner = msg.sender;
        withdrawInterval = _interval;
        withdrawAmount = _amount;
    }

    function setWithdrawSettings(
        uint256 _interval,
        uint256 _amount
    ) public onlyOwner {
        withdrawInterval = _interval;
        withdrawAmount = _amount;
        emit WithdrawSettingsUpdated(_interval, _amount);
    }

    function setValidationCode(
        address user,
        bytes32 codeHash
    ) public onlyOwner {
        validationCodes[user] = codeHash;
        emit ValidationCodeSet(user, codeHash);
    }

    function setTokenAddress(address _tokenAddress) public onlyOwner {
        token = IERC20(_tokenAddress);
        emit TokenAddressSet(_tokenAddress);
    }

    function withdrawTokens(string memory code) public {
        require(
            block.timestamp >= lastWithdrawTime[msg.sender] + withdrawInterval,
            "Wait for the next interval"
        );
        require(
            validationCodes[msg.sender] == keccak256(abi.encodePacked(code)),
            "Invalid validation code"
        );

        lastWithdrawTime[msg.sender] = block.timestamp;

        // Transfer tokens to the user
        require(
            token.transfer(msg.sender, withdrawAmount),
            "Token transfer failed"
        );

        emit TokensWithdrawn(msg.sender, withdrawAmount);
    }
}
