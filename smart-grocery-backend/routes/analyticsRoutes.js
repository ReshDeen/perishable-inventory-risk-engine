import express from "express";
import {
  getMonthlyTrends,
  getRiskDistribution,
  getSummary,
} from "../controllers/analyticsController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.use(protect);
router.get("/summary", getSummary);
router.get("/risk-distribution", getRiskDistribution);
router.get("/monthly-trends", getMonthlyTrends);

export default router;
