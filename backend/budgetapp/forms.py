from django import forms
from .models import Pledge, Donor, Event, ManualPayment, MpesaPayment

class PledgeAdminForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)

    class Meta:
        model = Pledge
        fields = ['name', 'phone', 'amount_pledged', 'event', 'is_fulfilled']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.donor:
            self.fields['name'].initial = self.instance.donor.name
            self.fields['phone'].initial = self.instance.donor.phone_number

    def save(self, commit=True):
        name = self.cleaned_data['name']
        phone = self.cleaned_data['phone']

        donor, created = Donor.objects.get_or_create(
            name=name,
            phone_number=phone
        )

        self.instance.donor = donor
        return super().save(commit=commit)


class ManualPaymentAdminForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    class Meta:
        model = ManualPayment
        fields = ['name', 'phone', 'amount', 'pledge']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.pledge.donor:
            self.fields['name'].initial = self.instance.pledge.donor.name
            self.fields['phone'].initial = self.instance.pledge.donor.phone_number
            
    def save(self, commit=True):
        name = self.cleaned_data['name']
        phone = self.cleaned_data['phone']

        donor, created = Donor.objects.get_or_create(
            name=name,
            phone_number=phone
        )

        self.instance.pledge.donor = donor
        return super().save(commit=commit)