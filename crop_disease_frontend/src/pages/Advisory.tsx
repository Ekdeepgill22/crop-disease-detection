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
      pest_risk: "Low risk of pest activity"
    };
  }
}

async function fetchDiseaseAdvisory(diseaseName: string) {
  try {
    const { data } = await api.get(`/advisory/disease/${diseaseName}`);
    return data;
  } catch (error) {
    // Return mock advisory data if API fails
    return {
      disease_name: diseaseName,
      description: `Treatment information for ${diseaseName.replace(/_/g, ' ')}`,
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
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <Thermometer className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Temperature</p>
                        <p className="text-lg font-semibold">{weatherData?.temperature}°C</p>
                      </div>
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <Droplets className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Humidity</p>
                        <p className="text-lg font-semibold">{weatherData?.humidity}%</p>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg col-span-2 md:col-span-1">
                        <CloudRain className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Condition</p>
                        <p className="text-lg font-semibold capitalize">
                          {weatherData?.weather_condition?.replace(/_/g, ' ')}
                        </p>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-medium text-green-800 mb-2">Planting Advice</h4>
                        <p className="text-sm text-green-700">{weatherData?.planting_advice}</p>
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-800 mb-2">Irrigation</h4>
                        <p className="text-sm text-blue-700">{weatherData?.irrigation_advice}</p>
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
            {diseaseName && (
              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    Treatment Advisory: {diseaseName.replace(/_/g, " ")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoadingDisease ? (
                    <div className="flex justify-center items-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : diseaseData ? (
                    <div className="space-y-6">
                      {/* Description */}
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="font-medium text-red-800 mb-2">Disease Information</h4>
                        <p className="text-sm text-red-700">{diseaseData.description}</p>
                      </div>

                      {/* Symptoms */}
                      {diseaseData.symptoms && (
                        <div>
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <AlertCircle className="h-4 w-4 text-orange-600" />
                            Symptoms to Look For
                          </h4>
                          <ul className="space-y-2">
                            {diseaseData.symptoms.map((symptom: string, index: number) => (
                              <li key={index} className="flex items-start gap-2 text-sm">
                                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                                {symptom}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Treatment Steps */}
                      {diseaseData.treatment_steps && (
                        <div>
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            Treatment Steps
                          </h4>
                          <ol className="space-y-4">
                            {diseaseData.treatment_steps.map((step: any, index: number) => (
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
                      {diseaseData.prevention_tips && (
                        <div>
                          <h4 className="font-medium mb-3">Prevention Tips</h4>
                          <ul className="space-y-2">
                            {diseaseData.prevention_tips.map((tip: string, index: number) => (
                              <li key={index} className="flex items-start gap-2 text-sm">
                                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                                {tip}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recovery Time */}
                      {diseaseData.estimated_recovery_time && (
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <h4 className="font-medium text-blue-800 mb-2">Expected Recovery Time</h4>
                          <p className="text-sm text-blue-700">{diseaseData.estimated_recovery_time}</p>
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