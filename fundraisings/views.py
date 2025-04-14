from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from fundraisings.models import Fundraising, Donation
from core.authentication.models import CustomUser

@login_required(login_url='/login/')
def donate(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    
    if request.method == 'POST' and request.user.is_authenticated:
        amount = request.POST.get('donation_amount')
        if amount and float(amount) > 0:
            # Create the donation
            donation = Donation.objects.create(
                fundraising=fundraising,
                user=request.user,
                amount=float(amount),
                message=request.POST.get('message', ''),
                anonymous=request.POST.get('anonymous', False) == 'on'
            )
            
            # Update user statistics
            update_user_statistics(request.user)
            update_user_statistics(fundraising.creator)
            
            messages.success(request, 'Ваш донат було успішно здійснено!')
            return redirect('donate', pk=fundraising.pk)
    
    donations = Donation.objects.filter(fundraising=fundraising).order_by('-date')
    other_fundraisings = Fundraising.objects.exclude(pk=pk).order_by('-start_date')[:3]
    
    context = {
        'fundraising': fundraising,
        'donations': donations,
        'other_fundraisings': other_fundraisings,
    }
    return render(request, 'donate.html', context)

def update_user_statistics(user):
    user_donations = Donation.objects.filter(user=user)
    total_donated = sum(donation.amount for donation in user_donations)
    user.total_donated = total_donated
    user.save()