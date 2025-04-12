# Shop &amp; Armory System Specification

## 1. Overview

This document outlines the design for the Shop and Armory system, allowing players to buy items/weapons and sell unwanted items using gold. Based on Fire Emblem mechanics, particularly considering Thracia 776's economic context (scarce gold, high prices).

## 2. Data Structures

### 2.1. Player Funds
```pseudocode
GameState {
  player_gold: Integer // Global variable tracking party funds
}
```
*TDD Anchor: test_initial_gold_is_zero_or_defined_start_value*
*TDD Anchor: test_gold_can_be_added*
*TDD Anchor: test_gold_can_be_deducted*
*TDD Anchor: test_gold_cannot_go_below_zero*

### 2.2. Shop/Armory Inventory Definition
```pseudocode
// Defined per chapter or map instance
ShopInventory {
  shop_id: String // Unique identifier for this shop instance
  type: Enum("Shop", "Armory", "SecretShop")
  available_items: List<ShopItemEntry>
  requires_member_card: Boolean // For Secret Shops
}

ShopItemEntry {
  item_id: String // Reference to ItemData
  stock: Integer // -1 for unlimited, >= 0 for limited stock
  // Purchase price is derived from ItemData.buy_price
}
```
*TDD Anchor: test_load_shop_inventory_data*
*TDD Anchor: test_secret_shop_requires_member_card*

### 2.3. Map Tile Data
```pseudocode
// Part of TerrainData definition
TerrainType {
  name: String
  is_shop_tile: Boolean // True for Shop, Vendor tiles
  is_armory_tile: Boolean // True for Armory tiles
  associated_shop_id: String // Links tile to a specific ShopInventory instance for this map
  // ... other terrain properties (movement cost, bonuses)
}
```
*TDD Anchor: test_map_tile_correctly_identifies_shop_armory*
*TDD Anchor: test_map_tile_links_to_correct_shop_id*

### 2.4. Item Data Extension
```pseudocode
// Existing ItemData needs these fields
ItemData {
  item_id: String
  name: String
  buy_price: Integer // Price to buy from Armory/Shop. -1 if not buyable.
  sell_price: Integer // Price when selling to Shop. Calculated (e.g., buy_price / 2) or fixed. -1 if not sellable.
  is_sellable: Boolean // Flag to prevent selling unique/important items
  // ... other item properties (stats, uses, type, etc.)
}
```
*TDD Anchor: test_item_sell_price_calculation*
*TDD Anchor: test_item_cannot_be_sold_if_flagged*

## 3. Core Logic Modules

### 3.1. Shop Interaction Module
```pseudocode
Function can_unit_use_shop_on_tile(unit, tile): Boolean
  // TDD Anchor: test_can_use_shop_on_correct_tile_type
  // TDD Anchor: test_cannot_use_shop_on_wrong_tile_type
  // TDD Anchor: test_cannot_use_shop_if_unit_has_acted
  // TDD Anchor: test_secret_shop_needs_member_card_in_inventory
  IF unit has already acted THEN RETURN FALSE
  IF tile.is_shop_tile OR tile.is_armory_tile THEN
    IF tile.associated_shop_id is valid THEN
      shop_data = load_shop_inventory(tile.associated_shop_id)
      IF shop_data.type == "SecretShop" AND shop_data.requires_member_card THEN
        IF unit has "Member Card" item in inventory THEN
          RETURN TRUE
        ELSE
          RETURN FALSE
        ENDIF
      ELSE
        RETURN TRUE // Regular shop/armory
      ENDIF
    ELSE
      RETURN FALSE // Tile marked as shop but no inventory defined
    ENDIF
  ELSE
    RETURN FALSE // Not a shop/armory tile
  ENDIF
EndFunction

Procedure initiate_shop_interaction(unit, tile)
  // TDD Anchor: test_shop_interaction_consumes_action
  // TDD Anchor: test_shop_interaction_opens_correct_ui
  IF can_unit_use_shop_on_tile(unit, tile) THEN
    shop_data = load_shop_inventory(tile.associated_shop_id)
    mark_unit_as_acted(unit) // Interaction costs the action

    IF tile.is_armory_tile THEN
      // Armories typically only allow buying
      open_armory_ui(unit, shop_data, GameState.player_gold)
    ELSE IF tile.is_shop_tile THEN
      // Shops allow buying and selling
      open_shop_ui(unit, shop_data, GameState.player_gold)
    ENDIF
  ELSE
    // Play error sound or give feedback
    log_error("Cannot use shop/armory here.")
  ENDIF
EndProcedure
```

