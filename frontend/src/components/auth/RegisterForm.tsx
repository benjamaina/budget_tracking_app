import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { Eye, EyeOff, DollarSign } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { toast } = useToast();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    
    try {
      await register(formData.username, formData.email, formData.password);
    } catch (error) {
      // Error handled in AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-6 animate-fade-in">
        {/* Logo */}
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-accent rounded-xl flex items-center justify-center mb-4">
            <DollarSign className="w-6 h-6 text-accent-foreground" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground">Event Budget Manager</h1>
          <p className="text-muted-foreground mt-2">Create your account to get started</p>
        </div>

        <Card className="border-border">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl">Create your account</CardTitle>
            <CardDescription>
              Set up your account to manage event budgets professionally
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Choose a username"
                  required
                  className="bg-input border-input-border"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email address"
                  required
                  className="bg-input border-input-border"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Create a strong password"
                    required
                    className="bg-input border-input-border pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? 
                      <EyeOff className="h-4 w-4 text-muted-foreground" /> : 
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    }
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  required
                  className="bg-input border-input-border"
                />
              </div>

              <Button 
                type="submit" 
                className="w-full bg-accent text-accent-foreground hover:bg-accent/90"
                disabled={loading}
              >
                {loading ? 'Creating account...' : 'Create account'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">Already have an account? </span>
              <Link 
                to="/login" 
                className="text-accent hover:text-accent/80 font-medium transition-colors"
              >
                Sign in here
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};