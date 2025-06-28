import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Careers() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Careers</h1>
        <p className="text-muted-foreground mb-4">
          Want to join a passionate team building the future of agriculture? We're always looking for talented engineers, data scientists, and agricultural experts.
        </p>
        <p className="text-muted-foreground mb-4">
          Email your resume to <a href="mailto:careers@khetai.com" className="text-emerald-600 underline">careers@khetai.com</a> and tell us why you want to work at KhetAI!
        </p>
        <p className="text-muted-foreground">
          Open positions will be posted here soon.
        </p>
      </div>
    </Layout>
  );
} 