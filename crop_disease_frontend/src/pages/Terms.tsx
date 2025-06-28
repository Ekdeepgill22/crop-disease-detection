import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Terms() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Terms of Service</h1>
        <p className="text-muted-foreground mb-4">
          By using KhetAI, you agree to use the platform for lawful agricultural purposes only. You are responsible for the accuracy of the information you provide.
        </p>
        <p className="text-muted-foreground mb-4">
          KhetAI is not liable for any loss or damage resulting from the use of our services. We reserve the right to update these terms at any time.
        </p>
        <p className="text-muted-foreground">
          Continued use of the platform constitutes acceptance of the latest terms.
        </p>
      </div>
    </Layout>
  );
} 