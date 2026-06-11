import { useState } from "react";

export default function AddItem() {
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const item = { name, quantity, expiryDate };

    try {
      const res = await fetch("http://localhost:5000/api/groceries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });

      if (res.ok) {
        setMessage("Item added successfully! ✔");
        setName("");
        setQuantity("");
        setExpiryDate("");
      } else {
        setMessage("Failed to add item ✘");
      }
    } catch (err) {
      setMessage("Error connecting to backend");
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Add Grocery Item</h2>

      {message && (
        <p className="mb-4 text-green-600 font-medium">{message}</p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">

        <input
          type="text"
          placeholder="Item Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <input
          type="number"
          placeholder="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <input
          type="date"
          value={expiryDate}
          onChange={(e) => setExpiryDate(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <button className="w-full py-2 bg-indigo-600 text-white rounded">
          Add Item
        </button>
      </form>
    </div>
  );
}
                                                                            