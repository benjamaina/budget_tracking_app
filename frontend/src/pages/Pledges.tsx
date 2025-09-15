import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, HandHeart, Phone, User, Trash2, DollarSign, CreditCard } from 'lucide-react';
import { pledgesAPI, eventsAPI, manualPaymentsAPI, mpesaPaymentsAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatErrorForToast } from '@/lib/error-utils';

interface Pledge {
  id: number;
  event: number;
  amount_pledged: number;
  is_fulfilled: boolean;
  name: string;
  phone_number: string;
  total_paid: number;
  balance: number;
}

interface Event {
  id: number;
  name: string;
}

interface ManualPayment {
  id: number;
  event: number;
  pledge: number;
  amount: number;
  date: string;
  user: number;
  phone_number: string;
  name: string;
}

interface MpesaPayment {
  id: number;
  event: number;
  pledge: number;
  amount: number;
  transaction_id: string;
  timestamp: string;
  user: number;
}

export const Pledges = () => {
  const [pledges, setPledges] = useState<Pledge[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [manualPayments, setManualPayments] = useState<ManualPayment[]>([]);
  const [mpesaPayments, setMpesaPayments] = useState<MpesaPayment[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [manualPaymentDialogOpen, setManualPaymentDialogOpen] = useState(false);
  const [mpesaPaymentDialogOpen, setMpesaPaymentDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    event: '',
    name: '',
    phone_number: '',
    amount_pledged: ''
  });
  const [manualPaymentFormData, setManualPaymentFormData] = useState({
    event: '',
    pledge: '',
    amount: ''
  });
  const [mpesaPaymentFormData, setMpesaPaymentFormData] = useState({
    event: '',
    pledge: '',
    amount: '',
    transaction_id: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [pledgesResponse, eventsResponse] = await Promise.all([
        pledgesAPI.list(),
        eventsAPI.list()
      ]);
      
      const pledgesData = pledgesResponse.data?.results || pledgesResponse.data || [];
      const eventsData = eventsResponse.data?.results || eventsResponse.data || [];
      
      console.log('Fetched pledges and events:', {
        pledges: pledgesData,
        events: eventsData
      });
      
      setPledges(pledgesData);
      setEvents(eventsData);
      
      // Fetch payments
      try {
        const [manualPaymentsResponse, mpesaPaymentsResponse] = await Promise.all([
          manualPaymentsAPI.list(),
          mpesaPaymentsAPI.list()
        ]);
        const manualData = manualPaymentsResponse.data?.results || manualPaymentsResponse.data || [];
        const mpesaData = mpesaPaymentsResponse.data?.results || mpesaPaymentsResponse.data || [];
        
        console.log('Fetched payments:', {
          manual: manualData,
          mpesa: mpesaData
        });
        setManualPayments(manualData);
        setMpesaPayments(mpesaData);
      } catch (error) {
        console.log('Payment fetch failed:', error);
        setManualPayments([]);
        setMpesaPayments([]);
      }
    } catch (error) {
      console.error('Fetch data error:', error);
      toast({
        title: "Error",
        description: "Failed to fetch data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await pledgesAPI.create({
        ...formData,
        event: parseInt(formData.event),
        amount_pledged: parseFloat(formData.amount_pledged)
      });
      toast({
        title: "Success",
        description: "Pledge created successfully",
      });
      setDialogOpen(false);
      setFormData({ event: '', name: '', phone_number: '', amount_pledged: '' });
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

  const handleManualPaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log('Submitting manual payment:', manualPaymentFormData);
      const response = await manualPaymentsAPI.create(manualPaymentFormData.pledge, {
        event: parseInt(manualPaymentFormData.event),
        amount: parseFloat(manualPaymentFormData.amount)
      });
      console.log('Manual payment created successfully:', response.data);
      toast({
        title: "Success",
        description: "Manual payment recorded successfully",
      });
      setManualPaymentDialogOpen(false);
      setManualPaymentFormData({ event: '', pledge: '', amount: '' });
      await fetchData();
    } catch (error: any) {
      console.error('Manual payment submit error:', error);
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleMpesaPaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log('Submitting mpesa payment:', mpesaPaymentFormData);
      const response = await mpesaPaymentsAPI.create({
        event: parseInt(mpesaPaymentFormData.event),
        pledge: parseInt(mpesaPaymentFormData.pledge),
        amount: parseFloat(mpesaPaymentFormData.amount),
        transaction_id: mpesaPaymentFormData.transaction_id
      });
      console.log('Mpesa payment created successfully:', response.data);
      toast({
        title: "Success",
        description: "Mpesa payment recorded successfully",
      });
      setMpesaPaymentDialogOpen(false);
      setMpesaPaymentFormData({ event: '', pledge: '', amount: '', transaction_id: '' });
      await fetchData();
    } catch (error: any) {
      console.error('Mpesa payment submit error:', error);
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this pledge?')) return;
    
    try {
      await pledgesAPI.delete(id.toString());
      toast({
        title: "Success",
        description: "Pledge deleted successfully",
      });
      fetchData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          "Failed to delete pledge";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const getEventName = (eventId: number) => {
    const event = events.find(e => e.id === eventId);
    return event ? event.name : 'Unknown Event';
  };

  const getPledgeName = (pledgeId: number) => {
    const pledge = pledges.find(p => p.id === pledgeId);
    return pledge ? pledge.name : 'Unknown Pledger';
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
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">Pledge Management</h1>
          <div className="flex gap-2">
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button className="hover-lift">
                  <Plus className="w-4 h-4 mr-2" />
                  New Pledge
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Pledge</DialogTitle>
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
                    placeholder="Donor Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                  <Input
                    placeholder="Phone Number"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    required
                  />
                  <Input
                    type="number"
                    placeholder="Pledge Amount (KSh)"
                    value={formData.amount_pledged}
                    onChange={(e) => setFormData({ ...formData, amount_pledged: e.target.value })}
                    required
                  />
                  <Button type="submit" className="w-full">Create Pledge</Button>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog open={manualPaymentDialogOpen} onOpenChange={setManualPaymentDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="hover-lift">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Manual Payment
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Record Manual Payment</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleManualPaymentSubmit} className="space-y-4">
                  <Select value={manualPaymentFormData.event} onValueChange={(value) => setManualPaymentFormData({ ...manualPaymentFormData, event: value })}>
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
                  <Select value={manualPaymentFormData.pledge} onValueChange={(value) => setManualPaymentFormData({ ...manualPaymentFormData, pledge: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Pledge" />
                    </SelectTrigger>
                    <SelectContent>
                      {pledges.filter(p => !manualPaymentFormData.event || p.event.toString() === manualPaymentFormData.event).map((pledge) => (
                        <SelectItem key={pledge.id} value={pledge.id.toString()}>
                          {pledge.name} - {getEventName(pledge.event)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    type="number"
                    placeholder="Payment Amount (KSh)"
                    value={manualPaymentFormData.amount}
                    onChange={(e) => setManualPaymentFormData({ ...manualPaymentFormData, amount: e.target.value })}
                    required
                  />
                  <Button type="submit" className="w-full">Record Manual Payment</Button>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog open={mpesaPaymentDialogOpen} onOpenChange={setMpesaPaymentDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="hover-lift">
                  <CreditCard className="w-4 h-4 mr-2" />
                  Mpesa Payment
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Record Mpesa Payment</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleMpesaPaymentSubmit} className="space-y-4">
                  <Select value={mpesaPaymentFormData.event} onValueChange={(value) => setMpesaPaymentFormData({ ...mpesaPaymentFormData, event: value })}>
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
                  <Select value={mpesaPaymentFormData.pledge} onValueChange={(value) => setMpesaPaymentFormData({ ...mpesaPaymentFormData, pledge: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Pledge" />
                    </SelectTrigger>
                    <SelectContent>
                      {pledges.filter(p => !mpesaPaymentFormData.event || p.event.toString() === mpesaPaymentFormData.event).map((pledge) => (
                        <SelectItem key={pledge.id} value={pledge.id.toString()}>
                          {pledge.name} - {getEventName(pledge.event)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    type="number"
                    placeholder="Payment Amount (KSh)"
                    value={mpesaPaymentFormData.amount}
                    onChange={(e) => setMpesaPaymentFormData({ ...mpesaPaymentFormData, amount: e.target.value })}
                    required
                  />
                  <Input
                    placeholder="Transaction ID"
                    value={mpesaPaymentFormData.transaction_id}
                    onChange={(e) => setMpesaPaymentFormData({ ...mpesaPaymentFormData, transaction_id: e.target.value })}
                    required
                  />
                  <Button type="submit" className="w-full">Record Mpesa Payment</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <Tabs defaultValue="pledges" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="pledges">Pledges</TabsTrigger>
            <TabsTrigger value="manual-payments">Manual Payments</TabsTrigger>
            <TabsTrigger value="mpesa-payments">Mpesa Payments</TabsTrigger>
          </TabsList>

          <TabsContent value="pledges" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {pledges.map((pledge) => (
                <Card key={pledge.id} className="hover-lift transition-all duration-200">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <User className="w-4 h-4 mr-2" />
                        {pledge.name}
                      </span>
                      <div className="flex items-center gap-2">
                        <Badge variant={pledge.is_fulfilled ? "default" : "secondary"}>
                          {pledge.is_fulfilled ? "Fulfilled" : "Pending"}
                        </Badge>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(pledge.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{getEventName(pledge.event)}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Phone className="w-4 h-4 mr-2" />
                      {pledge.phone_number}
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Pledged</span>
                        <span className="font-medium">KSh {pledge.amount_pledged.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Paid</span>
                        <span className="font-medium">KSh {pledge.total_paid.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Balance</span>
                        <span className={`font-medium ${pledge.balance > 0 ? 'text-destructive' : 'text-success'}`}>
                          KSh {pledge.balance.toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>{((pledge.total_paid / pledge.amount_pledged) * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-surface-elevated rounded-full h-2">
                        <div 
                          className="bg-accent h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${Math.min((pledge.total_paid / pledge.amount_pledged) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {pledges.length === 0 && (
              <div className="text-center py-12">
                <HandHeart className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No pledges yet</h3>
                <p className="text-muted-foreground">Create your first pledge to get started.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="manual-payments" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {manualPayments.map((payment) => (
                <Card key={payment.id} className="hover-lift transition-all duration-200">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <DollarSign className="w-4 h-4 mr-2" />
                        KSh {payment.amount.toLocaleString()}
                      </span>
                      <Badge variant="default">
                        Manual
                      </Badge>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{payment.name}</p>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Phone</span>
                      <span className="font-medium">{payment.phone_number}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Event</span>
                      <span className="font-medium">{getEventName(payment.event)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Date</span>
                      <span className="font-medium">{new Date(payment.date).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {manualPayments.length === 0 && (
              <div className="text-center py-12">
                <DollarSign className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No manual payments recorded yet</h3>
                <p className="text-muted-foreground">Record your first manual payment to get started.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="mpesa-payments" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {mpesaPayments.map((payment) => (
                <Card key={payment.id} className="hover-lift transition-all duration-200">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <CreditCard className="w-4 h-4 mr-2" />
                        KSh {payment.amount.toLocaleString()}
                      </span>
                      <Badge variant="secondary">
                        Mpesa
                      </Badge>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{getPledgeName(payment.pledge)}</p>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Transaction ID</span>
                      <span className="font-medium">{payment.transaction_id}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Event</span>
                      <span className="font-medium">{getEventName(payment.event)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Date</span>
                      <span className="font-medium">{new Date(payment.timestamp).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {mpesaPayments.length === 0 && (
              <div className="text-center py-12">
                <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No Mpesa payments recorded yet</h3>
                <p className="text-muted-foreground">Record your first Mpesa payment to get started.</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};