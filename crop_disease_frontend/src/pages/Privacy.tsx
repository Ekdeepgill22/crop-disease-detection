import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function Privacy() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">Privacy Policy</h1>
        <p className="text-muted-foreground mb-4">
          We value your privacy. KhetAI collects only the data necessary to provide our services, such as account information and crop images for disease analysis. We do not sell your data to third parties.
        </p>
        <p className="text-muted-foreground mb-4">
          All data is encrypted and securely stored. You can request deletion of your data at any time by contacting our support team.
        </p>
        <p className="text-muted-foreground">
          For more details, please contact us at <a href="mailto:support@khetai.com" className="text-emerald-600 underline">support@khetai.com</a>.
        </p>
      </div>
    </Layout>
  );
} 