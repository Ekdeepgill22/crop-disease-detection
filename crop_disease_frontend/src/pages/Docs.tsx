import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Docs() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Documentation</h1>
        <p className="text-muted-foreground mb-4">
          Find detailed guides and API documentation to help you get the most out of KhetAI.
        </p>
        <p className="text-muted-foreground">
          More documentation will be added soon.
        </p>
      </div>
    </Layout>
  );
} 