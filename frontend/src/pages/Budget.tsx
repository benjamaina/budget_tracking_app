import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Plus, DollarSign, CheckCircle, Trash2 } from 'lucide-react';
import { budgetAPI, eventsAPI, tasksAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatErrorForToast } from '@/lib/error-utils';

interface BudgetItem {
  id: number;
  event: number;
  category: string;
  estimated_budget: number;
  is_funded: boolean;
  total_vendor_payments: number;
  remaining_budget: number;
  is_fully_paid: boolean;
}

interface Event {
  id: number;
  name: string;
}

interface Task {
  id: number;
  budget_item: number;
  title: string;
  description: string;
  allocated_amount: number;
  amount_paid: number;
  balance: number;
}

export const Budget = () => {
  const [budgetItems, setBudgetItems] = useState<BudgetItem[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [tasks, setTasks] = useState<{ [key: number]: Task[] }>({});
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [selectedBudgetItemId, setSelectedBudgetItemId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    event: '',
    category: '',
    estimated_budget: ''
  });
  const [taskFormData, setTaskFormData] = useState({
    title: '',
    description: '',
    allocated_amount: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [budgetResponse, eventsResponse] = await Promise.all([
        budgetAPI.list(),
        eventsAPI.list()
      ]);
      const budgetData = budgetResponse.data?.results || budgetResponse.data || [];
      setBudgetItems(budgetData);
      setEvents(eventsResponse.data?.results || eventsResponse.data || []);
      
      // Fetch tasks for each budget item
      const taskPromises = budgetData.map((item: BudgetItem) => 
        tasksAPI.list({ budget_item: item.id })
      );
      const taskResponses = await Promise.all(taskPromises);
      
      const tasksData: { [key: number]: Task[] } = {};
      budgetData.forEach((item: BudgetItem, index: number) => {
        tasksData[item.id] = taskResponses[index].data?.results || taskResponses[index].data || [];
      });
      setTasks(tasksData);
    } catch (error) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await budgetAPI.create({
        ...formData,
        event: parseInt(formData.event),
        estimated_budget: parseFloat(formData.estimated_budget)
      });
      toast({
        title: "Success",
        description: "Budget item created successfully",
      });
      setDialogOpen(false);
      setFormData({ event: '', category: '', estimated_budget: '' });
      fetchData();
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this budget item?')) return;
    
    try {
      await budgetAPI.delete(id.toString());
      toast({
        title: "Success",
        description: "Budget item deleted successfully",
      });
      fetchData();
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await tasksAPI.create({
        ...taskFormData,
        allocated_amount: parseFloat(taskFormData.allocated_amount),
        budget_item: selectedBudgetItemId
      });
      
      toast({
        title: "Success",
        description: "Task created successfully",
      });
      
      setTaskFormData({ title: '', description: '', allocated_amount: '' });
      setShowTaskDialog(false);
      fetchData();
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await tasksAPI.delete(taskId);
        toast({
          title: "Success",
          description: "Task deleted successfully",
        });
        fetchData();
      } catch (error: any) {
        const { title, description } = formatErrorForToast(error);
        toast({
          title,
          description,
          variant: "destructive",
        });
      }
    }
  };

  const openTaskDialog = (budgetItemId: number) => {
    setSelectedBudgetItemId(budgetItemId);
    setShowTaskDialog(true);
  };

  const getEventName = (eventId: number) => {
    const event = events.find(e => e.id === eventId);
    return event ? event.name : 'Unknown Event';
  };

  if (loading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-surface-elevated rounded w-48"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-surface-elevated rounded-lg"></div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* HEADER + NEW BUDGET ITEM */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">Budget Items</h1>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="hover-lift">
                <Plus className="w-4 h-4 mr-2" />
                New Budget Item
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Budget Item</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Select value={formData.event} onValueChange={(value) => setFormData({ ...formData, event: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Event" />
                  </SelectTrigger>
                  <SelectContent>
                    {events.map((event) => (
                      <SelectItem key={event.id} value={event.id.toString()}>
                        {event.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  placeholder="Category (e.g., Catering, Venue, Equipment)"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                />
                <Input
                  type="number"
                  placeholder="Estimated Budget (KSh)"
                  value={formData.estimated_budget}
                  onChange={(e) => setFormData({ ...formData, estimated_budget: e.target.value })}
                  required
                />
                <Button type="submit" className="w-full">Create Budget Item</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* BUDGET CARDS */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {budgetItems.map((item) => (
            <Card key={item.id} className="hover-lift transition-all duration-200">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {item.category}
                  <div className="flex items-center gap-2">
                    <Badge variant={item.is_fully_paid ? "default" : "secondary"}>
                      {item.is_fully_paid ? "Paid" : "Pending"}
                    </Badge>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardTitle>
                <p className="text-sm text-muted-foreground">{getEventName(item.event)}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Budget</span>
                    <span className="font-medium">KSh {item.estimated_budget.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Paid</span>
                    <span className="font-medium">KSh {item.total_vendor_payments.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Remaining</span>
                    <span className="font-medium">KSh {item.remaining_budget.toLocaleString()}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{((item.total_vendor_payments / item.estimated_budget) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-surface-elevated rounded-full h-2">
                    <div 
                      className="bg-accent h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${Math.min((item.total_vendor_payments / item.estimated_budget) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Tasks Section */}
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="text-sm font-medium">Tasks</h4>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openTaskDialog(item.id)}
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add Task
                    </Button>
                  </div>
                  {tasks[item.id] && tasks[item.id].length > 0 ? (
                    <div className="space-y-2">
                      {tasks[item.id].map((task) => (
                        <div key={task.id} className="p-2 bg-surface-elevated rounded-lg">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <p className="text-sm font-medium">{task.title}</p>
                              {task.description && (
                                <p className="text-xs text-muted-foreground mt-1">{task.description}</p>
                              )}
                              <div className="flex justify-between text-xs mt-2">
                                <span>Allocated: KSh {task.allocated_amount.toLocaleString()}</span>
                                <span>Balance: KSh {task.balance.toLocaleString()}</span>
                              </div>
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDeleteTask(task.id)}
                              className="ml-2 text-destructive hover:text-destructive"
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">No tasks added yet</p>
                  )}
                </div>

                {item.is_funded && (
                  <div className="flex items-center text-success text-sm">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Funded
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {budgetItems.length === 0 && (
          <div className="text-center py-12">
            <DollarSign className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No budget items yet</h3>
            <p className="text-muted-foreground">Create your first budget item to get started.</p>
          </div>
        )}
      </div>

      {/* Task Dialog */}
      <Dialog open={showTaskDialog} onOpenChange={setShowTaskDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Task</DialogTitle>
            <DialogDescription>
              Create a task for a budget item.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleTaskSubmit} className="space-y-4">
            {/* Budget Item Dropdown */}
            <div>
              <Label>Budget Item</Label>
              <Select
                value={selectedBudgetItemId?.toString() || ""}
                onValueChange={(value) => setSelectedBudgetItemId(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Budget Item" />
                </SelectTrigger>
                <SelectContent>
                  {budgetItems.map((item) => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.category} ({getEventName(item.event)})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="task-title">Title</Label>
              <Input
                id="task-title"
                value={taskFormData.title}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, title: e.target.value }))}
                required
              />
            </div>
            <div>
              <Label htmlFor="task-description">Description (Optional)</Label>
              <Input
                id="task-description"
                value={taskFormData.description}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>
            <div>
              <Label htmlFor="task-allocated-amount">Allocated Amount (KSh)</Label>
              <Input
                id="task-allocated-amount"
                type="number"
                step="0.01"
                value={taskFormData.allocated_amount}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, allocated_amount: e.target.value }))}
                required
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowTaskDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Add Task</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};
