import { useAuth } from "@/contexts/AuthContext";
import { Layout } from "@/components/layout/Layout";
import { UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Profile() {
  const { user } = useAuth();

  return (
    <Layout isAuthenticated={true}>
      <div
        className="min-h-screen relative"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), url('https://images.pexels.com/photos/1595104/pexels-photo-1595104.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
        }}
      >
        <div className="container mx-auto px-4 py-8 flex justify-center items-center min-h-[70vh]">
          <div className="max-w-lg w-full bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg p-8">
            <div className="flex flex-col items-center mb-6">
              <UserCircle className="h-16 w-16 text-emerald-600 mb-2" />
              <h1 className="text-3xl font-bold">Profile</h1>
            </div>
            <hr className="mb-6 border-emerald-100" />
            {user ? (
              <div className="space-y-6">
                <div className="flex flex-col md:flex-row md:items-center md:gap-4">
                  <span className="font-semibold text-muted-foreground w-32">Name:</span>
                  <span className="text-lg">{user.name}</span>
                </div>
                <div className="flex flex-col md:flex-row md:items-center md:gap-4">
                  <span className="font-semibold text-muted-foreground w-32">Email:</span>
                  <span className="text-lg">{user.email}</span>
                </div>
                <div className="flex flex-col md:flex-row md:items-center md:gap-4">
                  <span className="font-semibold text-muted-foreground w-32">Phone Number:</span>
                  <span className="text-lg">{user.phone_number}</span>
                </div>
                <div className="flex flex-col md:flex-row md:items-center md:gap-4">
                  <span className="font-semibold text-muted-foreground w-32">Region:</span>
                  <span className="text-lg">{user.region}</span>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground text-center">No user information available.</div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
} 