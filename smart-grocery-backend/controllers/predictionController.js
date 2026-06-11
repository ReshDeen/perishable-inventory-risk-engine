import InventoryItem from "../models/InventoryItem.js";
import Prediction from "../models/Prediction.js";
import { runPythonPrediction } from "../utils/runPythonPrediction.js";

export const predictRisk = async (req, res, next) => {
  try {
    const payload = req.body;
    const prediction = await runPythonPrediction(payload);

    const savedPrediction = await Prediction.create({
      user: req.user._id,
      inventoryItem: payload.inventoryItemId || undefined,
      inputPayload: payload,
      ...prediction,
    });

    if (payload.inventoryItemId) {
      await InventoryItem.findOneAndUpdate(
        { _id: payload.inventoryItemId, user: req.user._id },
        {
          riskPrediction: prediction.riskPrediction,
          confidenceScore: prediction.confidenceScore,
          recommendedAction: prediction.recommendedAction,
        }
      );
    }

    return res.status(200).json({ ...prediction, predictionId: savedPrediction._id });
  } catch (error) {
    return next(error);
  }
};
