import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Leaf,
  Camera,
  Brain,
  CloudRain,
  TrendingUp,
  Shield,
  Clock,
  Users,
  ArrowRight,
  CheckCircle,
} from "lucide-react";

const features = [
  {
    icon: Camera,
    title: "Real-time Detection",
    description:
      "Upload crop images and get instant AI-powered disease identification with 95% accuracy.",
    color: "text-emerald-600",
  },
  {
    icon: Brain,
    title: "Smart Advisory",
    description:
      "Receive personalized treatment recommendations based on crop type, disease severity, and local conditions.",
    color: "text-forest-600",
  },
  {
    icon: CloudRain,
    title: "Weather Insights",
    description:
      "Get weather-adaptive farming tips and disease prevention strategies tailored to your location.",
    color: "text-earth-600",
  },
];

const benefits = [
  "Reduce crop loss by up to 40%",
  "Early disease detection saves costs",
  "Data-driven farming decisions",
  "24/7 AI agricultural advisor",
];

const stats = [
  { label: "Farmers Helped", value: "50,000+" },
  { label: "Diseases Detected", value: "200+" },
  { label: "Accuracy Rate", value: "95%" },
  { label: "Crops Saved", value: "1M+" },
];

export default function Landing() {
  return (
    <Layout isAuthenticated={false}>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-green-50 to-forest-50">
        <div className="absolute inset-0 bg-hero-pattern opacity-40"></div>
        <div className="relative container mx-auto px-4 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8 animate-fade-in">
              <div className="space-y-4">
                <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                  🚀 AI-Powered Agriculture
                </Badge>
                <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                  Smart Farming with{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-forest-600">
                    KhetAI
                  </span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-lg">
                  Detect crop diseases instantly, get expert treatment advice,
                  and maximize your harvest with AI-powered agricultural
                  intelligence.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register">
                  <Button size="lg" className="w-full sm:w-auto group">
                    Start Diagnosis
                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
                <Link to="/login">
                  <Button
                    variant="outline"
                    size="lg"
                    className="w-full sm:w-auto"
                  >
                    Sign In
                  </Button>
                </Link>
              </div>

              <div className="grid grid-cols-2 gap-6 pt-8">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                    <span className="text-sm text-muted-foreground">
                      {benefit}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative animate-fade-in">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-forest-400 rounded-3xl rotate-6 opacity-20"></div>
                <Card className="relative bg-white/80 backdrop-blur-sm border-0 shadow-2xl">
                  <CardContent className="p-8">
                    <div className="space-y-6">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                          <Leaf className="h-6 w-6 text-emerald-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold">Disease Detection</h3>
                          <p className="text-sm text-muted-foreground">
                            Upload & Analyze
                          </p>
                        </div>
                      </div>

                      <div className="bg-gradient-to-r from-emerald-50 to-forest-50 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            Analysis Progress
                          </span>
                          <span className="text-sm text-emerald-600">98%</span>
                        </div>
                        <div className="w-full bg-emerald-200 rounded-full h-2">
                          <div className="bg-emerald-600 h-2 rounded-full w-[98%]"></div>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                          <span className="text-sm font-medium">
                            Leaf Spot Disease
                          </span>
                          <Badge className="bg-emerald-100 text-emerald-800">
                            High Confidence
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                          <span className="text-sm font-medium">
                            Treatment Available
                          </span>
                          <Badge className="bg-orange-100 text-orange-800">
                            Immediate Action
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center space-y-2">
                <div className="text-3xl lg:text-4xl font-bold text-emerald-600">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-b from-white to-emerald-50">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-16">
            <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
              🌱 Advanced Features
            </Badge>
            <h2 className="text-3xl lg:text-4xl font-bold">
              Everything you need for smart farming
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our AI-powered platform combines cutting-edge technology with
              agricultural expertise to help you make informed decisions.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={index}
                  className="group hover:shadow-lg transition-shadow border-0 bg-white/80 backdrop-blur-sm"
                >
                  <CardHeader>
                    <div
                      className={`h-12 w-12 rounded-xl bg-gradient-to-br from-emerald-100 to-forest-100 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                    >
                      <Icon className={`h-6 w-6 ${feature.color}`} />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold">How KhetAI Works</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Simple steps to transform your farming with AI technology
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
                <Camera className="h-8 w-8 text-emerald-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold">1. Upload Image</h3>
                <p className="text-muted-foreground">
                  Take a photo of your crop and upload it to our platform
                </p>
              </div>
            </div>

            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-forest-100 rounded-full flex items-center justify-center mx-auto">
                <Brain className="h-8 w-8 text-forest-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold">2. AI Analysis</h3>
                <p className="text-muted-foreground">
                  Our AI analyzes the image and identifies potential diseases
                </p>
              </div>
            </div>

            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-earth-100 rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="h-8 w-8 text-earth-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold">3. Get Results</h3>
                <p className="text-muted-foreground">
                  Receive detailed diagnosis and treatment recommendations
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-emerald-600 to-forest-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <div className="space-y-6 max-w-3xl mx-auto">
            <h2 className="text-3xl lg:text-4xl font-bold">
              Ready to revolutionize your farming?
            </h2>
            <p className="text-xl opacity-90">
              Join thousands of farmers who are already using KhetAI to protect
              their crops and increase yields.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button
                  size="lg"
                  variant="secondary"
                  className="w-full sm:w-auto"
                >
                  Start Free Trial
                </Button>
              </Link>
              <Link to="/login">
                <Button
                  size="lg"
                  variant="outline"
                  className="w-full sm:w-auto border-white text-white hover:bg-white hover:text-emerald-600"
                >
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-gray-900 text-white">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600">
                  <Leaf className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">KhetAI</span>
              </div>
              <p className="text-gray-400">
                AI-powered crop disease detection and agricultural advisory
                platform.
              </p>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold">Product</h4>
              <div className="space-y-2 text-gray-400">
                <div>Disease Detection</div>
                <div>Treatment Advisory</div>
                <div>Weather Insights</div>
                <div>Analytics</div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold">Support</h4>
              <div className="space-y-2 text-gray-400">
                <div>Help Center</div>
                <div>Contact Us</div>
                <div>Documentation</div>
                <div>Community</div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold">Company</h4>
              <div className="space-y-2 text-gray-400">
                <div>About Us</div>
                <div>Privacy Policy</div>
                <div>Terms of Service</div>
                <div>Careers</div>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 KhetAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </Layout>
  );
}