### 3.2. Purchasing Module
```pseudocode
Function can_purchase_item(unit, item_id, shop_data, player_gold): Boolean
  // TDD Anchor: test_can_purchase_with_enough_gold
  // TDD Anchor: test_cannot_purchase_without_enough_gold
  // TDD Anchor: test_can_purchase_with_inventory_space
  // TDD Anchor: test_cannot_purchase_with_full_inventory_no_convoy
  // TDD Anchor: test_can_purchase_with_full_inventory_with_convoy
  // TDD Anchor: test_cannot_purchase_item_out_of_stock
  item_entry = find_item_in_shop(item_id, shop_data)
  IF item_entry is null THEN RETURN FALSE // Item not sold here
  IF item_entry.stock == 0 THEN RETURN FALSE // Out of stock

  item_data = load_item_data(item_id)
  IF item_data.buy_price < 0 THEN RETURN FALSE // Item not buyable

  IF player_gold < item_data.buy_price THEN RETURN FALSE // Not enough gold

  IF unit.inventory.is_full() THEN
    IF GameState.convoy_is_available THEN // Assuming a convoy system exists
      RETURN TRUE // Can send to convoy
    ELSE
      RETURN FALSE // Inventory full, no convoy
    ENDIF
  ELSE
    RETURN TRUE // Has space in inventory
  ENDIF
EndFunction

Procedure execute_purchase(unit, item_id, shop_data)
  // TDD Anchor: test_purchase_deducts_correct_gold
  // TDD Anchor: test_purchase_adds_item_to_inventory
  // TDD Anchor: test_purchase_adds_item_to_convoy_if_inventory_full
  // TDD Anchor: test_purchase_decrements_stock_if_limited
  IF can_purchase_item(unit, item_id, shop_data, GameState.player_gold) THEN
    item_data = load_item_data(item_id)
    item_entry = find_item_in_shop(item_id, shop_data)

    // Deduct gold
    GameState.player_gold -= item_data.buy_price

    // Add item
    IF unit.inventory.is_full() AND GameState.convoy_is_available THEN
      add_item_to_convoy(item_id)
    ELSE
      add_item_to_unit_inventory(unit, item_id)
    ENDIF

    // Decrement stock if limited
    IF item_entry.stock > 0 THEN
      item_entry.stock -= 1
      update_shop_inventory(shop_data) // Persist stock change if needed
    ENDIF

    // Play success sound, update UI
  ELSE
    // Play error sound or give feedback
    log_error("Purchase failed.")
  ENDIF
EndProcedure
```

### 3.3. Selling Module (Shops Only)
```pseudocode
Function can_sell_item(unit, item_instance_id): Boolean
  // TDD Anchor: test_can_sell_sellable_item
  // TDD Anchor: test_cannot_sell_unsellable_item
  // TDD Anchor: test_cannot_sell_equipped_item // Optional rule, common in FE
  item = get_item_from_unit_inventory(unit, item_instance_id)
  IF item is null THEN RETURN FALSE

  item_data = load_item_data(item.item_id)
  IF NOT item_data.is_sellable THEN RETURN FALSE
  IF item_data.sell_price <= 0 THEN RETURN FALSE // Cannot sell if value is 0 or less

  // Optional: Prevent selling equipped item
  // IF unit.equipped_weapon_instance_id == item_instance_id THEN RETURN FALSE

  RETURN TRUE
EndFunction

Procedure execute_sell(unit, item_instance_id)
  // TDD Anchor: test_sell_adds_correct_gold
  // TDD Anchor: test_sell_removes_item_from_inventory
  IF can_sell_item(unit, item_instance_id) THEN
    item = get_item_from_unit_inventory(unit, item_instance_id)
    item_data = load_item_data(item.item_id)

    // Add gold
    GameState.player_gold += item_data.sell_price

    // Remove item
    remove_item_from_unit_inventory(unit, item_instance_id)

    // Play success sound, update UI
  ELSE
    // Play error sound or give feedback
    log_error("Sell failed.")
  ENDIF
EndProcedure
```

