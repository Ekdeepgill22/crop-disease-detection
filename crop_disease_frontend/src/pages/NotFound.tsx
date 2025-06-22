import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Leaf, Home } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-forest-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-hero-pattern opacity-30"></div>

      <div className="relative text-center space-y-6 max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-600">
            <Leaf className="h-7 w-7 text-white" />
          </div>
          <span className="text-2xl font-bold">KhetAI</span>
        </div>

        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-emerald-600">404</h1>
          <h2 className="text-2xl font-semibold text-gray-800">
            Crop not found!
          </h2>
          <p className="text-gray-600">
            The page you're looking for seems to have been harvested or moved to
            a different field.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link to="/">
            <Button className="w-full sm:w-auto">
              <Home className="mr-2 h-4 w-4" />
              Return to Farm
            </Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="outline" className="w-full sm:w-auto">
              Go to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
