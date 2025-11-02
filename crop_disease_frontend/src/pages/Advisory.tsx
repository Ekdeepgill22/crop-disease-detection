import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, CloudRain, Thermometer, Droplets, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import api from "@/lib/api";

async function fetchWeatherAdvisory() {
  try {
    const { data } = await api.get("/advisory/weather");
    return data;
  } catch (error) {
    // Return mock weather data if API fails
    return {
      temperature: 25,
      humidity: 65,
      weather_condition: "partly_cloudy",
      planting_advice: "Good conditions for planting most crops",
      irrigation_advice: "Maintain regular watering schedule",
      pest_risk: "Low risk of pest activity",
      humidity_advice: "Humidity is low. Plants may need extra irrigation."
    };
  }
}

async function fetchDiseaseAdvisory(diseaseName: string, cropType: string) {
  try {
    const { data } = await api.get(`/advisory/disease/${diseaseName}?crop_type=${cropType}`);
    return data;
  } catch (error) {
    // Return mock advisory data if API fails
    return {
      disease_name: diseaseName,
      crop_type: cropType,
      description: `Treatment information for ${diseaseName.replace(/_/g, ' ')} (${cropType})`,
      symptoms: [
        "Visible spots or lesions on leaves",
        "Discoloration of plant tissue",
        "Wilting or stunted growth"
      ],
      treatment_steps: [
        {
          step: 1,
          description: "Remove affected plant parts immediately",
          materials_needed: ["Pruning shears", "Disinfectant"]
        },
        {
          step: 2,
          description: "Apply appropriate fungicide or treatment",
          materials_needed: ["Fungicide", "Sprayer"]
        },
        {
          step: 3,
          description: "Monitor plant recovery and repeat if necessary",
          materials_needed: ["Regular monitoring"]
        }
      ],
      prevention_tips: [
        "Ensure proper plant spacing for air circulation",
        "Water at soil level to avoid wetting leaves",
        "Remove plant debris regularly",
        "Use disease-resistant varieties when possible"
      ],
      estimated_recovery_time: "2-3 weeks with proper treatment"
    };
  }
}

async function fetchDiagnosisById(diagnosisId: string) {
  const { data } = await api.get(`/disease/diagnosis/${diagnosisId}`);
  return data;
}

function getPestRiskLevel(pestRisk) {
  if (!pestRisk) return '';
  const risk = pestRisk.toLowerCase();
  if (risk.includes('high')) return 'High';
  if (risk.includes('medium')) return 'Medium';
  if (risk.includes('low')) return 'Low';
  return '';
}

