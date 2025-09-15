import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Users, Phone, Mail, DollarSign } from 'lucide-react';
import { budgetAPI, serviceProvidersAPI, vendorPaymentsAPI } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatErrorForToast } from '@/lib/error-utils';

interface ServiceProvider {
  id: number;
  budget_item: number;
  service_type: string;
  name: string;
  phone_number: string;
  email: string;
  amount_charged: number;
  total_received: number;
  balance_due: number;
}

interface VendorPayment {
  id: number;
  budget_item: number;
  service_provider: number;
  payment_method: string;
  transaction_code: string;
  amount: number;
  confirmed: boolean;
  date_paid: string;
}

interface BudgetItem {
  id: number;
  category: string;
  event: number;
}

export const Vendors = () => {
  const [serviceProviders, setServiceProviders] = useState<ServiceProvider[]>([]);
  const [vendorPayments, setVendorPayments] = useState<VendorPayment[]>([]);
  const [budgetItems, setBudgetItems] = useState<BudgetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [providerFormData, setProviderFormData] = useState({
    budget_item: '',
    service_type: '',
    name: '',
    phone_number: '',
    email: '',
    amount_charged: ''
  });
  const [paymentFormData, setPaymentFormData] = useState({
    budget_item: '',
    service_provider: '',
    payment_method: '',
    transaction_code: '',
    amount: '',
    confirmed: false
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [budgetResponse, providersResponse, paymentsResponse] = await Promise.all([
        budgetAPI.list(),
        serviceProvidersAPI.list(),
        vendorPaymentsAPI.list()
      ]);
      setBudgetItems(budgetResponse.data?.results || budgetResponse.data || []);
      setServiceProviders(providersResponse.data?.results || providersResponse.data || []);
      setVendorPayments(paymentsResponse.data?.results || paymentsResponse.data || []);
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

  const handleProviderSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await serviceProvidersAPI.create({
        ...providerFormData,
        budget_item: parseInt(providerFormData.budget_item),
        amount_charged: parseFloat(providerFormData.amount_charged)
      });
      toast({
        title: "Success",
        description: "Service provider created successfully",
      });
      setProviderDialogOpen(false);
      setProviderFormData({
        budget_item: '',
        service_type: '',
        name: '',
        phone_number: '',
        email: '',
        amount_charged: ''
      });
      fetchData();
    } catch (error) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
    }
  };

  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await vendorPaymentsAPI.create({
        ...paymentFormData,
        budget_item: parseInt(paymentFormData.budget_item),
        service_provider: parseInt(paymentFormData.service_provider),
        amount: parseFloat(paymentFormData.amount)
      });
      toast({
        title: "Success",
        description: "Vendor payment recorded successfully",
      });
      setPaymentDialogOpen(false);
      setPaymentFormData({
        budget_item: '',
        service_provider: '',
        payment_method: '',
        transaction_code: '',
        amount: '',
        confirmed: false
      });
      fetchData();
    } catch (error) {
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
          <h1 className="text-3xl font-bold text-foreground">Vendors & Service Providers</h1>
          <div className="flex gap-2">
            <Dialog open={providerDialogOpen} onOpenChange={setProviderDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="hover-lift">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Provider
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Service Provider</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleProviderSubmit} className="space-y-4">
                  <Select value={providerFormData.budget_item} onValueChange={(value) => setProviderFormData({ ...providerFormData, budget_item: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Budget Item" />
                    </SelectTrigger>
                    <SelectContent>
                      {budgetItems.map((item) => (
                        <SelectItem key={item.id} value={item.id.toString()}>
                          {item.category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Service Type"
                    value={providerFormData.service_type}
                    onChange={(e) => setProviderFormData({ ...providerFormData, service_type: e.target.value })}
                    required
                  />
                  <Input
                    placeholder="Provider Name"
                    value={providerFormData.name}
                    onChange={(e) => setProviderFormData({ ...providerFormData, name: e.target.value })}
                    required
                  />
                  <Input
                    placeholder="Phone Number"
                    value={providerFormData.phone_number}
                    onChange={(e) => setProviderFormData({ ...providerFormData, phone_number: e.target.value })}
                    required
                  />
                  <Input
                    type="email"
                    placeholder="Email"
                    value={providerFormData.email}
                    onChange={(e) => setProviderFormData({ ...providerFormData, email: e.target.value })}
                  />
                  <Input
                    type="number"
                    placeholder="Amount Charged (KSh)"
                    value={providerFormData.amount_charged}
                    onChange={(e) => setProviderFormData({ ...providerFormData, amount_charged: e.target.value })}
                    required
                  />
                  <Button type="submit" className="w-full">Add Provider</Button>
                </form>
              </DialogContent>
            </Dialog>
            
            <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
              <DialogTrigger asChild>
                <Button className="hover-lift">
                  <Plus className="w-4 h-4 mr-2" />
                  Record Payment
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Record Vendor Payment</DialogTitle>
                </DialogHeader>
                <form onSubmit={handlePaymentSubmit} className="space-y-4">
                  <Select value={paymentFormData.budget_item} onValueChange={(value) => setPaymentFormData({ ...paymentFormData, budget_item: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Budget Item" />
                    </SelectTrigger>
                    <SelectContent>
                      {budgetItems.map((item) => (
                        <SelectItem key={item.id} value={item.id.toString()}>
                          {item.category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select 
                    value={paymentFormData.service_provider} 
                    onValueChange={(value) => setPaymentFormData({ ...paymentFormData, service_provider: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Service Provider" />
                    </SelectTrigger>
                    <SelectContent>
                      {serviceProviders
                        .filter(provider => !paymentFormData.budget_item || provider.budget_item.toString() === paymentFormData.budget_item)
                        .map((provider) => (
                        <SelectItem key={provider.id} value={provider.id.toString()}>
                          {provider.name} ({provider.service_type})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={paymentFormData.payment_method} onValueChange={(value) => setPaymentFormData({ ...paymentFormData, payment_method: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Payment Method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="mpesa">M-Pesa</SelectItem>
                      <SelectItem value="bank">Bank Transfer</SelectItem>
                      <SelectItem value="cash">Cash</SelectItem>
                      <SelectItem value="cheque">Cheque</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Transaction Code"
                    value={paymentFormData.transaction_code}
                    onChange={(e) => setPaymentFormData({ ...paymentFormData, transaction_code: e.target.value })}
                  />
                  <Input
                    type="number"
                    placeholder="Amount (KSh)"
                    value={paymentFormData.amount}
                    onChange={(e) => setPaymentFormData({ ...paymentFormData, amount: e.target.value })}
                    required
                  />
                  <Button type="submit" className="w-full">Record Payment</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <Tabs defaultValue="providers" className="space-y-4">
          <TabsList>
            <TabsTrigger value="providers">Service Providers</TabsTrigger>
            <TabsTrigger value="payments">Payments</TabsTrigger>
          </TabsList>

          <TabsContent value="providers" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {serviceProviders.map((provider) => (
                <Card key={provider.id} className="hover-lift transition-all duration-200">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <Users className="w-4 h-4 mr-2" />
                        {provider.name}
                      </span>
                      <Badge variant={provider.balance_due === 0 ? "default" : "secondary"}>
                        {provider.balance_due === 0 ? "Paid" : "Pending"}
                      </Badge>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{provider.service_type}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center text-muted-foreground">
                        <Phone className="w-4 h-4 mr-2" />
                        {provider.phone_number}
                      </div>
                      {provider.email && (
                        <div className="flex items-center text-muted-foreground">
                          <Mail className="w-4 h-4 mr-2" />
                          {provider.email}
                        </div>
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Charged</span>
                        <span className="font-medium">KSh {provider.amount_charged.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Received</span>
                        <span className="font-medium">KSh {provider.total_received.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Balance Due</span>
                        <span className={`font-medium ${provider.balance_due > 0 ? 'text-destructive' : 'text-success'}`}>
                          KSh {provider.balance_due.toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Payment Progress</span>
                        <span>{((provider.total_received / provider.amount_charged) * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-surface-elevated rounded-full h-2">
                        <div 
                          className="bg-accent h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${Math.min((provider.total_received / provider.amount_charged) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {serviceProviders.length === 0 && (
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No service providers yet</h3>
                <p className="text-muted-foreground">Add your first service provider to get started.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="payments" className="space-y-4">
            <div className="grid gap-4">
              {vendorPayments.map((payment) => (
                <Card key={payment.id} className="hover-lift transition-all duration-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <DollarSign className="w-4 h-4 text-accent" />
                          <span className="font-medium">KSh {payment.amount.toLocaleString()}</span>
                          <Badge variant={payment.confirmed ? "default" : "secondary"}>
                            {payment.confirmed ? "Confirmed" : "Pending"}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {payment.payment_method} • {payment.transaction_code}
                        </p>
                      </div>
                      <div className="text-right text-sm text-muted-foreground">
                        {new Date(payment.date_paid).toLocaleDateString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {vendorPayments.length === 0 && (
              <div className="text-center py-12">
                <DollarSign className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No payments recorded yet</h3>
                <p className="text-muted-foreground">Record your first vendor payment to get started.</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};