import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import InventoryForm from "../components/InventoryForm";
import Loader from "../components/ui/Loader";
import api from "../services/api";
import { useToast } from "../context/ToastContext";

export default function EditInventory() {
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { id } = useParams();
  const toast = useToast();

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get(`/inventory/${id}`);
        setItem(response.data);
      } catch (error) {
        toast?.pushToast("Could not load item.", "error");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [id]);

  const submit = async (payload) => {
    try {
      await api.put(`/inventory/${id}`, payload);
      toast?.pushToast("Inventory item updated.");
      navigate("/app/inventory");
    } catch (error) {
      toast?.pushToast(error.response?.data?.message || "Update failed.", "error");
    }
  };

  if (loading) return <Loader label="Loading item..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Edit Inventory</h1>
        <p className="text-sm text-slate-400">Update item details and refresh risk calculation if needed.</p>
      </div>
      <InventoryForm initialValue={item} onSubmit={submit} submitLabel="Save Changes" />
    </div>
  );
}
