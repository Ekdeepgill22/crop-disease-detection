import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Advisory from "./pages/Advisory";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Profile from "./pages/Profile";

const queryClient = new QueryClient();

function AuthRedirect() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" /> : <Outlet />;
}

const routes = [
  {
    path: "/",
    element: <Landing />
  },
  {
    path: "/login",
    element: <AuthRedirect />,
    children: [
      {
        index: true,
        element: <Login />
      },
      {
        path: "register",
        element: <Register />
      }
    ]
  },
  {
    path: "/register",
    element: <AuthRedirect />,
    children: [
      {
        index: true,
        element: <Register />
      }
    ]
  },
  {
    path: "/dashboard",
    element: <ProtectedRoute />,
    children: [
      {
        index: true,
        element: <Dashboard />
      }
    ]
  },
  {
    path: "/history",
    element: <ProtectedRoute />,
    children: [
      {
        index: true,
        element: <History />
      }
    ]
  },
  {
    path: "/advisory",
    element: <ProtectedRoute />,
    children: [
      {
        index: true,
        element: <Advisory />
      }
    ]
  },
  {
    path: "/profile",
    element: <ProtectedRoute />,
    children: [
      {
        index: true,
        element: <Profile />
      }
    ]
  },
  {
    path: "*",
    element: <NotFound />
  }
];

const router = createBrowserRouter(routes);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <RouterProvider router={router} />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
