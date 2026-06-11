import mongoose from "mongoose";

const GroceryItemSchema = new mongoose.Schema(
  {
    name: { type: String, required: true },
    quantity: { type: Number, required: true },
    expiryDate: { type: Date, required: true },
    image: { type: String, default: "" }, // <-- add this line
  },
  { timestamps: true }
);

export default mongoose.model("GroceryItem", GroceryItemSchema);
