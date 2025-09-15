import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Calendar, DollarSign, HandHeart, Users, Edit } from 'lucide-react';
import { pledgesAPI, eventsAPI, dashboardAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { extractListData } from '@/lib/utils-api';

// Helper function to format time ago
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) return 'Just now';
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
  return `${Math.floor(diffInMinutes / 1440)}d ago`;
};

interface Pledge {
  id: number;
  pledger_name: string;
  amount: number;
  status: 'pending' | 'fulfilled' | 'cancelled';
  created_at: string;
  event: number;
  event_name?: string;
}

interface Event {
  id: number;
  name: string;
}

interface Activity {
  id: string;
  type: 'pledge' | 'payment' | 'budget' | 'event';
  title: string;
  description: string;
  amount: string;
  time: string;
  icon: any;
  status: string;
  originalData?: Pledge;
}

export const RecentActivity: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingPledge, setEditingPledge] = useState<Pledge | null>(null);
  const [formData, setFormData] = useState({
    pledger_name: '',
    amount: '',
    status: '',
    event: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [activitiesResponse, eventsResponse] = await Promise.all([
        dashboardAPI.recentActivities(),
        eventsAPI.list()
      ]);
      
      const events = extractListData<Event>(eventsResponse);
      const rawActivities = extractListData(activitiesResponse);
      setEvents(events);
      
      // Transform Django API response to match UI Activity interface
      const transformedActivities: Activity[] = rawActivities.map((item: any) => {
        const baseActivity = {
          id: `${item.type}-${item.id}`,
          type: item.type as 'pledge' | 'payment' | 'budget' | 'event',
        };

        // Transform based on activity type
        if (item.type === 'event') {
          return {
            ...baseActivity,
            title: 'New Event Created',
            description: `${item.name || 'Unnamed Event'}`,
            amount: 'Event',
            time: formatTimeAgo(item.created),
            icon: Calendar,
            status: 'neutral',
          };
        } else if (item.type === 'pledge') {
          return {
            ...baseActivity,
            title: 'New Pledge Received',
            description: `Pledge of KSh ${item.amount_pledged?.toLocaleString() || '0'}`,
            amount: `KSh ${item.amount_pledged?.toLocaleString() || '0'}`,
            time: formatTimeAgo(item.created),
            icon: HandHeart,
            status: 'success',
          };
        } else if (item.type === 'payment') {
          return {
            ...baseActivity,
            title: 'Payment Received',
            description: `M-Pesa payment of KSh ${item.amount?.toLocaleString() || '0'}`,
            amount: `KSh ${item.amount?.toLocaleString() || '0'}`,
            time: formatTimeAgo(item.created),
            icon: DollarSign,
            status: 'success',
          };
        }
        
        // Fallback for unknown types
        return {
          ...baseActivity,
          title: 'Activity',
          description: 'Recent activity',
          amount: '',
          time: formatTimeAgo(item.created),
          icon: DollarSign,
          status: 'neutral',
        };
      });

      setActivities(transformedActivities);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch recent activity",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (pledge: Pledge) => {
    setEditingPledge(pledge);
    setFormData({
      pledger_name: pledge.pledger_name,
      amount: pledge.amount.toString(),
      status: pledge.status,
      event: pledge.event.toString()
    });
    setEditDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPledge) return;

    try {
      await pledgesAPI.update(editingPledge.id.toString(), {
        pledger_name: formData.pledger_name,
        amount: parseFloat(formData.amount),
        status: formData.status,
        event: parseInt(formData.event)
      });
      
      toast({
        title: "Success",
        description: "Pledge updated successfully"
      });
      
      setEditDialogOpen(false);
      setEditingPledge(null);
      fetchData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          Object.values(error.response?.data || {}).flat().join(', ') ||
                          "Failed to update pledge";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse flex items-start space-x-4 p-3">
              <div className="w-10 h-10 bg-surface-elevated rounded-lg"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-surface-elevated rounded w-3/4"></div>
                <div className="h-3 bg-surface-elevated rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {activities.length === 0 ? (
          <div className="text-center py-8">
            <HandHeart className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-muted-foreground">No recent activity</p>
          </div>
        ) : (
          activities.map((activity) => {
            const Icon = activity.icon;
            
            return (
              <div key={activity.id} className="flex items-start space-x-4 p-3 rounded-lg hover:bg-surface-elevated transition-colors">
                <div className="w-10 h-10 bg-surface-elevated rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-accent" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-foreground truncate">
                      {activity.title}
                    </h4>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant={activity.status === 'success' ? 'default' : 'secondary'}
                        className="ml-2"
                      >
                        {activity.amount}
                      </Badge>
                      {activity.originalData && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(activity.originalData!)}
                        >
                          <Edit className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-xs text-muted-foreground mb-2">
                    {activity.description}
                  </p>
                  
                  <p className="text-xs text-muted-foreground">
                    {activity.time}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </CardContent>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Pledge</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              placeholder="Pledger Name"
              value={formData.pledger_name}
              onChange={(e) => setFormData({ ...formData, pledger_name: e.target.value })}
              required
            />
            <Input
              type="number"
              placeholder="Amount (KSh)"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              required
            />
            <select
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              required
            >
              <option value="">Select Status</option>
              <option value="pending">Pending</option>
              <option value="fulfilled">Fulfilled</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              value={formData.event}
              onChange={(e) => setFormData({ ...formData, event: e.target.value })}
              required
            >
              <option value="">Select Event</option>
              {events.map((event) => (
                <option key={event.id} value={event.id}>{event.name}</option>
              ))}
            </select>
            <Button type="submit" className="w-full">Update Pledge</Button>
          </form>
        </DialogContent>
      </Dialog>
    </Card>
  );
};