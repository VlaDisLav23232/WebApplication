from django.shortcuts import render, redirect
from fundraisings.models import Fundraising, Category
from fundraisings.forms import UpdateFundraisingForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from decimal import Decimal


def create_fundraising(request):
    all_categories = Category.objects.all()
    if request.method == "POST":
        form = UpdateFundraisingForm(request.POST, request.FILES)
        
        if form.is_valid():
            fundraising = form.save(commit=False)
            fundraising.creator = request.user
            fundraising.save()
            
            # Get single selected category
            selected_category_id = request.POST.get("selected_categories")
            if selected_category_id:
                try:
                    category = Category.objects.get(id=selected_category_id)
                    fundraising.categories.add(category)
                except Category.DoesNotExist:
                    pass
            
            return redirect('donate', pk=fundraising.pk)
        else:
            print("Форма невалідна. Помилки:", form.errors)
    else:
        form = UpdateFundraisingForm()

    return render(request, 'create_fundraising.html', {'form': form, 'categories': all_categories})
    

def update_fundraising(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    all_categories = Category.objects.all()
    current_category = fundraising.categories.first()  # Get primary category

    if request.user != fundraising.creator:
        return redirect('donate', pk=pk)

    if request.method == "POST":
        form = UpdateFundraisingForm(request.POST, request.FILES, instance=fundraising)
        if form.is_valid():
            updated_fundraising = form.save()
            # Don't change category on update - keeping it as is
            return redirect('donate', pk=pk)
    else:
        form = UpdateFundraisingForm(instance=fundraising)

    return render(request, 'update_fundraising.html', {
        'form': form, 
        'fundraising': fundraising, 
        'categories': all_categories,
        'current_category': current_category
    })


def delete_fundraising(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)

    if request.user != fundraising.creator:
        return HttpResponseForbidden("Ви не маєте прав для видалення цього збору.")

    if request.method == 'POST':
        fundraising.delete()
        return redirect('')

    return render(request, 'confirm_delete.html', {'fundraising': fundraising})


def donate(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    other_fundraisings = Fundraising.objects.exclude(pk=pk)
    
    # Handle donation POST request
    if request.method == 'POST' and 'donation_amount' in request.POST:
        try:
            amount = Decimal(request.POST.get('donation_amount'))
            if amount > 0:
                fundraising.add_donation(amount)
                return redirect('donate', pk=pk)
        except (ValueError, TypeError):
            # Handle invalid amount input
            pass
        
    return render(request, 'donate.html', {'fundraising': fundraising, 'other_fundraisings': other_fundraisings})


# Add a new view for AJAX donation updates
def update_donation(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        fundraising = get_object_or_404(Fundraising, pk=pk)
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount > 0:
                fundraising.add_donation(amount)
                return JsonResponse({
                    'success': True,
                    'current_sum': float(fundraising.current_sum),
                    'needed_sum': float(fundraising.needed_sum),
                    'progress_percentage': int(fundraising.progress_percentage)  # Will be integer now
                })
        except (ValueError, TypeError):
            pass
            
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
