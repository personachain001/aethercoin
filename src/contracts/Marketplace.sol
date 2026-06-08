// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20.sol";

/**
 * @title Marketplace
 * @dev A simple marketplace for trading items using AetherCoin
 */
contract Marketplace {
    address public owner;
    address public aetherCoin;
    
    struct Item {
        uint256 id;
        address seller;
        string name;
        string description;
        uint256 price;
        bool isActive;
        uint256 createdAt;
    }
    
    struct Offer {
        uint256 id;
        uint256 itemId;
        address buyer;
        uint256 amount;
        bool isActive;
        uint256 createdAt;
    }
    
    mapping(uint256 => Item) public items;
    mapping(uint256 => Offer) public offers;
    mapping(address => uint256[]) public userItems;
    mapping(address => uint256[]) public userOffers;
    
    uint256 public itemCount;
    uint256 public offerCount;
    uint256 public platformFeePercent = 250; // 2.5%
    
    event ItemListed(uint256 indexed itemId, address indexed seller, string name, uint256 price);
    event ItemSold(uint256 indexed itemId, address indexed seller, address indexed buyer, uint256 price);
    event OfferMade(uint256 indexed offerId, uint256 indexed itemId, address indexed buyer, uint256 amount);
    event OfferAccepted(uint256 indexed offerId, uint256 indexed itemId);
    event OfferCancelled(uint256 indexed offerId);
    event ItemDelisted(uint256 indexed itemId);
    event PlatformFeeUpdated(uint256 newFeePercent);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Marketplace: caller is not the owner");
        _;
    }
    
    modifier onlySeller(uint256 _itemId) {
        require(items[_itemId].seller == msg.sender, "Marketplace: caller is not the seller");
        _;
    }
    
    constructor(address _aetherCoin) {
        owner = msg.sender;
        aetherCoin = _aetherCoin;
    }
    
    /**
     * @dev List a new item for sale
     */
    function listItem(
        string memory _name,
        string memory _description,
        uint256 _price
    ) external returns (uint256) {
        require(_price > 0, "Marketplace: price must be greater than 0");
        require(bytes(_name).length > 0, "Marketplace: name cannot be empty");
        
        itemCount++;
        items[itemCount] = Item({
            id: itemCount,
            seller: msg.sender,
            name: _name,
            description: _description,
            price: _price,
            isActive: true,
            createdAt: block.timestamp
        });
        
        userItems[msg.sender].push(itemCount);
        
        emit ItemListed(itemCount, msg.sender, _name, _price);
        
        return itemCount;
    }
    
    /**
     * @dev Buy an item directly
     */
    function buyItem(uint256 _itemId) external {
        Item storage item = items[_itemId];
        require(item.isActive, "Marketplace: item is not active");
        require(item.seller != msg.sender, "Marketplace: cannot buy your own item");
        require(item.price > 0, "Marketplace: item has no price");
        
        // Calculate platform fee
        uint256 fee = (item.price * platformFeePercent) / 10000;
        uint256 sellerAmount = item.price - fee;
        
        // Transfer tokens
        IERC20(aetherCoin).transferFrom(msg.sender, item.seller, sellerAmount);
        if (fee > 0) {
            IERC20(aetherCoin).transferFrom(msg.sender, owner, fee);
        }
        
        // Mark item as sold
        item.isActive = false;
        
        emit ItemSold(_itemId, item.seller, msg.sender, item.price);
    }
    
    /**
     * @dev Make an offer on an item
     */
    function makeOffer(uint256 _itemId, uint256 _amount) external returns (uint256) {
        Item storage item = items[_itemId];
        require(item.isActive, "Marketplace: item is not active");
        require(item.seller != msg.sender, "Marketplace: cannot offer on your own item");
        require(_amount > 0, "Marketplace: amount must be greater than 0");
        
        // Transfer tokens to escrow
        IERC20(aetherCoin).transferFrom(msg.sender, address(this), _amount);
        
        offerCount++;
        offers[offerCount] = Offer({
            id: offerCount,
            itemId: _itemId,
            buyer: msg.sender,
            amount: _amount,
            isActive: true,
            createdAt: block.timestamp
        });
        
        userOffers[msg.sender].push(offerCount);
        
        emit OfferMade(offerCount, _itemId, msg.sender, _amount);
        
        return offerCount;
    }
    
    /**
     * @dev Accept an offer on your item
     */
    function acceptOffer(uint256 _offerId) external {
        Offer storage offer = offers[_offerId];
        Item storage item = items[offer.itemId];
        
        require(offer.isActive, "Marketplace: offer is not active");
        require(item.seller == msg.sender, "Marketplace: only seller can accept offers");
        require(item.isActive, "Marketplace: item is not active");
        
        // Calculate platform fee
        uint256 fee = (offer.amount * platformFeePercent) / 10000;
        uint256 sellerAmount = offer.amount - fee;
        
        // Transfer tokens from escrow
        IERC20(aetherCoin).transfer(msg.sender, sellerAmount);
        if (fee > 0) {
            IERC20(aetherCoin).transfer(owner, fee);
        }
        
        // Mark offer and item as completed
        offer.isActive = false;
        item.isActive = false;
        
        emit OfferAccepted(_offerId, offer.itemId);
        emit ItemSold(offer.itemId, item.seller, offer.buyer, offer.amount);
    }
    
    /**
     * @dev Cancel an offer
     */
    function cancelOffer(uint256 _offerId) external {
        Offer storage offer = offers[_offerId];
        require(offer.buyer == msg.sender, "Marketplace: only buyer can cancel offers");
        require(offer.isActive, "Marketplace: offer is not active");
        
        // Refund tokens from escrow
        IERC20(aetherCoin).transfer(msg.sender, offer.amount);
        
        offer.isActive = false;
        
        emit OfferCancelled(_offerId);
    }
    
    /**
     * @dev Delist an item
     */
    function delistItem(uint256 _itemId) external onlySeller(_itemId) {
        Item storage item = items[_itemId];
        require(item.isActive, "Marketplace: item is not active");
        
        item.isActive = false;
        
        emit ItemDelisted(_itemId);
    }
    
    /**
     * @dev Update platform fee (only owner)
     */
    function updatePlatformFee(uint256 _newFeePercent) external onlyOwner {
        require(_newFeePercent <= 1000, "Marketplace: fee cannot exceed 10%");
        platformFeePercent = _newFeePercent;
        
        emit PlatformFeeUpdated(_newFeePercent);
    }
    
    /**
     * @dev Get item details
     */
    function getItem(uint256 _itemId) external view returns (
        uint256 id,
        address seller,
        string memory name,
        string memory description,
        uint256 price,
        bool isActive,
        uint256 createdAt
    ) {
        Item storage item = items[_itemId];
        return (
            item.id,
            item.seller,
            item.name,
            item.description,
            item.price,
            item.isActive,
            item.createdAt
        );
    }
    
    /**
     * @dev Get offer details
     */
    function getOffer(uint256 _offerId) external view returns (
        uint256 id,
        uint256 itemId,
        address buyer,
        uint256 amount,
        bool isActive,
        uint256 createdAt
    ) {
        Offer storage offer = offers[_offerId];
        return (
            offer.id,
            offer.itemId,
            offer.buyer,
            offer.amount,
            offer.isActive,
            offer.createdAt
        );
    }
    
    /**
     * @dev Get user's items
     */
    function getUserItems(address _user) external view returns (uint256[] memory) {
        return userItems[_user];
    }
    
    /**
     * @dev Get user's offers
     */
    function getUserOffers(address _user) external view returns (uint256[] memory) {
        return userOffers[_user];
    }
    
    /**
     * @dev Withdraw platform fees (only owner)
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = IERC20(aetherCoin).balanceOf(address(this));
        require(balance > 0, "Marketplace: no fees to withdraw");
        
        IERC20(aetherCoin).transfer(owner, balance);
    }
}