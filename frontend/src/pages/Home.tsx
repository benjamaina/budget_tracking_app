import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Calendar, 
  Users, 
  TrendingUp, 
  Shield, 
  CheckCircle, 
  ArrowRight,
  BarChart3,
  HandHeart
} from 'lucide-react';

export const Home: React.FC = () => {
  const features = [
    {
      icon: Calendar,
      title: "Event Management",
      description: "Create and manage multiple events with detailed budget tracking for each occasion."
    },
    {
      icon: BarChart3,
      title: "Budget Control",
      description: "Set budgets, track expenses, and monitor financial performance with real-time analytics."
    },
    {
      icon: HandHeart,
      title: "Pledge System",
      description: "Manage pledges and donations from sponsors and attendees efficiently."
    },
    {
      icon: Users,
      title: "Vendor Management",
      description: "Keep track of vendors, their services, and payment schedules."
    },
    {
      icon: TrendingUp,
      title: "Analytics & Reports",
      description: "Generate comprehensive reports and gain insights into your event finances."
    },
    {
      icon: Shield,
      title: "Secure & Reliable",
      description: "Your financial data is protected with enterprise-grade security measures."
    }
  ];

  const benefits = [
    "Professional event budget management",
    "Real-time financial tracking",
    "Comprehensive reporting system",
    "Multi-event support",
    "Vendor and pledge management",
    "Mobile-responsive design"
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-surface">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-accent-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">Event Budget Manager</h1>
                <p className="text-sm text-muted-foreground">Professional Financial Tracking</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" asChild>
                <Link to="/login">Sign In</Link>
              </Button>
              <Button variant="default" asChild>
                <Link to="/register">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <Badge variant="secondary" className="mb-6">
            Professional Event Management
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
            Master Your Event
            <span className="text-accent"> Finances</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Streamline your event budget management with our comprehensive platform. 
            Track expenses, manage pledges, and generate detailed reports all in one place.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" className="w-full sm:w-auto" asChild>
              <Link to="/register">
                Start Free Trial <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="w-full sm:w-auto" asChild>
              <Link to="/login">Sign In to Account</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-surface-elevated">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Everything You Need for Event Success
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our platform provides all the tools you need to manage your event finances 
              professionally and efficiently.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-border hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-accent" />
                  </div>
                  <CardTitle className="text-foreground">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
                Why Choose Our Platform?
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Built specifically for event organizers who need professional-grade 
                financial management tools without the complexity.
              </p>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                    <span className="text-foreground">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gradient-to-br from-accent/10 to-accent/5 rounded-2xl p-8">
              <div className="text-center">
                <div className="text-4xl font-bold text-accent mb-2">KSh 0</div>
                <div className="text-lg text-foreground mb-4">Setup Cost</div>
                <div className="text-sm text-muted-foreground mb-6">
                  Start managing your event finances today at no upfront cost
                </div>
                <Button className="w-full" asChild>
                  <Link to="/register">Get Started Now</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-accent/5">
        <div className="container mx-auto text-center max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
            Ready to Transform Your Event Management?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join hundreds of event organizers who trust our platform for their financial management needs.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" asChild>
              <Link to="/register">
                Create Account <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/login">Already have an account?</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-12 px-4">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-accent-foreground" />
            </div>
            <span className="text-lg font-semibold text-foreground">Event Budget Manager</span>
          </div>
          <p className="text-muted-foreground">
            Professional event financial management made simple.
          </p>
        </div>
      </footer>
    </div>
  );
};