## 4. User Interface (UI)

### 4.1. Armory UI
*   Displays: Armory Name/Type, Player Gold.
*   List of buyable items: Icon, Name, Price, Stock (if limited).
*   Shows unit's current inventory for reference (optional).
*   Allows selecting an item to buy.
*   Shows confirmation prompt with item details and cost.
*   Provides feedback on success/failure (e.g., "Not enough gold", "Inventory full", "Purchase complete").
*   Exit option.

### 4.2. Shop UI
*   Displays: Shop Name/Type, Player Gold.
*   Two main modes/tabs: Buy / Sell.
*   **Buy Mode:** Same as Armory UI (list of items for sale).
*   **Sell Mode:**
    *   Displays unit's inventory: Icon, Name, Uses, Calculated Sell Price.
    *   Grays out or hides unsellable items.
    *   Allows selecting an item to sell.
    *   Shows confirmation prompt with item details and gold gain.
    *   Provides feedback on success/failure.
*   Exit option.

## 5. AI Considerations

*   AI units **do not** interact with Shops or Armories. This system is player-only.

## 6. Integration Points

*   **Map System:** Needs `TerrainData` with `is_shop_tile`, `is_armory_tile`, `associated_shop_id`. Needs function to get tile data at coordinates.
*   **Unit System:** Needs `Unit` object with `inventory` (list of item instances), `has_acted` flag, `position`. Needs functions `add_item_to_unit_inventory`, `remove_item_from_unit_inventory`, `get_item_from_unit_inventory`, `unit.inventory.is_full()`, `mark_unit_as_acted`. Needs check for "Member Card" item.
*   **Item System:** Needs `ItemData` with `buy_price`, `sell_price`, `is_sellable`. Needs `load_item_data(item_id)`.
*   **Game State:** Needs `GameState` with `player_gold`. Needs access to `GameState.convoy_is_available` and `add_item_to_convoy` if a convoy system exists.
*   **Action System:** Needs to register "Shop" / "Armory" as valid unit commands available on specific tiles. Needs to ensure using the shop consumes the action.
*   **Data Loading:** Needs functions `load_shop_inventory(shop_id)` and `update_shop_inventory(shop_data)` (if stock needs persistence). Shop inventories likely loaded from chapter data files.
*   **UI System:** Needs to implement the Armory and Shop UI screens described above.

## 7. Thracia 776 Specific Considerations

*   **Gold Scarcity:** Initial `player_gold` should be very low (possibly 0). Gold sources (selling valuable captured items, arena, events) should be limited.
*   **High Prices:** `buy_price` for items in `ItemData` should reflect Thracia's high costs.
*   **Sell Prices:** `sell_price` is typically `buy_price / 2`. Ensure `is_sellable` is FALSE for unique/important items (like Crusader Scrolls, personal weapons).
*   **Member Card:** Implement the `requires_member_card` check for Secret Shops. The Member Card itself is an item the player must find/obtain.
*   **Convoy:** Thracia's convoy system is less prominent than in other games. If implementing a convoy, decide how it's accessed (Leif only? Prep screen only?). If no convoy, purchasing with a full inventory is impossible. For simplicity, initially assume no convoy interaction unless specified elsewhere.

## 8. Open Questions / Future Considerations

*   Convoy integration details?
*   Persistence of limited stock? (Per chapter visit? Globally?) Thracia's economy makes unlimited stock + high prices more likely, but limited stock is possible.
*   Handling broken items in sell menu (sell value 0 or 1?).
*   Specific UI layout and flow details.