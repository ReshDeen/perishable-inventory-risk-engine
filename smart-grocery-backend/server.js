import express from "express";
import cors from "cors";
import mongoose from "mongoose";
import dotenv from "dotenv";
import authRoutes from "./routes/authRoutes.js";
import inventoryRoutes from "./routes/inventoryRoutes.js";
import predictionRoutes from "./routes/predictionRoutes.js";
import analyticsRoutes from "./routes/analyticsRoutes.js";
import alertsRoutes from "./routes/alertsRoutes.js";
import exportRoutes from "./routes/exportRoutes.js";
import { errorHandler, notFound } from "./middleware/errorMiddleware.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

const allowedOrigins = (process.env.FRONTEND_URLS || process.env.FRONTEND_URL || "http://localhost:5173")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

app.use(
  cors({
    origin: (origin, callback) => {
      // Allow same-origin or non-browser requests (no Origin header)
      if (!origin) return callback(null, true);

      const isAllowed =
        allowedOrigins.includes(origin) || /^http:\/\/localhost:\d+$/.test(origin);

      if (isAllowed) return callback(null, true);
      return callback(new Error(`CORS blocked for origin: ${origin}`));
    },
    methods: "GET,POST,PUT,DELETE",
    credentials: true,
  })
);
app.use(express.json());

app.get("/", (req, res) => {
  res.send("P.I.R.E. Backend is running");
});

app.use("/api/auth", authRoutes);
app.use("/api/inventory", inventoryRoutes);
app.use("/api/predict", predictionRoutes);
app.use("/api/analytics", analyticsRoutes);
app.use("/api/alerts", alertsRoutes);
app.use("/api/export", exportRoutes);

app.use(notFound);
app.use(errorHandler);

mongoose
  .connect(process.env.MONGO_URI, { dbName: process.env.DB_NAME || "pire" })
  .then(() => {
    console.log("MongoDB connected");
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
  })
  .catch((err) => {
    console.log("Mongo error:", err.message);
    process.exit(1);
  });
