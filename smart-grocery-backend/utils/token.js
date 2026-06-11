import jwt from "jsonwebtoken";

const jwtSecret = process.env.JWT_SECRET || "pire_dev_secret_change_me";

export const generateToken = (userId) =>
  jwt.sign({ userId }, jwtSecret, { expiresIn: process.env.JWT_EXPIRES_IN || "7d" });
