import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Upload, Camera, TrendingUp, AlertTriangle, Loader2, CheckCircle, XCircle } from "lucide-react";
import api from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { useNavigate } from "react-router-dom";

async function predictDisease(formData: FormData) {
  const { data } = await api.post("/disease/predict", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

async function fetchDashboardStats() {
  const { data } = await api.get("/dashboard/statistics");
  return data;
}

async function fetchSupportedCrops() {
  const { data } = await api.get("/disease/supported-crops");
  return data;
}

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [cropType, setCropType] = useState<string>("");
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: fetchDashboardStats,
  });

  const { data: supportedCrops } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: fetchSupportedCrops,
  });

  const mutation = useMutation({
    mutationFn: predictDisease,
    onSuccess: (data) => {
      setPredictionResult(data);
      refetchStats();
      toast({
        title: "Analysis Complete",
        description: `Disease: ${data.disease_name}, Confidence: ${(data.confidence_score * 100).toFixed(1)}%`,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Analysis Failed",
        description: error.response?.data?.detail || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: "Invalid File Type",
          description: "Please select an image file (JPG, PNG, etc.)",
          variant: "destructive",
        });
        return;
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please select an image smaller than 5MB",
          variant: "destructive",
        });
        return;
      }

      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setPredictionResult(null); // Clear previous results
    }
  };

  const handleUpload = () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please choose an image file to upload.",
        variant: "destructive",
      });
      return;
    }

    if (!cropType) {
      toast({
        title: "Crop type required",
        description: "Please select the type of crop in the image.",
        variant: "destructive",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("crop_type", cropType);

    mutation.mutate(formData);
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setPreview(null);
    setCropType("");
    setPredictionResult(null);
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
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">
                Monitor your crops and get AI-powered insights
              </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Scans
                  </CardTitle>
                  <Camera className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_diagnoses || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    Lifetime diagnoses
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Diseases Detected
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.most_common_diseases?.length || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    Unique disease types
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Crop Types
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.most_common_crops?.length || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    Analyzed crop varieties
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    AI Accuracy
                  </CardTitle>
                  <Upload className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">95%</div>
                  <p className="text-xs text-muted-foreground">
                    Detection accuracy
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Upload Section */}
            <Card className="bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Crop Disease Analysis</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Upload an image of your crop to detect diseases and get treatment recommendations
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* File Upload Area */}
                  <div className="text-center">
                    <div className="border-2 border-dashed border-muted rounded-lg p-8">
                      <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                      {preview ? (
                        <div className="space-y-4">
                          <img 
                            src={preview} 
                            alt="Selected crop" 
                            className="max-h-60 mx-auto rounded-lg shadow-md" 
                          />
                          <Button 
                            variant="outline" 
                            onClick={resetUpload}
                            className="ml-4"
                          >
                            Choose Different Image
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
                          <div>
                            <p className="text-lg font-medium mb-2">
                              Upload crop image for analysis
                            </p>
                            <p className="text-muted-foreground mb-4">
                              Drag and drop or click to select files (JPG, PNG - Max 5MB)
                            </p>
                            <Button asChild>
                              <label htmlFor="file-upload" className="cursor-pointer">
                                Choose File
                              </label>
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Crop Type Selection */}
                  {selectedFile && (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Crop Type</label>
                      <Select value={cropType} onValueChange={setCropType}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select the type of crop in the image" />
                        </SelectTrigger>
                        <SelectContent>
                          {supportedCrops?.crops?.map((crop: string) => (
                            <SelectItem key={crop} value={crop}>
                              {crop.charAt(0).toUpperCase() + crop.slice(1)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {/* Analysis Button */}
                  {selectedFile && cropType && (
                    <Button 
                      onClick={handleUpload} 
                      className="w-full" 
                      size="lg"
                      disabled={mutation.isPending}
                    >
                      {mutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Analyzing Image...
                        </>
                      ) : (
                        <>
                          <Camera className="mr-2 h-4 w-4" />
                          Analyze Crop
                        </>
                      )}
                    </Button>
                  )}

                  {/* Results */}
                  {predictionResult && (
                    <Card className="border-2 border-emerald-200 bg-emerald-50">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-emerald-600" />
                          Analysis Results
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Disease Detected</p>
                            <p className="text-lg font-semibold">
                              {predictionResult.disease_name ? predictionResult.disease_name.replace(/_/g, ' ') : 'N/A'}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Confidence</p>
                            <div className="flex items-center gap-2">
                              <p className="text-lg font-semibold">
                                {predictionResult.confidence_score ? (predictionResult.confidence_score * 100).toFixed(1) : 'N/A'}%
                              </p>
                              <Badge 
                                variant={predictionResult.confidence_score > 0.8 ? "default" : "secondary"}
                              >
                                {predictionResult.confidence_score > 0.8 ? "High" : "Medium"}
                              </Badge>
                            </div>
                          </div>
                        </div>

                        {/* Advisory Section */}
                        {predictionResult.advisory && (
                          <div className="space-y-2">
                            <p className="text-sm font-medium text-muted-foreground">Treatment Recommendations</p>
                            <div className="bg-white p-4 rounded-lg border border-emerald-100">
                              <p className="text-sm mb-2 font-semibold text-emerald-800">{predictionResult.advisory.description}</p>
                              {predictionResult.advisory.treatment_steps && (
                                <ol className="list-decimal list-inside space-y-1 text-sm">
                                  {predictionResult.advisory.treatment_steps.map((step: any, index: number) => (
                                    <li key={index}>{step.description}</li>
                                  ))}
                                </ol>
                              )}
                              {predictionResult.advisory.prevention_tips && (
                                <div className="mt-3">
                                  <p className="font-medium text-emerald-700 mb-1">Prevention Tips:</p>
                                  <ul className="list-disc list-inside text-sm">
                                    {predictionResult.advisory.prevention_tips.map((tip: string, idx: number) => (
                                      <li key={idx}>{tip}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        <Button 
                          variant="outline"
                          className="w-full"
                          onClick={() => navigate(`/advisory?diagnosis_id=${predictionResult._id}&disease=${predictionResult.disease_name}&crop_type=${predictionResult.crop_type}`)}
                        >
                          View Detailed Advisory
                        </Button>
                        <Button
                          variant="ghost"
                          className="w-full mt-2"
                          onClick={() => navigate('/history')}
                        >
                          View Diagnosis History
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}