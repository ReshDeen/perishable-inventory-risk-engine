import InventoryItem from "../models/InventoryItem.js";
import { daysUntilExpiry } from "../utils/dateUtils.js";

export const getSummary = async (req, res, next) => {
  try {
    const items = await InventoryItem.find({ user: req.user._id });

    const summary = {
      totalProducts: items.length,
      highRiskCount: 0,
      moderateRiskCount: 0,
      safeCount: 0,
      expiringSoonCount: 0,
      estimatedWasteValue: 0,
    };

    items.forEach((item) => {
      const risk = item.riskPrediction || "Safe";
      if (risk === "High Risk") summary.highRiskCount += 1;
      if (risk === "Moderate Risk") summary.moderateRiskCount += 1;
      if (risk === "Safe") summary.safeCount += 1;

      const daysLeft = daysUntilExpiry(item.expiryDate);
      if (daysLeft <= 3) summary.expiringSoonCount += 1;

      if (risk === "High Risk" || daysLeft <= 3) {
        summary.estimatedWasteValue += item.quantity * item.pricePerUnit;
      }
    });

    summary.estimatedWasteValue = Number(summary.estimatedWasteValue.toFixed(2));

    return res.status(200).json(summary);
  } catch (error) {
    return next(error);
  }
};

export const getRiskDistribution = async (req, res, next) => {
  try {
    const grouped = await InventoryItem.aggregate([
      { $match: { user: req.user._id } },
      { $group: { _id: "$riskPrediction", value: { $sum: 1 } } },
    ]);

    const normalized = ["High Risk", "Moderate Risk", "Safe"].map((label) => ({
      risk: label,
      value: grouped.find((item) => item._id === label)?.value || 0,
    }));

    return res.status(200).json(normalized);
  } catch (error) {
    return next(error);
  }
};

export const getMonthlyTrends = async (req, res, next) => {
  try {
    const trends = await InventoryItem.aggregate([
      { $match: { user: req.user._id } },
      {
        $group: {
          _id: {
            year: { $year: "$createdAt" },
            month: { $month: "$createdAt" },
          },
          addedItems: { $sum: 1 },
          highRisk: {
            $sum: {
              $cond: [{ $eq: ["$riskPrediction", "High Risk"] }, 1, 0],
            },
          },
        },
      },
      { $sort: { "_id.year": 1, "_id.month": 1 } },
    ]);

    const formatted = trends.map((row) => ({
      month: `${row._id.year}-${String(row._id.month).padStart(2, "0")}`,
      addedItems: row.addedItems,
      highRisk: row.highRisk,
    }));

    return res.status(200).json(formatted);
  } catch (error) {
    return next(error);
  }
};
