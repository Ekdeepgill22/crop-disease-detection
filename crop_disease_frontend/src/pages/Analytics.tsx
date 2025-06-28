import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Analytics() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={true}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Analytics</h1>
        <p className="text-muted-foreground mb-4">
          View your crop health trends, diagnosis history, and actionable insights to improve your yield.
        </p>
        <p className="text-muted-foreground">
          Analytics dashboard coming soon.
        </p>
      </div>
    </Layout>
  );
} 