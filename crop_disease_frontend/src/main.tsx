// ... existing code ...
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./styles/index.css";
import { AuthProvider } from "./contexts/AuthContext.tsx";

createRoot(document.getElementById("root")!).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
