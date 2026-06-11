import express from "express";
import { body } from "express-validator";
import { predictRisk } from "../controllers/predictionController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validateRequest } from "../middleware/validateRequest.js";

const router = express.Router();

router.post(
  "/",
  protect,
  [
    body("quantity").isFloat({ min: 0 }),
    body("consumptionRate").isFloat({ min: 0 }),
    body("daysToExpiry").isInt({ min: 0 }),
    body("pricePerUnit").isFloat({ min: 0 }),
  ],
  validateRequest,
  predictRisk
);

export default router;
