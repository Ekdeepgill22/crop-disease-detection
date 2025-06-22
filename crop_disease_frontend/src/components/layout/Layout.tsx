import { ReactNode } from "react";
import { Navigation } from "./Navigation";

interface LayoutProps {
  children: ReactNode;
  isAuthenticated?: boolean;
}

export function Layout({ children, isAuthenticated = false }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Navigation isAuthenticated={isAuthenticated} />
      <main className="flex-1">{children}</main>
    </div>
  );
}
