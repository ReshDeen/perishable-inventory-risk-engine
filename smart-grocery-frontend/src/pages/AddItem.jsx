import { useState } from "react";
import API from "../api/api";

export default function AddItem() {
  const [item, setItem] = useState({
    name: "",
    quantity: "",
    expiryDate: "",
    cost: "",
    image: "",
  });

  const handleChange = (e) => {
    setItem({ ...item, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await API.post("/groceries", item); // POST request
      alert("Item Added Successfully!");
      console.log(res.data);

      // Clear form
      setItem({
        name: "",
        quantity: "",
        expiryDate: "",
        cost: "",
        image: "",
      });
    } catch (err) {
      console.error(err);
      alert("Failed to add item. Check console.");
    }
  };

  return (
    <div className="min-h-screen bg-green-50 flex justify-center items-start py-12 px-4">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-green-900 text-center mb-6">
          Add Grocery Item
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            name="name"
            value={item.name}
            onChange={handleChange}
            placeholder="Item Name"
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />

          <input
            type="number"
            name="quantity"
            value={item.quantity}
            onChange={handleChange}
            placeholder="Quantity"
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />

          <input
            type="number"
            name="cost"
            value={item.cost}
            onChange={handleChange}
            placeholder="Cost (optional)"
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
          />

          <input
            type="date"
            name="expiryDate"
            value={item.expiryDate}
            onChange={handleChange}
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />

          <input
            type="text"
            name="image"
            value={item.image}
            onChange={handleChange}
            placeholder="Image URL (optional)"
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
          />

          <button
            type="submit"
            className="w-full bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition font-semibold"
          >
            Add Item
          </button>
        </form>
      </div>
    </div>
  );
}
