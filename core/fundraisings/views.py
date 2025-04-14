from django.shortcuts import render, redirect, get_object_or_404
from fundraisings.models import Fundraising, Category, Donation
from fundraisings.forms import UpdateFundraisingForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.db import transaction


def create_fundraising(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        needed_sum = request.POST.get('needed_sum')
        end_date = request.POST.get('end_date')
        link_for_money = request.POST.get('link_for_money')
        main_image = request.FILES.get('main_image')
        confirm_reporting = request.POST.get('confirm_reporting') == 'on'
        
        # Simplified category handling
        primary_category_id = request.POST.get('primary_category')
        
        try:
            # Try to get the selected category or use default
            if primary_category_id:
                primary_category = Category.objects.get(id=primary_category_id)
            else:
                # Get a default category without creating during initialization
                primary_category = Category.get_default_category()
                
        except Category.DoesNotExist:
            # If selected category doesn't exist, use default
            primary_category = Category.get_default_category()

        # Create the fundraising object
        fundraising = Fundraising.objects.create(
            title=title,
            description=description,
            creator=request.user,
            needed_sum=needed_sum,
            end_date=end_date,
            link_for_money=link_for_money,
            main_image=main_image,
            confirm_reporting=confirm_reporting,
            primary_category=primary_category
        )
        
        # Add to categories M2M relationship
        fundraising.categories.add(primary_category)
        
        messages.success(request, 'Збір успішно створено!')
        return redirect('donate', pk=fundraising.pk)
    else:
        # Get existing categories, rather than creating defaults
        categories = Category.objects.all()
        return render(request, 'create_fundraising.html', {'categories': categories})
    

def update_fundraising(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    
    # Get existing categories without creating them
    all_categories = Category.objects.all()
    current_category = fundraising.categories.first() or Category.get_default_category()

    if request.user != fundraising.creator:
        return redirect('donate', pk=pk)

    if request.method == "POST":
        form = UpdateFundraisingForm(request.POST, request.FILES, instance=fundraising)
        if form.is_valid():
            updated_fundraising = form.save()
            return redirect('donate', pk=pk)
    else:
        form = UpdateFundraisingForm(instance=fundraising)

    today = timezone.now().date()
    
    return render(request, 'update_fundraising.html', {
        'form': form, 
        'fundraising': fundraising, 
        'categories': all_categories,
        'current_category': current_category,
        'today': today
    })


def delete_fundraising(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)

    if request.user != fundraising.creator:
        return HttpResponseForbidden("Ви не маєте прав для видалення цього збору.")

    if request.method == 'POST':
        fundraising.delete()
        return redirect('fundraisings')

    return render(request, 'confirm_delete.html', {'fundraising': fundraising})


def donate(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                amount = Decimal(request.POST.get('amount', 0))
                result = fundraising.add_donation(amount)
                return JsonResponse({
                    'success': True,
                    'current_sum': str(result['current_sum']),
                    'progress_percentage': result['progress_percentage']
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        try:
            with transaction.atomic():
                amount = request.POST.get('donation_amount')
                
                if amount:
                    try:
                        amount_decimal = Decimal(amount)
                        
                        donation = Donation.objects.create(
                            fundraising=fundraising,
                            user=request.user if request.user.is_authenticated else None,
                            amount=amount_decimal,
                            message=request.POST.get('message', ''),
                            anonymous=request.POST.get('anonymous', False) == 'on'
                        )
                        
                        messages.success(request, 'Ваш донат було успішно здійснено!')
                    except ValueError:
                        messages.error(request, 'Будь ласка, введіть коректну суму.')
                else:
                    messages.error(request, 'Сума донату не може бути порожньою.')
        except Exception as e:
            messages.error(request, f'Помилка при створенні донату: {str(e)}')
        
        return redirect('donate', pk=fundraising.pk)
    
    donations = Donation.objects.filter(fundraising=fundraising).order_by('-date')
    
    # First get other users' fundraisings, then the current user's fundraisings
    from django.db.models import Case, When, Value, IntegerField
    
    other_fundraisings = Fundraising.objects.exclude(pk=fundraising.pk).annotate(
        creator_priority=Case(
            When(creator=request.user, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('creator_priority', '?')
    
    context = {
        'fundraising': fundraising,
        'donations': donations,
        'other_fundraisings': other_fundraisings,
    }
    return render(request, 'donate.html', context)
