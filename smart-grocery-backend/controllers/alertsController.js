import InventoryItem from "../models/InventoryItem.js";
import { daysUntilExpiry } from "../utils/dateUtils.js";

export const getAlerts = async (req, res, next) => {
  try {
    const items = await InventoryItem.find({ user: req.user._id });
    const alerts = [];

    items.forEach((item) => {
      const daysLeft = daysUntilExpiry(item.expiryDate);

      if (daysLeft <= 3) {
        alerts.push({
          type: "Expiry Soon",
          severity: "high",
          message: `${item.name} expires in ${daysLeft} day(s).`,
          itemId: item._id,
        });
      }

      if (item.riskPrediction === "High Risk") {
        alerts.push({
          type: "High Risk",
          severity: "high",
          message: `${item.name} has high spoilage risk.`,
          itemId: item._id,
        });
      }

      if (item.quantity > 100 && item.consumptionRate < 5) {
        alerts.push({
          type: "Overstock",
          severity: "moderate",
          message: `${item.name} is overstocked with low consumption.`,
          itemId: item._id,
        });
      }
    });

    return res.status(200).json(alerts);
  } catch (error) {
    return next(error);
  }
};
