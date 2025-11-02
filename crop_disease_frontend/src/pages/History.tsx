import { useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { History as HistoryIcon, Calendar, Leaf, Loader2, Eye, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";

async function fetchHistory() {
  const { data } = await api.get("/disease/history");
  return data;
}

async function deleteDiagnosis(id: string) {
  await api.delete(`/disease/diagnosis/${id}`);
}

export default function History() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { data: history, isLoading, isError, refetch } = useQuery({
    queryKey: ["history"],
    queryFn: fetchHistory,
  });

  const getSeverityColor = (confidence: number) => {
    if (confidence > 0.8) return "bg-red-100 text-red-800";
    if (confidence > 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-green-100 text-green-800";
  };

  const getSeverityText = (confidence: number) => {
    if (confidence > 0.8) return "High Risk";
    if (confidence > 0.6) return "Medium Risk";
    return "Low Risk";
  };

  return (
    <Layout isAuthenticated={true}>
      <div 
        className="min-h-screen relative"
        style={{
          backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('https://images.pexels.com/photos/1595104/pexels-photo-1595104.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed'
        }}
      >
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
                <Loader2 className="h-16 w-16 animate-spin text-emerald-600" />
              </div>
            )}

            {isError && (
              <div className="text-center py-16">
                <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-4 text-red-500">
                  Error Fetching History
                </h2>
                <p className="text-muted-foreground">
                  We couldn't load your diagnosis history. Please try again later.
                </p>
              </div>
            )}

            {!isLoading && !isError && history && history.length > 0 && (
              <div className="space-y-4">
                {history.map((item: any) => (
                  <Card key={item._id} className="bg-white/90 backdrop-blur-sm hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <Leaf className="h-5 w-5 text-emerald-600" />
                          {item.crop_type.charAt(0).toUpperCase() + item.crop_type.slice(1)} Analysis
                        </CardTitle>
                        <Badge className={getSeverityColor(item.confidence_score)}>
                          {getSeverityText(item.confidence_score)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">Date:</span>
                            <span>{new Date(item.created_at).toLocaleDateString()}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Disease:</span>
                            <span className="ml-2 font-medium">
                              {item.predicted_disease.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Confidence:</span>
                            <span className="ml-2 font-medium">
                              {(item.confidence_score * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>

                        {item.image_url && (
                          <div className="flex items-center justify-between">
                            <img 
                              src={`http://localhost:8000${item.image_url}`} 
                              alt="Analyzed crop" 
                              className="h-20 w-20 object-cover rounded-lg"
                            />
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => navigate(`/advisory?diagnosis_id=${item._id}`)}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                View Advisory
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={async () => {
                                  if (window.confirm("Are you sure you want to delete this scan? This action cannot be undone.")) {
                                    try {
                                      await deleteDiagnosis(item._id);
                                      toast({ title: "Scan deleted", description: "The scan and its image have been removed." });
                                      refetch();
                                    } catch (err: any) {
                                      toast({ title: "Delete failed", description: err?.response?.data?.detail || "An error occurred.", variant: "destructive" });
                                    }
                                  }
                                }}
                              >
                                Delete
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
            
            {!isLoading && !isError && (!history || history.length === 0) && (
              <div className="text-center py-16">
                <HistoryIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-4">
                  No History Found
                </h2>
                <p className="text-muted-foreground mb-6">
                  You haven't performed any diagnoses yet. Get started by analyzing your first crop!
                </p>
                <Button onClick={() => navigate("/dashboard")}>
                  Start Analysis
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}