import express from "express";
import { body } from "express-validator";
import { getMe, login, register } from "../controllers/authController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validateRequest } from "../middleware/validateRequest.js";

const router = express.Router();

router.post(
  "/register",
  [body("name").notEmpty(), body("email").isEmail(), body("password").isLength({ min: 6 })],
  validateRequest,
  register
);

router.post("/login", [body("email").isEmail(), body("password").notEmpty()], validateRequest, login);
router.get("/me", protect, getMe);

export default router;
