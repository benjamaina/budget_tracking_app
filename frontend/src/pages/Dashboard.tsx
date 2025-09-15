import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { BudgetChart } from '@/components/dashboard/BudgetChart';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  DollarSign, 
  TrendingUp, 
  HandHeart, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  Users,
  Target
} from 'lucide-react';
import { dashboardAPI } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';

interface DashboardData {
  summary: {
    total_events: number;
    active_events: number;
    funded_events: number;
    total_budget: number;
  };
  upcoming_events: Array<{
    id: number;
    title: string;
    event_date: string;
    total_budget: number;
    is_funded: boolean;
  }>;
}

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.general();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => `KSh ${amount.toLocaleString()}`;

  if (!dashboardData && !loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">No dashboard data available</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-4">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-foreground">Welcome to Event Budget Manager</h1>
            <p className="text-xl text-muted-foreground">
              Your comprehensive solution for managing event budgets, pledges, and vendor payments in Kenya.
            </p>
          </div>
          
          {/* App Info */}
          <div className="bg-surface border border-border rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-foreground mb-3">Getting Started</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">📅 Event Management</h3>
                <p className="text-muted-foreground">Create and manage your events with detailed budget tracking</p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">💰 Budget Control</h3>
                <p className="text-muted-foreground">Track expenses, set limits, and monitor financial health</p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">🤝 Pledge System</h3>
                <p className="text-muted-foreground">Manage pledges and payments including M-Pesa integration</p>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            <>
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
            </>
          ) : dashboardData ? (
            <>
              <MetricCard
                title="Total Budget"
                value={formatCurrency(dashboardData.summary.total_budget)}
                change={`${dashboardData.summary.active_events} active events`}
                changeType="neutral"
                icon={DollarSign}
              />
              
              <MetricCard
                title="Total Events"
                value={dashboardData.summary.total_events.toString()}
                change={`${dashboardData.summary.funded_events} fully funded`}
                changeType={dashboardData.summary.funded_events > 0 ? "positive" : "neutral"}
                icon={Calendar}
              />
              
              <MetricCard
                title="Active Events"
                value={dashboardData.summary.active_events.toString()}
                change="Upcoming events"
                changeType="neutral"
                icon={Users}
              />
              
              <MetricCard
                title="Funding Rate"
                value={`${dashboardData.summary.total_events > 0 ? Math.round((dashboardData.summary.funded_events / dashboardData.summary.total_events) * 100) : 0}%`}
                change="Events fully funded"
                changeType={dashboardData.summary.funded_events >= dashboardData.summary.total_events / 2 ? "positive" : "neutral"}
                icon={Target}
              />
            </>
          ) : null}
        </div>

        {/* Charts and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <BudgetChart />
          <RecentActivity />
        </div>

        {/* Upcoming Events */}
        {dashboardData && dashboardData.upcoming_events.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Upcoming Events
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.upcoming_events.slice(0, 5).map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                    <div className="space-y-1">
                      <h4 className="font-medium text-foreground">{event.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {new Date(event.event_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right space-y-1">
                      <p className="font-medium text-foreground">
                        {formatCurrency(event.total_budget)}
                      </p>
                      <Badge variant={event.is_funded ? "default" : "secondary"}>
                        {event.is_funded ? "Funded" : "Pending"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};