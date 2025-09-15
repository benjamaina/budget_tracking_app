import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Edit, Plus } from 'lucide-react';
import { budgetAPI, eventsAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface BudgetItem {
  id: number;
  category: string;
  allocated_amount: number;
  spent_amount: number;
  event: number;
}

interface Event {
  id: number;
  name: string;
}

const CHART_COLORS = [
  'hsl(var(--accent))',
  'hsl(var(--success))',
  'hsl(var(--warning))',
  'hsl(var(--destructive))',
  'hsl(var(--muted-foreground))',
  'hsl(var(--primary))',
];

export const BudgetChart: React.FC = () => {
  const [budgetItems, setBudgetItems] = useState<BudgetItem[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<BudgetItem | null>(null);
  const [formData, setFormData] = useState({
    category: '',
    allocated_amount: '',
    event: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [budgetResponse, eventsResponse] = await Promise.all([
        budgetAPI.list(),
        eventsAPI.list()
      ]);
      setBudgetItems(budgetResponse.data?.results || budgetResponse.data || []);
      setEvents(eventsResponse.data?.results || eventsResponse.data || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch budget data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item: BudgetItem) => {
    setEditingItem(item);
    setFormData({
      category: item.category || '',
      allocated_amount: (item.allocated_amount || 0).toString(),
      event: (item.event || '').toString()
    });
    setEditDialogOpen(true);
  };

  const handleAdd = () => {
    setFormData({ category: '', allocated_amount: '', event: '' });
    setAddDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent, isEdit: boolean) => {
    e.preventDefault();
    try {
      const data = {
        category: formData.category,
        allocated_amount: parseFloat(formData.allocated_amount),
        event: parseInt(formData.event)
      };

      if (isEdit && editingItem) {
        await budgetAPI.update(editingItem.id.toString(), data);
        toast({ title: "Success", description: "Budget item updated successfully" });
        setEditDialogOpen(false);
      } else {
        await budgetAPI.create(data);
        toast({ title: "Success", description: "Budget item created successfully" });
        setAddDialogOpen(false);
      }
      
      setFormData({ category: '', allocated_amount: '', event: '' });
      setEditingItem(null);
      fetchData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          Object.values(error.response?.data || {}).flat().join(', ') ||
                          "Failed to save budget item";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Budget Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="w-64 h-64 bg-surface-elevated rounded-full mx-auto"></div>
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-12 bg-surface-elevated rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = budgetItems.map((item, index) => ({
    name: item.category || 'Unknown',
    value: item.allocated_amount || 0,
    color: CHART_COLORS[index % CHART_COLORS.length],
    id: item.id
  }));

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-lg font-semibold">
          Budget Breakdown
          <Button variant="outline" size="sm" onClick={handleAdd}>
            <Plus className="w-4 h-4 mr-2" />
            Add Item
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No budget items found</p>
            <Button onClick={handleAdd}>Add Your First Budget Item</Button>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row items-center space-y-4 lg:space-y-0 lg:space-x-6">
            <div className="w-64 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`KSh ${value.toLocaleString()}`, 'Amount']}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="flex-1 space-y-3">
              {chartData.map((item, index) => {
                const budgetItem = budgetItems.find(b => b.id === item.id);
                return (
                  <div key={index} className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm font-medium text-foreground">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p className="text-sm font-semibold text-foreground">
                          KSh {item.value.toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {total > 0 ? ((item.value / total) * 100).toFixed(1) : 0}%
                        </p>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => budgetItem && handleEdit(budgetItem)}
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Budget Item</DialogTitle>
          </DialogHeader>
          <form onSubmit={(e) => handleSubmit(e, true)} className="space-y-4">
            <Input
              placeholder="Category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              required
            />
            <Input
              type="number"
              placeholder="Allocated Amount (KSh)"
              value={formData.allocated_amount}
              onChange={(e) => setFormData({ ...formData, allocated_amount: e.target.value })}
              required
            />
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
            <Button type="submit" className="w-full">Update Budget Item</Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Add Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Budget Item</DialogTitle>
          </DialogHeader>
          <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-4">
            <Input
              placeholder="Category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              required
            />
            <Input
              type="number"
              placeholder="Allocated Amount (KSh)"
              value={formData.allocated_amount}
              onChange={(e) => setFormData({ ...formData, allocated_amount: e.target.value })}
              required
            />
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
            <Button type="submit" className="w-full">Add Budget Item</Button>
          </form>
        </DialogContent>
      </Dialog>
    </Card>
  );
};