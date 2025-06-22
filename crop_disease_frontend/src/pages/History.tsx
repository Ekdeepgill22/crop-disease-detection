import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { History as HistoryIcon, Calendar, Leaf } from "lucide-react";

export default function History() {
  return (
    <Layout isAuthenticated={true}>
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold">Diagnosis History</h1>
            <p className="text-muted-foreground">
              View your past crop analyses and treatment progress
            </p>
          </div>

          {/* Sample History Items */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Leaf className="h-5 w-5 text-emerald-600" />
                    Tomato Plant Analysis
                  </CardTitle>
                  <Badge className="bg-red-100 text-red-800">
                    High Severity
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />2 days ago
                  </div>
                  <div>Disease: Late Blight</div>
                  <div>Confidence: 94%</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Leaf className="h-5 w-5 text-emerald-600" />
                    Wheat Crop Analysis
                  </CardTitle>
                  <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />1 week ago
                  </div>
                  <div>No diseases detected</div>
                  <div>Confidence: 99%</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Placeholder */}
          <div className="text-center py-16">
            <HistoryIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-4">
              Full History Coming Soon
            </h2>
            <p className="text-muted-foreground">
              This is a placeholder page. Complete history functionality will be
              implemented in the next iteration.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
