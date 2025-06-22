import { useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { History as HistoryIcon, Calendar, Leaf, Loader2 } from "lucide-react";
import api from "@/lib/api";

async function fetchHistory() {
  const { data } = await api.get("/disease/history");
  return data;
}

export default function History() {
  const { data: history, isLoading, isError } = useQuery({
    queryKey: ["history"],
    queryFn: fetchHistory,
  });

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

          {isLoading && (
            <div className="flex justify-center items-center py-16">
              <Loader2 className="h-16 w-16 animate-spin text-muted-foreground" />
            </div>
          )}

          {isError && (
            <div className="text-center py-16">
              <HistoryIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4 text-red-500">
                Error Fetching History
              </h2>
              <p className="text-muted-foreground">
                We couldn't load your diagnosis history. Please try again later.
              </p>
            </div>
          )}

          {!isLoading && !isError && history && (
            <div className="space-y-4">
              {history.map((item: any) => (
                <Card key={item.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Leaf className="h-5 w-5 text-emerald-600" />
                        {item.plant_name} Analysis
                      </CardTitle>
                      <Badge
                        className={
                          item.is_healthy
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }
                      >
                        {item.is_healthy ? "Healthy" : "Disease Detected"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(item.diagnosed_at).toLocaleDateString()}
                      </div>
                      <div>Disease: {item.disease_name}</div>
                      <div>Confidence: {item.confidence.toFixed(2)}%</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          
          {!isLoading && !isError && history?.length === 0 && (
            <div className="text-center py-16">
              <HistoryIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4">
                No History Found
              </h2>
              <p className="text-muted-foreground">
                You haven't performed any diagnoses yet. Get started on the Dashboard!
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
