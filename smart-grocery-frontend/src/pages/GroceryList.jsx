// src/pages/GroceryList.jsx
import { useEffect, useState } from "react";
import API from "../api/api";
import React from "react";
import milkImg from "../assets/milk.jpeg";
import breadImg from "../assets/bread.jpeg";

export default function GroceryList() {
  const [items, setItems] = useState([]);

  
  useEffect(() => {
    const fetchItems = async () => {
      try {
        const res = await API.get("/groceries");
        setItems(res.data);
      } catch (err) {
        console.error(err);
      }
    };


    fetchItems();
  }, []);

  // Helper function to check if item is expired
  const isExpired = (expiryDate) => {
    const today = new Date();
    const expiry = new Date(expiryDate);
    return expiry < today;
  };

  // Return image based on name
  const getImage = (name) => {
    if (name.toLowerCase() === "milk") return milkImg;
    if (name.toLowerCase() === "bread") return breadImg;
    return ""; // default no image
  };

  return (
    

    <div className="min-h-screen bg-green-50 p-8">
      <h1 className="text-3xl font-bold mb-6 text-center text-green-900">
        Grocery Items
      </h1>

      {items.length === 0 ? (
        <p className="text-center text-green-700 text-lg">No items added yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {items.map((item) => (
            <div
              key={item._id}
              className={`p-4 rounded-2xl shadow-lg bg-white border ${
                isExpired(item.expiryDate)
                  ? "border-red-400 bg-red-50"
                  : "border-green-200"
              }`}
            >
              {item.image || getImage(item.name) ? (
                <img
                  src={item.image || getImage(item.name)}
                  alt={item.name}
                  className="w-full h-32 object-cover rounded-lg mb-3"
                />
              ) : null}

              <h2 className="text-xl font-semibold text-green-900">{item.name}</h2>
              <p className="text-green-700">Quantity: {item.quantity}</p>
              <p className="text-green-700">
                Expiry: {new Date(item.expiryDate).toDateString()}
              </p>
              {isExpired(item.expiryDate) && (
                <p className="text-red-600 font-bold mt-1">❗ Expired!</p>
              )}

              {isExpired(item.expiryDate) && (
  <p className="text-red-600 font-bold mt-1">❗ Expired!</p>
)}

{/* DELETE BUTTON */}
<button
  className="mt-2 bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
  onClick={async () => {
    if (window.confirm("Are you sure you want to delete this item?")) {
      try {
        await API.delete(`/groceries/${item._id}`);
        setItems(items.filter((i) => i._id !== item._id)); // Remove item from state
        alert("Item deleted!");
      } catch (err) {
        console.error(err);
        alert("Failed to delete item.");
      }
    }
  }}
>
  Delete
</button>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}
