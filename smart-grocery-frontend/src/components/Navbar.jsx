import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-indigo-600 text-white p-4 flex justify-around">
      <Link to="/">Home</Link>
      <Link to="/add-item">Add Item</Link>
      <Link to="/expiry-alerts">Expiry Alerts</Link>
    </nav>
  );
}
