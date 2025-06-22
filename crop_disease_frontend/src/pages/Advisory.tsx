import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, CloudRain, Thermometer, Droplets, Loader2 } from "lucide-react";
import api from "@/lib/api";

async function fetchWeatherAdvisory() {
  const { data } = await api.get("/advisory/weather");
  return data;
}

async function fetchDiseaseAdvisory(diseaseName: string) {
  const { data } = await api.get(`/advisory/disease/${diseaseName}`);
  return data;
}

export default function Advisory() {
  const [searchParams] = useSearchParams();
  const diseaseName = searchParams.get("disease");

  const { data: weatherData, isLoading: isLoadingWeather } = useQuery({
    queryKey: ["weatherAdvisory"],
    queryFn: fetchWeatherAdvisory,
  });

  const { data: diseaseData, isLoading: isLoadingDisease } = useQuery({
    queryKey: ["diseaseAdvisory", diseaseName],
    queryFn: () => fetchDiseaseAdvisory(diseaseName!),
    enabled: !!diseaseName,
  });

  return (
    <Layout isAuthenticated={true}>
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold">Agricultural Advisory</h1>
            <p className="text-muted-foreground">
              Get expert recommendations and weather-based insights
            </p>
          </div>

          {/* Weather Widget */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CloudRain className="h-5 w-5 text-blue-600" />
                Weather Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingWeather ? (
                <div className="flex justify-center items-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <Thermometer className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Temperature</p>
                    <p className="text-lg font-semibold">{weatherData?.temperature}°C</p>
                  </div>
                  <div className="text-center">
                    <Droplets className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Humidity</p>
                    <p className="text-lg font-semibold">{weatherData?.humidity}%</p>
                  </div>
                  <div className="text-center">
                    <CloudRain className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Rainfall</p>
                    <p className="text-lg font-semibold">{weatherData?.rainfall}mm</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Disease Advisory */}
          {diseaseName && (
            <Card>
              <CardHeader>
                <CardTitle>Advisory for {diseaseName.replace(/_/g, " ")}</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoadingDisease ? (
                  <div className="flex justify-center items-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </div>
                ) : diseaseData ? (
                  <ol className="list-decimal list-inside space-y-2 text-sm">
                    {diseaseData.treatment.map((step: string, index: number) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                ) : (
                  <p>No advisory found for this disease.</p>
                )}
              </CardContent>
            </Card>
          )}

          {!diseaseName && (
            <div className="text-center py-16">
              <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4">
                Select a Disease
              </h2>
              <p className="text-muted-foreground">
                To see specific treatment advice, first get a diagnosis from the dashboard.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