export default function Advisory() {
  const [searchParams] = useSearchParams();
  const diseaseName = searchParams.get("disease");
  const cropType = searchParams.get("crop_type");
  const diagnosisId = searchParams.get("diagnosis_id");

  const { data: weatherData, isLoading: isLoadingWeather } = useQuery({
    queryKey: ["weatherAdvisory"],
    queryFn: fetchWeatherAdvisory,
  });

  // If diagnosisId is present, fetch diagnosis and use its advisory
  const { data: diagnosisData, isLoading: isLoadingDiagnosis } = useQuery({
    queryKey: ["diagnosisAdvisory", diagnosisId],
    queryFn: () => fetchDiagnosisById(diagnosisId!),
    enabled: !!diagnosisId,
  });

  // If no diagnosisId, fall back to disease name
  const { data: diseaseData, isLoading: isLoadingDisease } = useQuery({
    queryKey: ["diseaseAdvisory", diseaseName, cropType],
    queryFn: () => fetchDiseaseAdvisory(diseaseName!, cropType!),
    enabled: !!diseaseName && !!cropType && !diagnosisId,
  });

  // Choose advisory data
  const advisoryData = diagnosisId ? diagnosisData?.advisory : diseaseData;
  const isLoadingAdvisory = diagnosisId ? isLoadingDiagnosis : isLoadingDisease;

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
              <h1 className="text-3xl font-bold">Agricultural Advisory</h1>
              <p className="text-muted-foreground">
                Get expert recommendations and weather-based insights
              </p>
            </div>

            {/* Weather Widget */}
            <Card className="bg-white/90 backdrop-blur-sm">
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
                  <div className="space-y-6">
                    {/* 4-column weather summary */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-4 bg-orange-50 rounded-lg flex flex-col items-center">
                        <Thermometer className="h-8 w-8 text-orange-500 mb-2" />
                        <p className="text-sm text-muted-foreground">Temperature</p>
                        <p className="text-lg font-semibold">{weatherData?.temperature}°C</p>
                      </div>
                      <div className="text-center p-4 bg-blue-50 rounded-lg flex flex-col items-center">
                        <Droplets className="h-8 w-8 text-blue-500 mb-2" />
                        <p className="text-sm text-muted-foreground">Humidity</p>
                        <p className="text-lg font-semibold">{weatherData?.humidity}%</p>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg flex flex-col items-center">
                        <CloudRain className="h-8 w-8 text-gray-500 mb-2" />
                        <p className="text-sm text-muted-foreground">Condition</p>
                        <p className="text-lg font-semibold capitalize">
                          {weatherData?.weather_condition?.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 rounded-lg flex flex-col items-center">
                        <AlertCircle className="h-8 w-8 text-yellow-700 mb-2" />
                        <p className="text-sm text-muted-foreground">Pest Risk</p>
                        <p className="text-lg font-semibold capitalize">
                          {getPestRiskLevel(weatherData?.pest_risk)}
                        </p>
                      </div>
                    </div>

                    {/* 4-column advice row (add Pest Risk here) */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-medium text-green-800 mb-2">Planting Advice</h4>
                        <p className="text-sm text-green-700">{weatherData?.planting_advice}</p>
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-800 mb-2">Irrigation</h4>
                        <p className="text-sm text-blue-700">{weatherData?.irrigation_advice}</p>
                      </div>
                      <div className="bg-orange-50 p-4 rounded-lg">
                        <h4 className="font-medium text-orange-800 mb-2">Humidity Advice</h4>
                        <p className="text-sm text-orange-700">{weatherData?.humidity_advice}</p>
                      </div>
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <h4 className="font-medium text-yellow-800 mb-2">Pest Risk</h4>
                        <p className="text-sm text-yellow-700">{weatherData?.pest_risk}</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Disease Advisory */}
            {(diseaseName || diagnosisId) && (
              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    Treatment Advisory
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoadingAdvisory ? (
                    <div className="flex justify-center items-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : advisoryData ? (
                    <div className="space-y-6">
                      {/* Description */}
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="font-medium text-red-800 mb-2">Disease Information</h4>
                        <p className="text-sm text-red-700">{advisoryData.description}</p>
                      </div>

                      {/* Treatment Steps */}
                      {advisoryData.treatment_steps && (
                        <div>
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            Treatment Steps
                          </h4>
                          <ol className="space-y-4">
                            {advisoryData.treatment_steps.map((step: any, index: number) => (
                              <li key={index} className="flex gap-4">
                                <div className="flex-shrink-0 w-8 h-8 bg-green-100 text-green-800 rounded-full flex items-center justify-center text-sm font-medium">
                                  {step.step}
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm font-medium">{step.description}</p>
                                  {step.materials_needed && step.materials_needed.length > 0 && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                      Materials: {step.materials_needed.join(", ")}
                                    </p>
                                  )}
                                </div>
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}

                      {/* Prevention Tips */}
                      {advisoryData.prevention_tips && (
                        <div>
                          <h4 className="font-medium mb-3">Prevention Tips</h4>
                          <ul className="space-y-2">
                            {advisoryData.prevention_tips.map((tip: string, index: number) => (
                              <li key={index} className="flex items-start gap-2 text-sm">
                                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                                {tip}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No advisory found for this disease.
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {!diseaseName && (
              <div className="text-center py-16">
                <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-4">
                  Select a Disease for Advisory
                </h2>
                <p className="text-muted-foreground">
                  To see specific treatment advice, first get a diagnosis from the dashboard.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}