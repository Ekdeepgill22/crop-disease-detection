import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function About() {
  const navigate = useNavigate();
  return (
    <Layout isAuthenticated={false}>
      <div className="container mx-auto px-4 py-16 max-w-2xl">
        <button onClick={() => navigate(-1)} className="flex items-center mb-6 text-emerald-600 hover:underline">
          <ArrowLeft className="mr-2 h-5 w-5" /> Back
        </button>
        <h1 className="text-3xl font-bold mb-4">About Us</h1>
        <p className="text-muted-foreground mb-4">
          <b>KhetAI</b> is dedicated to revolutionizing agriculture through artificial intelligence. Our mission is to empower farmers with instant crop disease detection, actionable treatment advice, and data-driven insights to maximize yield and sustainability.
        </p>
        <p className="text-muted-foreground mb-4">
          Our platform leverages state-of-the-art AI models and real-time weather data to provide accurate diagnoses and personalized recommendations. We believe in making advanced technology accessible to every farmer, everywhere.
        </p>
        <p className="text-muted-foreground">
          Join us on our journey to create a healthier, more productive, and sustainable future for agriculture.
        </p>
      </div>
    </Layout>
  );
} 