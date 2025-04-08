// Space Hackathon: Intergalactic Inventory Manager
class IntergalacticInventory {
  constructor() {
    // Initialize storage locations with some default spacecraft
    this.storageLocations = {
      'ISS': { items: {}, capacity: 1000 },
      'Mars Rover': { items: {}, capacity: 500 },
      'Lunar Base': { items: {}, capacity: 2000 },
      'Starship Enterprise': { items: {}, capacity: 3000 }
    };
    
    // Track item transfers
    this.transferLog = [];
    this.nextItemId = 1;
  }

  /**
   * Add a new storage location
   * @param {string} locationName - Name of the new location
   * @param {number} capacity - Storage capacity in kg
   */
  addStorageLocation(locationName, capacity) {
    if (this.storageLocations[locationName]) {
      throw new Error(`Location ${locationName} already exists`);
    }
    this.storageLocations[locationName] = {
      items: {},
      capacity: capacity
    };
    console.log(`Added new storage location: ${locationName}`);
  }

  /**
   * Add an item to a storage location
   * @param {string} location - Storage location name
   * @param {string} name - Item name
   * @param {number} quantity - Item quantity
   * @param {number} weight - Weight per item in kg
   * @param {string} category - Item category
   * @param {Date} expiry - Expiry date (optional)
   */
  addItem(location, name, quantity, weight, category, expiry = null) {
    if (!this.storageLocations[location]) {
      throw new Error(`Location ${location} not found`);
    }

    const locationData = this.storageLocations[location];
    const totalWeight = quantity * weight;
    const currentWeight = this.getCurrentWeight(location);

    if (currentWeight + totalWeight > locationData.capacity) {
      throw new Error(`Adding ${totalWeight}kg would exceed ${location}'s capacity`);
    }

    const itemId = this.nextItemId++;
    const item = {
      id: itemId,
      name,
      quantity,
      weight,
      totalWeight,
      category,
      expiry,
      location,
      addedAt: new Date()
    };

    locationData.items[itemId] = item;
    console.log(`Added ${quantity} ${name}(s) to ${location}`);
    return itemId;
  }

  /**
   * Remove an item from storage
   * @param {number} itemId - ID of the item to remove
   * @param {number} [quantity] - Quantity to remove (defaults to all)
   */
  removeItem(itemId, quantity = null) {
    const item = this.findItemById(itemId);
    if (!item) {
      throw new Error(`Item with ID ${itemId} not found`);
    }

    const location = item.location;
    const locationData = this.storageLocations[location];

    if (quantity === null || quantity >= item.quantity) {
      // Remove all
      delete locationData.items[itemId];
      console.log(`Removed all ${item.name} from ${location}`);
    } else {
      // Remove partial quantity
      item.quantity -= quantity;
      item.totalWeight = item.quantity * item.weight;
      console.log(`Removed ${quantity} ${item.name}(s) from ${location}`);
    }
  }

  /**
   * Transfer items between locations
   * @param {number} itemId - ID of item to transfer
   * @param {string} newLocation - Destination location
   * @param {number} [quantity] - Quantity to transfer (defaults to all)
   */
  transferItem(itemId, newLocation, quantity = null) {
    const item = this.findItemById(itemId);
    if (!item) {
      throw new Error(`Item with ID ${itemId} not found`);
    }

    if (!this.storageLocations[newLocation]) {
      throw new Error(`Destination location ${newLocation} not found`);
    }

    if (item.location === newLocation) {
      throw new Error(`Item is already at ${newLocation}`);
    }

    const transferQuantity = quantity === null ? item.quantity : quantity;
    const transferWeight = transferQuantity * item.weight;

    // Check destination capacity
    const destCurrentWeight = this.getCurrentWeight(newLocation);
    if (destCurrentWeight + transferWeight > this.storageLocations[newLocation].capacity) {
      throw new Error(`Transfer would exceed ${newLocation}'s capacity`);
    }

    // Remove from source
    if (transferQuantity === item.quantity) {
      this.removeItem(itemId);
    } else {
      this.removeItem(itemId, transferQuantity);
    }

    // Add to destination
    const newItemId = this.addItem(
      newLocation,
      item.name,
      transferQuantity,
      item.weight,
      item.category,
      item.expiry
    );

    // Log the transfer
    const transferRecord = {
      itemId: itemId,
      newItemId: newItemId,
      itemName: item.name,
      from: item.location,
      to: newLocation,
      quantity: transferQuantity,
      date: new Date()
    };

    this.transferLog.push(transferRecord);
    console.log(`Transferred ${transferQuantity} ${item.name}(s) from ${item.location} to ${newLocation}`);
    return transferRecord;
  }

