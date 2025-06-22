import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, CloudRain, Thermometer, Droplets } from "lucide-react";

export default function Advisory() {
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
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <Thermometer className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Temperature</p>
                  <p className="text-lg font-semibold">28°C</p>
                </div>
                <div className="text-center">
                  <Droplets className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Humidity</p>
                  <p className="text-lg font-semibold">75%</p>
                </div>
                <div className="text-center">
                  <CloudRain className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Rainfall</p>
                  <p className="text-lg font-semibold">12mm</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sample Advisory */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Advisory</CardTitle>
                <Badge className="bg-yellow-100 text-yellow-800">
                  Action Required
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <h3 className="font-semibold mb-2">
                Late Blight Treatment Protocol
              </h3>
              <p className="text-muted-foreground mb-4">
                Based on your recent tomato plant diagnosis, here are the
                recommended treatment steps:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>Apply copper-based fungicide immediately</li>
                <li>Remove affected plant parts and destroy them</li>
                <li>Improve air circulation around plants</li>
                <li>Reduce watering frequency to prevent moisture buildup</li>
              </ol>
            </CardContent>
          </Card>

          {/* Placeholder */}
          <div className="text-center py-16">
            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-4">
              Advanced Advisory Coming Soon
            </h2>
            <p className="text-muted-foreground">
              This is a placeholder page. Complete advisory system with
              personalized recommendations will be implemented in the next
              iteration.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
