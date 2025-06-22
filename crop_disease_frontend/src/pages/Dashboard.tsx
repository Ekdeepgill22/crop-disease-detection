import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Camera, TrendingUp, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

async function predictDisease(imageFile: File) {
  const formData = new FormData();
  formData.append("file", imageFile);

  const { data } = await api.post("/disease/predict", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const { toast } = useToast();

  const mutation = useMutation({
    mutationFn: predictDisease,
    onSuccess: (data) => {
      toast({
        title: "Prediction Successful",
        description: `Disease: ${data.disease}, Confidence: ${data.confidence.toFixed(2)}%`,
      });
      // Here you would typically update a state to show the prediction results
      console.log("Prediction data:", data);
    },
    onError: (error: any) => {
      toast({
        title: "Prediction Failed",
        description: error.response?.data?.detail || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      mutation.mutate(selectedFile);
    } else {
      toast({
        title: "No file selected",
        description: "Please choose an image file to upload.",
        variant: "destructive",
      });
    }
  };

  return (
    <Layout isAuthenticated={true}>
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
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Scans
                </CardTitle>
                <Camera className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">42</div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Diseases Detected
                </CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">
                  Early detection saves crops
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Crops Saved
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">95%</div>
                <p className="text-xs text-muted-foreground">
                  Success rate this season
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Active Treatments
                </CardTitle>
                <Upload className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">
                  Ongoing treatments
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Upload</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <div className="border-2 border-dashed border-muted rounded-lg p-8">
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileChange}
                  />
                  {preview ? (
                    <div className="mb-4">
                      <img src={preview} alt="Selected crop" className="max-h-60 mx-auto rounded-lg" />
                    </div>
                  ) : (
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  )}
                  <p className="text-lg font-medium mb-2">
                    Upload crop image for analysis
                  </p>
                  <p className="text-muted-foreground mb-4">
                    Drag and drop or click to select files
                  </p>
                  <Button asChild>
                    <label htmlFor="file-upload">Choose File</label>
                  </Button>
                  {selectedFile && (
                    <Button onClick={handleUpload} className="ml-4" disabled={mutation.isPending}>
                      {mutation.isPending ? "Analyzing..." : "Analyze"}
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Placeholder for other sections */}
          <div className="text-center py-16">
            <h2 className="text-2xl font-bold mb-4">
              More Features Coming Soon
            </h2>
            <p className="text-muted-foreground">
              This is a placeholder page. Full dashboard functionality will be
              implemented in the next iteration.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
