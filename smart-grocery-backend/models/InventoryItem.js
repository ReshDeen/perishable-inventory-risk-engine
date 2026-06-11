import mongoose from "mongoose";

const inventoryItemSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    name: { type: String, required: true, trim: true },
    category: { type: String, required: true, trim: true },
    quantity: { type: Number, required: true, min: 0 },
    unit: { type: String, default: "kg", trim: true },
    purchaseDate: { type: Date, required: true },
    expiryDate: { type: Date, required: true },
    pricePerUnit: { type: Number, required: true, min: 0 },
    consumptionRate: { type: Number, required: true, min: 0 },
    riskPrediction: {
      type: String,
      enum: ["High Risk", "Moderate Risk", "Safe"],
      default: "Safe",
    },
    confidenceScore: { type: Number, default: 0 },
    recommendedAction: { type: String, default: "Monitor" },
  },
  { timestamps: true }
);

inventoryItemSchema.index({ user: 1, expiryDate: 1 });
inventoryItemSchema.index({ user: 1, category: 1 });

export default mongoose.model("InventoryItem", inventoryItemSchema);
