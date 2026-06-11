import express from "express";
import GroceryItem from "../models/GroceryItem.js";

const router = express.Router();

// Add item
router.post("/", async (req, res) => {
  try {
    const item = new GroceryItem(req.body);
    await item.save();
    res.status(201).json(item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get all items
router.get("/", async (req, res) => {
  try {
    const items = await GroceryItem.find();
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete an item by ID
router.delete("/:id", async (req, res) => {
  try {
    const deletedItem = await GroceryItem.findByIdAndDelete(req.params.id);
    if (!deletedItem) {
      return res.status(404).json({ message: "Item not found" });
    }
    res.json({ message: "Item deleted successfully" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


export default router;
