import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Contact() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Contact Us</h1>
        <p className="text-muted-foreground mb-4">
          Have questions or feedback? Reach out to us and we'll get back to you as soon as possible.
        </p>
        <p className="text-muted-foreground">
          Email: <a href="mailto:support@khetai.com" className="text-emerald-600 underline">support@khetai.com</a>
        </p>
      </div>
    </Layout>
  );
} 