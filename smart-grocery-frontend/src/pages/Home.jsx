// src/pages/Home.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import homeImage from "../assets/home.jpeg";
import groceryImage from "../assets/grocery.jpeg";
import addItemImage from "../assets/add.jpeg";
import editItemImage from "../assets/edit.jpeg";
import aboutImage from "../assets/about.jpeg";

export default function Home() {
  const navigate = useNavigate();

  const sections = [
    {
      title: "Home",
      description: "Return to this landing page",
      img: homeImage,
      action: () => navigate("/"),
    },
    {
      title: "Grocery List",
      description: "View all grocery items and their expiry status",
      img: groceryImage,
      action: () => navigate("/grocery-list"),
    },
    {
      title: "Add Item",
      description: "Add a new grocery item with quantity, cost, expiry and image",
      img: addItemImage,
      action: () => navigate("/add-item"),
    },
    {
      title: "Edit Item",
      description: "Edit or delete existing grocery items",
      img: editItemImage,
      action: () => navigate("/edit-item"),
    },
    {
      title: "About Us",
      description: "Know more about Reshma Banu & this project",
      img: aboutImage,
      action: () => navigate("/about"),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-100 to-green-300">
      {/* Hero Section */}
      <div className="text-center py-16 px-4">
        <h1 className="text-4xl font-bold mb-4">Welcome!</h1>
        <p className="text-xl mb-6">
          Created by <span className="font-semibold">Reshma Banu</span> — where creativity meets development
        </p>
        <p className="text-green-900 text-lg max-w-xl mx-auto">
          Manage your groceries, track expiry dates, add costs, and simplify your shopping experience.
        </p>
      </div>

      {/* Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-8 pb-16">
        {sections.map((section) => (
          <div
            key={section.title}
            onClick={section.action}
            className="cursor-pointer bg-white rounded-xl shadow-lg p-6 flex flex-col items-center text-center hover:scale-105 hover:shadow-2xl transition-transform duration-300"
          >
            <img src={section.img} alt={section.title} className="w-24 h-24 mb-4 object-contain" />
            <h2 className="text-2xl font-semibold mb-2">{section.title}</h2>
            <p className="text-green-900 text-sm">{section.description}</p>
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer className="bg-green-800 text-green-50 py-6 text-center">
        <p>© 2025 Reshma Banu | Smart Grocery & Expiry Tracker</p>
        <p>Where creativity meets development</p>
      </footer>
    </div>
  );
}
