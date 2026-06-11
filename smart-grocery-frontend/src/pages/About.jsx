// src/pages/About.jsx
import React from "react";
import aboutImg from "../assets/about.jpeg";

export default function About() {
  return (
    <div className="min-h-screen bg-green-50 p-8 flex flex-col items-center">
      <img src={aboutImg} alt="About" className="w-64 h-64 object-cover rounded-lg mb-6" />
      <h1 className="text-3xl font-bold text-green-900 mb-4">About Reshma Banu</h1>
      <p className="text-green-700 max-w-2xl text-center">
        Hello! I am <span className="font-semibold">Reshma Banu</span>, a passionate developer. This project, <span className="font-semibold">P.I.R.E. (Perishable Inventory Risk Engine)</span>, is built to manage groceries, track expiry dates, and predict spoilage risk for smarter inventory decisions.
      </p>
    </div>
  );
}
