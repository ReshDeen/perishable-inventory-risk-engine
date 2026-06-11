import InventoryItem from "../models/InventoryItem.js";

export const getInventory = async (req, res, next) => {
  try {
    const { search, category, risk } = req.query;
    const query = { user: req.user._id };

    if (search) {
      query.name = { $regex: search, $options: "i" };
    }
    if (category) {
      query.category = category;
    }
    if (risk) {
      query.riskPrediction = risk;
    }

    const items = await InventoryItem.find(query).sort({ expiryDate: 1 });
    return res.status(200).json(items);
  } catch (error) {
    return next(error);
  }
};

export const createInventoryItem = async (req, res, next) => {
  try {
    const item = await InventoryItem.create({ ...req.body, user: req.user._id });
    return res.status(201).json(item);
  } catch (error) {
    return next(error);
  }
};

export const getInventoryItemById = async (req, res, next) => {
  try {
    const item = await InventoryItem.findOne({ _id: req.params.id, user: req.user._id });
    if (!item) {
      return res.status(404).json({ message: "Inventory item not found" });
    }
    return res.status(200).json(item);
  } catch (error) {
    return next(error);
  }
};

export const updateInventoryItem = async (req, res, next) => {
  try {
    const item = await InventoryItem.findOneAndUpdate(
      { _id: req.params.id, user: req.user._id },
      req.body,
      { new: true, runValidators: true }
    );

    if (!item) {
      return res.status(404).json({ message: "Inventory item not found" });
    }

    return res.status(200).json(item);
  } catch (error) {
    return next(error);
  }
};

export const deleteInventoryItem = async (req, res, next) => {
  try {
    const item = await InventoryItem.findOneAndDelete({ _id: req.params.id, user: req.user._id });

    if (!item) {
      return res.status(404).json({ message: "Inventory item not found" });
    }

    return res.status(200).json({ message: "Inventory item deleted successfully" });
  } catch (error) {
    return next(error);
  }
};
