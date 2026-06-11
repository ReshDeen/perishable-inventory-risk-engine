import express from "express";
import { getAlerts } from "../controllers/alertsController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/", protect, getAlerts);

export default router;
