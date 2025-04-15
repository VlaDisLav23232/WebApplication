from django.shortcuts import render, redirect, get_object_or_404
from fundraisings.models import Fundraising, Category, Donation, Achievement
from fundraisings.forms import UpdateFundraisingForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
                        
                        # Check for achievements
                        if request.user.is_authenticated:
                            Achievement.check_achievements(request.user)
                            # Also check achievements for the fundraising creator
                            Achievement.check_achievements(fundraising.creator)
                        
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


def fundraisings(request):
    # Get all fundraisings, ordered by creation date (newest first) by default
    fundraisings_list = Fundraising.objects.all().order_by('-created_at')
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    # Get filter parameters from the request
    sort_option = request.GET.get('sort', 'newest')
    category_filter = request.GET.get('category', '')
    
    # Apply category filter if specified
    if category_filter:
        fundraisings_list = fundraisings_list.filter(
            Q(primary_category__name=category_filter) | 
            Q(categories__name=category_filter)
        ).distinct()
    
    # Apply sorting
    if sort_option == 'newest':
        fundraisings_list = fundraisings_list.order_by('-created_at')
    elif sort_option == 'oldest':
        fundraisings_list = fundraisings_list.order_by('created_at')  # Сортування за датою створення (найстаріші спочатку)
    elif sort_option == 'ending-soon':
        # Сортуємо за датою завершення (найближчі дати спочатку)
        fundraisings_list = fundraisings_list.order_by('end_date')
    elif sort_option == 'completion':
        # Sort by percentage of completion (current_sum/needed_sum ratio)
        fundraisings_list = sorted(
            fundraisings_list,
            key=lambda f: f.progress_percentage,
            reverse=True
        )
    elif sort_option == 'popular':
        # Sort by number of donations (we assume more donations = more popular)
        fundraisings_list = fundraisings_list.annotate(
            donation_count=Count('donations')
        ).order_by('-donation_count')
    
    # Пагінація: 12 зборів на сторінку
    paginator = Paginator(fundraisings_list, 12)
    page = request.GET.get('page')
    
    try:
        fundraisings_page = paginator.page(page)
    except PageNotAnInteger:
        # Якщо page не є цілим числом, показуємо першу сторінку
        fundraisings_page = paginator.page(1)
    except EmptyPage:
        # Якщо page більше максимального, показуємо останню сторінку
        fundraisings_page = paginator.page(paginator.num_pages)
    
    # Створюємо діапазон сторінок для відображення
    # Показуємо максимум 5 сторінок навколо поточної
    current_page = fundraisings_page.number
    total_pages = paginator.num_pages
    
    # Початкове значення для діапазону сторінок
    page_range = list(range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)))
    
    # Додаємо "..." якщо потрібно
    if page_range[0] > 1:
        page_range.insert(0, '...')
        page_range.insert(0, 1)
    if page_range[-1] < total_pages:
        page_range.append('...')
        page_range.append(total_pages)
    
    context = {
        'fundraisings': fundraisings_page,
        'categories': categories,
        'selected_sort': sort_option,
        'selected_category': category_filter,
        'page_range': page_range,
        'total_pages': total_pages,
    }
    
    return render(request, 'fundraisings.html', context)


def update_donation(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            donation = get_object_or_404(Donation, pk=pk)
            
            # Check if user has permission to update
            if request.user != donation.user and request.user != donation.fundraising.creator:
                return JsonResponse({'success': False, 'error': 'Permission denied'})
                
            # Get updated values
            amount = request.POST.get('amount')
            message = request.POST.get('message')
            anonymous = request.POST.get('anonymous') == 'true'
            
            # Update fields
            if amount:
                # Calculate difference to adjust fundraising total
                difference = Decimal(amount) - donation.amount
                donation.amount = Decimal(amount)
                
                # Update the fundraising total
                fundraising = donation.fundraising
                result = fundraising.add_donation(difference)
            
            if message is not None:
                donation.message = message
                
            donation.anonymous = anonymous
            donation.save()
            
            return JsonResponse({
                'success': True,
                'current_sum': str(donation.fundraising.current_sum),
                'progress_percentage': donation.fundraising.progress_percentage
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def donation_form(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    
    if request.method == 'POST':
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
                        
                        # Check and update achievements if user is authenticated
                        if request.user.is_authenticated:
                            Achievement.check_achievements(request.user)
                            # Also check achievements for the fundraising creator
                            Achievement.check_achievements(fundraising.creator)
                        
                        messages.success(request, 'Ваш донат було успішно здійснено! Дякуємо за підтримку!')
                    except ValueError:
                        messages.error(request, 'Будь ласка, введіть коректну суму.')
                else:
                    messages.error(request, 'Сума донату не може бути порожньою.')
        except Exception as e:
            messages.error(request, f'Помилка при створенні донату: {str(e)}')
        
        return redirect('donate', pk=fundraising.pk)
    
    context = {
        'fundraising': fundraising,
    }
    return render(request, 'donation.html', context)
