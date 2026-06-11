import express from "express";
import { exportAnalyticsPdf, exportInventoryCsv } from "../controllers/exportController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/inventory/csv", protect, exportInventoryCsv);
router.get("/analytics/pdf", protect, exportAnalyticsPdf);

export default router;
