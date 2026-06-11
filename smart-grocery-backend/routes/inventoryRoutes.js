import express from "express";
import { body, param } from "express-validator";
import {
  createInventoryItem,
  deleteInventoryItem,
  getInventory,
  getInventoryItemById,
  updateInventoryItem,
} from "../controllers/inventoryController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validateRequest } from "../middleware/validateRequest.js";

const router = express.Router();

const inventoryValidation = [
  body("name").notEmpty(),
  body("category").notEmpty(),
  body("quantity").isFloat({ min: 0 }),
  body("purchaseDate").isISO8601(),
  body("expiryDate").isISO8601(),
  body("pricePerUnit").isFloat({ min: 0 }),
  body("consumptionRate").isFloat({ min: 0 }),
];

router.use(protect);

router.get("/", getInventory);
router.post("/", inventoryValidation, validateRequest, createInventoryItem);
router.get("/:id", [param("id").isMongoId()], validateRequest, getInventoryItemById);
router.put("/:id", [param("id").isMongoId(), ...inventoryValidation], validateRequest, updateInventoryItem);
router.delete("/:id", [param("id").isMongoId()], validateRequest, deleteInventoryItem);

export default router;
