import mongoose from "mongoose";

const predictionSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    inventoryItem: { type: mongoose.Schema.Types.ObjectId, ref: "InventoryItem" },
    inputPayload: { type: Object, required: true },
    riskPrediction: {
      type: String,
      enum: ["High Risk", "Moderate Risk", "Safe"],
      required: true,
    },
    confidenceScore: { type: Number, required: true },
    recommendedAction: { type: String, required: true },
  },
  { timestamps: true }
);

export default mongoose.model("Prediction", predictionSchema);