  /**
   * Find an item by its ID
   * @param {number} itemId - Item ID to search for
   * @returns {object|null} The item object or null if not found
   */
  findItemById(itemId) {
    for (const locationName in this.storageLocations) {
      const location = this.storageLocations[locationName];
      if (location.items[itemId]) {
        return location.items[itemId];
      }
    }
    return null;
  }

  /**
   * Search for items by name or category
   * @param {string} query - Search query
   * @param {string} [field='name'] - Field to search ('name' or 'category')
   * @returns {array} Array of matching items
   */
  searchItems(query, field = 'name') {
    const results = [];
    const searchTerm = query.toLowerCase();

    for (const locationName in this.storageLocations) {
      const location = this.storageLocations[locationName];
      for (const itemId in location.items) {
        const item = location.items[itemId];
        if (item[field].toLowerCase().includes(searchTerm)) {
          results.push(item);
        }
      }
    }

    return results;
  }

  /**
   * Get current weight used at a location
   * @param {string} location - Location name
   * @returns {number} Total weight in kg
   */
  getCurrentWeight(location) {
    if (!this.storageLocations[location]) {
      throw new Error(`Location ${location} not found`);
    }

    let total = 0;
    for (const itemId in this.storageLocations[location].items) {
      total += this.storageLocations[location].items[itemId].totalWeight;
    }
    return total;
  }

  /**
   * Get storage location summary
   * @param {string} location - Location name
   * @returns {object} Summary object
   */
  getLocationSummary(location) {
    if (!this.storageLocations[location]) {
      throw new Error(`Location ${location} not found`);
    }

    const locationData = this.storageLocations[location];
    const currentWeight = this.getCurrentWeight(location);
    const itemCount = Object.keys(locationData.items).length;

    return {
      location,
      capacity: locationData.capacity,
      currentWeight,
      availableSpace: locationData.capacity - currentWeight,
      itemCount,
      utilization: (currentWeight / locationData.capacity * 100).toFixed(2) + '%'
    };
  }

  /**
   * Get all items expiring before a certain date
   * @param {Date} date - Cutoff date
   * @returns {array} Array of expiring items
   */
  getExpiringItems(date) {
    const results = [];
    const cutoff = new Date(date);

    for (const locationName in this.storageLocations) {
      const location = this.storageLocations[locationName];
      for (const itemId in location.items) {
        const item = location.items[itemId];
        if (item.expiry && new Date(item.expiry) <= cutoff) {
          results.push(item);
        }
      }
    }

    return results;
  }

  /**
   * Generate a full inventory report
   * @returns {object} Comprehensive inventory report
   */
  generateInventoryReport() {
    const report = {
      timestamp: new Date(),
      totalLocations: Object.keys(this.storageLocations).length,
      locations: {},
      totalItems: 0,
      totalWeight: 0,
      categories: {},
      expiringSoon: this.getExpiringItems(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)) // 30 days from now
    };

    for (const locationName in this.storageLocations) {
      const location = this.storageLocations[locationName];
      const locationSummary = this.getLocationSummary(locationName);
      report.locations[locationName] = locationSummary;
      report.totalItems += locationSummary.itemCount;
      report.totalWeight += locationSummary.currentWeight;

      // Count items by category
      for (const itemId in location.items) {
        const item = location.items[itemId];
        if (!report.categories[item.category]) {
          report.categories[item.category] = 0;
        }
        report.categories[item.category] += item.quantity;
      }
    }

    return report;
  }
}

// Example Usage
const inventory = new IntergalacticInventory();

// Add some items
inventory.addItem('ISS', 'Oxygen Tank', 10, 15, 'Life Support', new Date('2025-12-31'));
inventory.addItem('ISS', 'Food Packet', 50, 0.5, 'Consumables', new Date('2024-06-30'));
inventory.addItem('Mars Rover', 'Drill Bit', 5, 2, 'Equipment');
inventory.addItem('Lunar Base', 'Solar Panel', 8, 20, 'Power Systems');

// Add a new storage location
inventory.addStorageLocation('Jupiter Station', 5000);

// Transfer some items
inventory.transferItem(1, 'Jupiter Station', 5); // Move half the oxygen tanks

// Search for items
const foodItems = inventory.searchItems('food');
console.log('Food items:', foodItems);

// Get a location summary
const issSummary = inventory.getLocationSummary('ISS');
console.log('ISS Summary:', issSummary);

// Generate full report
const report = inventory.generateInventoryReport();
console.log('Inventory Report:', report);