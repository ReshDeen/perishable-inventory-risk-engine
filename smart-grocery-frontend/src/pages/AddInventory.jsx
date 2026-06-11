import { useNavigate } from "react-router-dom";
import InventoryForm from "../components/InventoryForm";
import api from "../services/api";
import { useToast } from "../context/ToastContext";

export default function AddInventory() {
  const navigate = useNavigate();
  const toast = useToast();

  const submit = async (payload) => {
    try {
      const response = await api.post("/inventory", payload);
      toast?.pushToast("Inventory item created.");
      navigate(`/app/prediction`, { state: { item: response.data, created: true } });
    } catch (error) {
      toast?.pushToast(error.response?.data?.message || "Could not create item.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Add Inventory</h1>
        <p className="text-sm text-slate-400">Register a new perishable product with quantity and expiry details.</p>
      </div>
      <InventoryForm onSubmit={submit} submitLabel="Create Inventory Item" />
    </div>
  );
}
