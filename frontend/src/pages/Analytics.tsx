import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { BudgetChart } from '@/components/dashboard/BudgetChart';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { 
  TrendingUp, DollarSign, Calendar, HandHeart, 
  Users, CheckCircle, AlertCircle 
} from 'lucide-react';
import { eventsAPI, budgetAPI, pledgesAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface Event {
  id: number;
  name: string;
  total_budget: number;
  total_received: number;
  total_pledged: number;
  percentage_covered: number;
}

interface AnalyticsData {
  totalEvents: number;
  totalBudget: number;
  totalReceived: number;
  totalPledged: number;
  avgPercentageCovered: number;
  eventBreakdown: Array<{
    name: string;
    budget: number;
    received: number;
    pledged: number;
  }>;
  categoryBreakdown: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

const COLORS = ['hsl(var(--primary))', 'hsl(var(--secondary))', 'hsl(var(--accent))', 'hsl(var(--muted))'];

export const Analytics = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<string>('all');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [eventsResponse, budgetResponse, pledgesResponse] = await Promise.all([
        eventsAPI.list(),
        budgetAPI.list(),
        pledgesAPI.list()
      ]);

      const eventsData = eventsResponse.data?.results || eventsResponse.data || [];
      const budgetData = budgetResponse.data?.results || budgetResponse.data || [];
      const pledgesData = pledgesResponse.data?.results || pledgesResponse.data || [];

      setEvents(eventsData);

      // Calculate analytics
      const totalEvents = eventsData.length;
      const totalBudget = eventsData.reduce((sum: number, event: Event) => sum + event.total_budget, 0);
      const totalReceived = eventsData.reduce((sum: number, event: Event) => sum + event.total_received, 0);
      const totalPledged = eventsData.reduce((sum: number, event: Event) => sum + event.total_pledged, 0);
      const avgPercentageCovered = eventsData.length > 0 
        ? eventsData.reduce((sum: number, event: Event) => sum + event.percentage_covered, 0) / eventsData.length 
        : 0;

      // Event breakdown for charts
      const eventBreakdown = eventsData.map((event: Event) => ({
        name: event.name.substring(0, 10) + (event.name.length > 10 ? '...' : ''),
        budget: event.total_budget,
        received: event.total_received,
        pledged: event.total_pledged
      }));

      // Category breakdown from budget items
      const categoryMap = new Map();
      budgetData.forEach((item: any) => {
        const category = item.category;
        if (categoryMap.has(category)) {
          categoryMap.set(category, categoryMap.get(category) + item.estimated_budget);
        } else {
          categoryMap.set(category, item.estimated_budget);
        }
      });

      const categoryBreakdown = Array.from(categoryMap.entries()).map(([name, value], index) => ({
        name,
        value,
        color: COLORS[index % COLORS.length]
      }));

      setAnalyticsData({
        totalEvents,
        totalBudget,
        totalReceived,
        totalPledged,
        avgPercentageCovered,
        eventBreakdown,
        categoryBreakdown
      });

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch analytics data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading || !analyticsData) {
    return (
      <Layout>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-surface-elevated rounded w-48"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-surface-elevated rounded-lg"></div>
            ))}
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="h-80 bg-surface-elevated rounded-lg"></div>
            <div className="h-80 bg-surface-elevated rounded-lg"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <Select value={selectedEvent} onValueChange={setSelectedEvent}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select Event" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Events</SelectItem>
              {events.map((event) => (
                <SelectItem key={event.id} value={event.id.toString()}>
                  {event.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Key Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Events"
            value={analyticsData.totalEvents.toString()}
            icon={Calendar}
            changeType="neutral"
          />
          <MetricCard
            title="Total Budget"
            value={`KSh ${analyticsData.totalBudget.toLocaleString()}`}
            icon={DollarSign}
            changeType="neutral"
          />
          <MetricCard
            title="Total Received"
            value={`KSh ${analyticsData.totalReceived.toLocaleString()}`}
            icon={CheckCircle}
            changeType="positive"
          />
          <MetricCard
            title="Avg Coverage"
            value={`${analyticsData.avgPercentageCovered.toFixed(1)}%`}
            icon={TrendingUp}
            changeType={analyticsData.avgPercentageCovered >= 75 ? "positive" : "negative"}
          />
        </div>

        {/* Charts */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Event Performance Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Event Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.eventBreakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => [`KSh ${value.toLocaleString()}`, '']}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--surface))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="budget" fill="hsl(var(--muted))" name="Budget" />
                  <Bar dataKey="received" fill="hsl(var(--primary))" name="Received" />
                  <Bar dataKey="pledged" fill="hsl(var(--accent))" name="Pledged" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Budget Category Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Budget by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analyticsData.categoryBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {analyticsData.categoryBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`KSh ${value.toLocaleString()}`, 'Amount']}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--surface))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Additional Analytics Components */}
        <div className="grid gap-6 md:grid-cols-2">
          <BudgetChart />
          <RecentActivity />
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="hover-lift transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-success" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Funded Events</p>
                  <p className="text-2xl font-bold text-foreground">
                    {events.filter(e => e.percentage_covered >= 100).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover-lift transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-warning" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Underfunded</p>
                  <p className="text-2xl font-bold text-foreground">
                    {events.filter(e => e.percentage_covered < 100).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover-lift transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                  <HandHeart className="w-6 h-6 text-accent" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Pledges</p>
                  <p className="text-2xl font-bold text-foreground">
                    KSh {analyticsData.totalPledged.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};