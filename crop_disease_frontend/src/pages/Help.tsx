import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Help() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Help Center</h1>
        <p className="text-muted-foreground mb-4">
          Need assistance? Browse our documentation or contact our support team for help with your account, diagnosis, or using KhetAI features.
        </p>
        <p className="text-muted-foreground">
          Email: <a href="mailto:support@khetai.com" className="text-emerald-600 underline">support@khetai.com</a>
        </p>
      </div>
    </Layout>
  );
} 