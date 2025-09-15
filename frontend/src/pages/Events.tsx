import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious, PaginationEllipsis } from '@/components/ui/pagination';
import { Plus, Calendar, MapPin, DollarSign, Trash2, Edit } from 'lucide-react';
import { eventsAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatErrorForToast } from '@/lib/error-utils';

interface Event {
  id: number;
  name: string;
  description: string;
  venue: string;
  total_budget: number;
  event_date: string;
  is_funded: boolean;
  total_received: number;
  total_pledged: number;
  percentage_covered: number;
}

export const Events = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    venue: '',
    total_budget: '',
    event_date: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchEvents(1);
  }, []);

  useEffect(() => {
    fetchEvents(currentPage);
  }, [currentPage]);

  const fetchEvents = async (page: number = 1) => {
    try {
      const response = await eventsAPI.list(`?page=${page}`);
      // Handle paginated response format
      const eventsData = response.data.results || response.data;
      setEvents(Array.isArray(eventsData) ? eventsData : []);
      
      // Set pagination metadata
      if (response.data.results) {
        const count = response.data.count || 0;
        const pageSize = response.data.page_size || 10;
        setTotalCount(count);
        setTotalPages(Math.ceil(count / pageSize));
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch events",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent, isEdit: boolean = false) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        total_budget: parseFloat(formData.total_budget)
      };

      if (isEdit && editingEvent) {
        await eventsAPI.update(editingEvent.id.toString(), data);
        toast({
          title: "Success",
          description: "Event updated successfully",
        });
        setEditDialogOpen(false);
        setEditingEvent(null);
      } else {
        await eventsAPI.create(data);
        toast({
          title: "Success",
          description: "Event created successfully",
        });
        setDialogOpen(false);
      }
      
      setFormData({ name: '', description: '', venue: '', total_budget: '', event_date: '' });
      fetchEvents(currentPage);
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleEdit = (event: Event) => {
    setEditingEvent(event);
    setFormData({
      name: event.name,
      description: event.description,
      venue: event.venue,
      total_budget: event.total_budget.toString(),
      event_date: event.event_date
    });
    setEditDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this event?')) return;
    
    try {
      await eventsAPI.delete(id.toString());
      toast({
        title: "Success",
        description: "Event deleted successfully",
      });
      fetchEvents(currentPage);
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-surface-elevated rounded w-48"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-surface-elevated rounded-lg"></div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">Events</h1>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="hover-lift">
                <Plus className="w-4 h-4 mr-2" />
                New Event
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Event</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  placeholder="Event Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <Textarea
                  placeholder="Event Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
                <Input
                  placeholder="Venue"
                  value={formData.venue}
                  onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
                  required
                />
                <Input
                  type="number"
                  placeholder="Total Budget (KSh)"
                  value={formData.total_budget}
                  onChange={(e) => setFormData({ ...formData, total_budget: e.target.value })}
                  required
                />
                <Input
                  type="date"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  required
                />
                <Button type="submit" className="w-full">Create Event</Button>
              </form>
            </DialogContent>
          </Dialog>

          {/* Edit Dialog */}
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Event</DialogTitle>
              </DialogHeader>
              <form onSubmit={(e) => handleSubmit(e, true)} className="space-y-4">
                <Input
                  placeholder="Event Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <Textarea
                  placeholder="Event Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
                <Input
                  placeholder="Venue"
                  value={formData.venue}
                  onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
                  required
                />
                <Input
                  type="number"
                  placeholder="Total Budget (KSh)"
                  value={formData.total_budget}
                  onChange={(e) => setFormData({ ...formData, total_budget: e.target.value })}
                  required
                />
                <Input
                  type="date"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  required
                />
                <Button type="submit" className="w-full">Update Event</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {events.map((event) => (
            <Card key={event.id} className="hover-lift transition-all duration-200">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {event.name}
                  <div className="flex items-center gap-2">
                    <Badge variant={event.is_funded ? "default" : "secondary"}>
                      {event.is_funded ? "Funded" : "Pending"}
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(event)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(event.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">{event.description}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-muted-foreground">
                    <Calendar className="w-4 h-4 mr-2" />
                    {new Date(event.event_date).toLocaleDateString()}
                  </div>
                  <div className="flex items-center text-muted-foreground">
                    <MapPin className="w-4 h-4 mr-2" />
                    {event.venue}
                  </div>
                  <div className="flex items-center text-muted-foreground">
                    <DollarSign className="w-4 h-4 mr-2" />
                    KSh {event.total_budget.toLocaleString()}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{event.percentage_covered}%</span>
                  </div>
                  <div className="w-full bg-surface-elevated rounded-full h-2">
                    <div 
                      className="bg-accent h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${Math.min(event.percentage_covered, 100)}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Received: KSh {event.total_received.toLocaleString()}</span>
                    <span>Pledged: KSh {event.total_pledged.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {events.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No events yet</h3>
            <p className="text-muted-foreground">Create your first event to get started.</p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center mt-8">
            <Pagination>
              <PaginationContent>
                {currentPage > 1 && (
                  <PaginationItem>
                    <PaginationPrevious 
                      href="#" 
                      onClick={(e) => {
                        e.preventDefault();
                        setCurrentPage(currentPage - 1);
                      }}
                    />
                  </PaginationItem>
                )}
                
                {/* Page numbers */}
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  // Show first page, last page, current page, and pages around current page
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <PaginationItem key={page}>
                        <PaginationLink
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            setCurrentPage(page);
                          }}
                          isActive={page === currentPage}
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  } else if (
                    page === currentPage - 2 ||
                    page === currentPage + 2
                  ) {
                    return (
                      <PaginationItem key={page}>
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }
                  return null;
                })}

                {currentPage < totalPages && (
                  <PaginationItem>
                    <PaginationNext 
                      href="#" 
                      onClick={(e) => {
                        e.preventDefault();
                        setCurrentPage(currentPage + 1);
                      }}
                    />
                  </PaginationItem>
                )}
              </PaginationContent>
            </Pagination>
          </div>
        )}

        {/* Page info */}
        {totalCount > 0 && (
          <div className="text-center text-sm text-muted-foreground mt-4">
            Showing {((currentPage - 1) * 10) + 1}-{Math.min(currentPage * 10, totalCount)} of {totalCount} events
          </div>
        )}
      </div>
    </Layout>
  );
};