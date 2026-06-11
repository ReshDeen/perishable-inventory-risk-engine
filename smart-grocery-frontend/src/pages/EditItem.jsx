// src/pages/EditItem.jsx
import React, { useEffect, useState } from "react";
import API from "../api/api";

export default function EditItem() {
  const [items, setItems] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    quantity: "",
    expiryDate: "",
    image: "",
  });

  // Fetch all grocery items
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

  // Handle input changes for edit form
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Start editing an item
  const startEditing = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      quantity: item.quantity,
      expiryDate: item.expiryDate.split("T")[0], // format date
      image: item.image || "",
    });
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingItem(null);
    setFormData({ name: "", quantity: "", expiryDate: "", image: "" });
  };

  // Submit edited item
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.put(`/groceries/${editingItem._id}`, formData);
      alert("Item updated successfully!");
      setItems(items.map((i) => (i._id === editingItem._id ? res.data : i)));
      cancelEdit();
    } catch (err) {
      console.error(err);
      alert("Failed to update item.");
    }
  };

  // Delete item
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;
    try {
      await API.delete(`/groceries/${id}`);
      setItems(items.filter((i) => i._id !== id));
      alert("Item deleted successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to delete item.");
    }
  };

  return (
    <div className="min-h-screen bg-green-50 p-8">
      <h1 className="text-3xl font-bold text-center mb-6 text-green-900">
        Edit Grocery Items
      </h1>

      {/* List of items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        {items.map((item) => (
          <div
            key={item._id}
            className="p-4 rounded-2xl shadow-lg bg-white border border-green-200 flex flex-col"
          >
            <h2 className="text-xl font-semibold text-green-900">{item.name}</h2>
            <p className="text-green-700">Quantity: {item.quantity}</p>
            <p className="text-green-700">
              Expiry: {new Date(item.expiryDate).toDateString()}
            </p>
            <div className="mt-2 flex space-x-2">
              <button
                className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                onClick={() => startEditing(item)}
              >
                Edit
              </button>
              <button
                className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                onClick={() => handleDelete(item._id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Edit form */}
      {editingItem && (
        <div className="max-w-lg mx-auto p-6 bg-white rounded-xl shadow-md">
          <h2 className="text-2xl font-bold mb-4 text-center text-green-900">
            Editing: {editingItem.name}
          </h2>

          <form onSubmit={handleEditSubmit} className="space-y-4">
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Item Name"
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <input
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              placeholder="Quantity"
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <input
              type="date"
              name="expiryDate"
              value={formData.expiryDate}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <input
              type="text"
              name="image"
              value={formData.image}
              onChange={handleChange}
              placeholder="Image URL (optional)"
              className="w-full p-2 border rounded"
            />

            <div className="flex justify-between">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
              >
                Save Changes
              </button>
              <button
                type="button"
                className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500 transition"
                onClick={cancelEdit}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
