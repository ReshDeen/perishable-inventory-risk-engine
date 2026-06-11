import PDFDocument from "pdfkit";
import { Parser } from "json2csv";
import InventoryItem from "../models/InventoryItem.js";
import { getSummary } from "./analyticsController.js";

export const exportInventoryCsv = async (req, res, next) => {
  try {
    const items = await InventoryItem.find({ user: req.user._id }).lean();
    const parser = new Parser({
      fields: [
        "name",
        "category",
        "quantity",
        "unit",
        "purchaseDate",
        "expiryDate",
        "pricePerUnit",
        "consumptionRate",
        "riskPrediction",
        "confidenceScore",
        "recommendedAction",
      ],
    });

    const csv = parser.parse(items);
    res.header("Content-Type", "text/csv");
    res.attachment("inventory-export.csv");
    return res.send(csv);
  } catch (error) {
    return next(error);
  }
};

export const exportAnalyticsPdf = async (req, res, next) => {
  try {
    const items = await InventoryItem.find({ user: req.user._id }).lean();

    const summary = {
      totalProducts: items.length,
      highRiskCount: items.filter((i) => i.riskPrediction === "High Risk").length,
      moderateRiskCount: items.filter((i) => i.riskPrediction === "Moderate Risk").length,
      safeCount: items.filter((i) => i.riskPrediction === "Safe").length,
    };

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "attachment; filename=analytics-report.pdf");

    const doc = new PDFDocument({ margin: 40 });
    doc.pipe(res);

    doc.fontSize(20).text("P.I.R.E. Analytics Report", { underline: true });
    doc.moveDown();
    doc.fontSize(12).text(`Generated: ${new Date().toLocaleString()}`);
    doc.moveDown();

    Object.entries(summary).forEach(([key, value]) => {
      doc.text(`${key}: ${value}`);
    });

    doc.moveDown();
    doc.text("Top Inventory Items:");
    items.slice(0, 20).forEach((item, index) => {
      doc.text(
        `${index + 1}. ${item.name} | Risk: ${item.riskPrediction} | Qty: ${item.quantity} | Exp: ${new Date(item.expiryDate).toLocaleDateString()}`
      );
    });

    doc.end();
  } catch (error) {
    return next(error);
  }
};
