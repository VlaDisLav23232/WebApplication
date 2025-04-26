from django.shortcuts import render, redirect, get_object_or_404
from fundraisings.models import Fundraising, Category, Donation, Achievement, Report, ReportImage, ReportVideo
from fundraisings.forms import UpdateFundraisingForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.db import transaction, connection
from django.db.models import Q, Sum, Count, Case, When, Value, IntegerField, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from authentication.models import CustomUser


@login_required
def create_fundraising(request):
    """
    Handle creation of new fundraisings.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        needed_sum = request.POST.get('needed_sum')
        end_date = request.POST.get('end_date')
        main_image = request.FILES.get('main_image')
        primary_category = request.POST.get('primary_category')
        confirm_terms = request.POST.get('confirm_terms')
        confirm_reporting = bool(request.POST.get('confirm_reporting'))
        # Get link_for_money from form or use default
        link_for_money = request.POST.get('link_for_money', 'https://dovir.ua/payment')
        
        # Validate required fields
        if not all([title, description, needed_sum, end_date, main_image, primary_category, confirm_terms]):
            messages.error(request, "Будь ласка, заповніть всі обов'язкові поля")
            return redirect('create_fundraising')
        
        try:
            # Create fundraising with link_for_money
            fundraising = Fundraising.objects.create(
                title=title,
                description=description,
                needed_sum=needed_sum,
                end_date=end_date,
                main_image=main_image,
                creator=request.user,
                primary_category_id=primary_category,
                confirm_reporting=confirm_reporting,
                link_for_money=link_for_money,
            )
            
            # Explicitly update user statistics after creating fundraising
            update_user_statistics(request.user)
            
            # Check for achievements
            Achievement.check_achievements(request.user)
            
            messages.success(request, 'Збір успішно створено!')
            return redirect('donate', pk=fundraising.pk)
            
        except Exception as e:
            messages.error(request, f"Помилка при створенні збору: {str(e)}")
            return redirect('create_fundraising')
    
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


@login_required
def create_report(request, fundraising_id=None):
    """
    View to create a report for a fundraising campaign.
    If fundraising_id is provided, it pre-selects that fundraising.
    """
    # If fundraising_id is provided, get the fundraising object
    fundraising = None
    if fundraising_id:
        fundraising = get_object_or_404(Fundraising, pk=fundraising_id)
        # Check if user is the creator
        if request.user != fundraising.creator:
            messages.error(request, "Тільки автор збору може створити звіт.")
            return redirect('donate', pk=fundraising_id)
    
    # Get all fundraisings created by the user for the dropdown if no specific fundraising is selected
    user_fundraisings = None
    if not fundraising:
        user_fundraisings = Fundraising.objects.filter(creator=request.user)
    
    if request.method == 'POST':
        # Process the form data
        try:
            # Get fundraising ID from form or from URL parameter
            if fundraising:
                report_fundraising_id = fundraising.id
            else:
                report_fundraising_id = request.POST.get('fundraising_id')
            
            report_fundraising = get_object_or_404(Fundraising, pk=report_fundraising_id)
            
            # Create the report with an auto-generated title based on the fundraising
            report = Report.objects.create(
                fundraising=report_fundraising,
                title=f"Звіт по збору: {report_fundraising.title}",
                description=request.POST.get('description'),
                creator=request.user,
            )
            
            # Process the single image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                try:
                    report_image = ReportImage.objects.create(
                        report=report,
                        image=image
                    )
                    print(f"Created report image: {report_image}")
                except Exception as e:
                    print(f"Error creating report image: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            # Process optional video upload
            if 'video' in request.FILES and request.FILES['video']:
                video = request.FILES['video']
                
                # Validate video file format
                valid_formats = ['video/mp4', 'video/webm']
                if video.content_type in valid_formats:
                    try:
                        report_video = ReportVideo.objects.create(
                            report=report,
                            video=video
                        )
                        print(f"Created report video: {report_video}")
                    except Exception as e:
                        print(f"Error creating report video: {e}")
                        import traceback
                        print(traceback.format_exc())
                else:
                    print(f"Invalid video format: {video.content_type}")
            
            # Close the fundraising
            report_fundraising.status = 'completed'
            report_fundraising.save()
            
            # Update user statistics to reflect completed fundraising
            update_user_statistics(report_fundraising.creator)
            
            # Check for achievements related to completed fundraisings
            Achievement.check_achievements(report_fundraising.creator)
            
            messages.success(request, 'Звіт успішно створено! Збір було закрито.')
            return redirect('donate', pk=report_fundraising.pk)
            
        except Exception as e:
            # More detailed error logging
            import traceback
            print(f"Error creating report: {e}")
            print(traceback.format_exc())
            messages.error(request, f"Помилка при створенні звіту: {str(e)}")
    
    context = {
        'fundraising': fundraising,
        'fundraisings': user_fundraisings,
    }
    return render(request, 'create_report.html', context)


def donate(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    donations = Donation.objects.filter(fundraising=fundraising).order_by('-date')
    
    # Only get active fundraisings for "other fundraisings" section
    other_fundraisings = Fundraising.objects.filter(report__isnull=True).exclude(pk=pk)[:6]
    
    # Check if fundraising has a report
    fundraising.has_report = hasattr(fundraising, 'report') and fundraising.report is not None
    
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
                        
                        # Update user statistics
                        if request.user.is_authenticated:
                            update_user_statistics(request.user)
                        update_user_statistics(fundraising.creator)
                        
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
    
    context = {
        'fundraising': fundraising,
        'donations': donations,
        'other_fundraisings': other_fundraisings,
    }
    return render(request, 'donate.html', context)


def update_user_statistics(user):
    """Update user statistics related to donations"""
    try:
        # Calculate donation statistics
        from django.db.models import Sum, Count, Max
        
        # User's donations
        user_donations = Donation.objects.filter(user=user)
        total_donated = user_donations.aggregate(Sum('amount'))['amount__sum'] or 0
        largest_donation = user_donations.aggregate(Max('amount'))['amount__max'] or 0
        supported_fundraisings = user_donations.values('fundraising').distinct().count()
        
        # Update fields using setters
        user.total_donated_amount = total_donated
        user.largest_donation_amount = largest_donation
        user.supported_fundraisings_count = supported_fundraisings
        
        # Direct field updates
        user.total_donations_amount = total_donated
        user.created_fundraisings_count = Fundraising.objects.filter(creator=user).count()
        user.completed_fundraisings_count = Fundraising.objects.filter(
            creator=user, status='completed').count()
        
        # Statistics for fundraisings created by the user
        user_fundraisings = Fundraising.objects.filter(creator=user)
        donations_received = Donation.objects.filter(fundraising__in=user_fundraisings)
        user.total_received_amount = donations_received.aggregate(Sum('amount'))['amount__sum'] or 0
        user.unique_donators_count = donations_received.exclude(user=None).values('user').distinct().count()
        
        # Save changes
        user.save()
    except Exception as e:
        print(f"Error updating user statistics: {e}")


@login_required
def fundraisings(request):
    # Get filter parameters from the request
    sort_option = request.GET.get('sort', 'newest')
    selected_category = request.GET.get('category', '')
    
    # Base queryset - EXCLUDE fundraisings that have reports
    fundraisings_list = Fundraising.objects.filter(report__isnull=True)
    
    # Apply sorting
    if sort_option == 'newest':
        fundraisings_list = fundraisings_list.order_by('-created_at')
    elif sort_option == 'oldest':
        fundraisings_list = fundraisings_list.order_by('created_at')
    elif sort_option == 'ending-soon':
        fundraisings_list = fundraisings_list.order_by('end_date')
    elif sort_option == 'completion':
        # Order by completion percentage (current_sum/needed_sum ratio)
        fundraisings_list = sorted(
            fundraisings_list,
            key=lambda f: (f.current_sum / f.needed_sum if f.needed_sum > 0 else 0),
            reverse=True
        )
    
    # Apply category filter if selected
    if selected_category:
        fundraisings_list = [f for f in fundraisings_list if f.primary_category and f.primary_category.name == selected_category]

    # If sorting is done in Python (completion), we need to convert the list back to a queryset for pagination
    if sort_option == 'completion' and not selected_category:
        ids = [f.id for f in fundraisings_list]
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        fundraisings_list = Fundraising.objects.filter(id__in=ids).order_by(preserved_order)
    
    # Pagination
    paginator = Paginator(fundraisings_list, 9)  # 9 per page
    page = request.GET.get('page', 1)
    
    try:
        fundraisings_page = paginator.page(page)
    except PageNotAnInteger:
        fundraisings_page = paginator.page(1)
    except EmptyPage:
        fundraisings_page = paginator.page(paginator.num_pages)
    
    # Get all categories for the filter
    categories = Category.objects.all()
    
    # Create page range for pagination display
    page_range = get_page_range(paginator, fundraisings_page.number)
    
    context = {
        'fundraisings': fundraisings_page,
        'categories': categories,
        'selected_sort': sort_option,
        'selected_category': selected_category,
        'page_range': page_range,
    }
    
    return render(request, 'fundraisings.html', context)


@login_required
def active_fundraisings(request):
    """View to display all active fundraisings"""
    fundraisings = Fundraising.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'active_fundraisings.html', {'fundraisings': fundraisings})


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
                'progress_percentage': donation.fundraising.progress_percentage,
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


def get_page_range(paginator, current_page, margin=2):
    """
    Helper function to create a page range for pagination with ellipsis
    Ensures there are always margin pages on either side of the current page
    """
    num_pages = paginator.num_pages
    
    # If fewer than 2*margin+5 pages, show all pages
    if num_pages <= 2 * margin + 5:
        return range(1, num_pages + 1)
    
    # We always show first and last page, and margin pages around current page
    pages = []
    
    # Always include page 1
    pages.append(1)
    
    # Add ellipsis if needed
    if current_page > margin + 2:
        pages.append('...')
    
    # Add margin pages before current page
    for i in range(max(2, current_page - margin), current_page):
        pages.append(i)
    
    # Add current page if not page 1 or last page
    if current_page != 1 and current_page != num_pages:
        pages.append(current_page)
    
    # Add margin pages after current page
    for i in range(current_page + 1, min(current_page + margin + 1, num_pages)):
        pages.append(i)
    
    # Add ellipsis if needed
    if current_page < num_pages - margin - 1:
        pages.append('...')
    
    # Always include last page if not already included
    if num_pages > 1 and num_pages not in pages:
        pages.append(num_pages)
    
    return pages


@login_required
def reports(request):
    # Get all fundraisings that have a report
    fundraisings_with_reports = Fundraising.objects.filter(report__isnull=False)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    # Handle sorting
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'newest':
        fundraisings_with_reports = fundraisings_with_reports.order_by('-report__created_at')
    elif sort_option == 'oldest':
        fundraisings_with_reports = fundraisings_with_reports.order_by('report__created_at')
    
    # Handle category filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        fundraisings_with_reports = fundraisings_with_reports.filter(primary_category__name=selected_category)
    
    # Pagination
    paginator = Paginator(fundraisings_with_reports, 9)  # Show 9 cards per page
    page = request.GET.get('page', 1)
    
    try:
        paginated_fundraisings = paginator.page(page)
    except PageNotAnInteger:
        paginated_fundraisings = paginator.page(1)
    except EmptyPage:
        paginated_fundraisings = paginator.page(paginator.num_pages)
    
    # Create a range of page numbers for pagination display
    page_range = get_page_range(paginator, paginated_fundraisings.number)
    
    context = {
        'fundraisings': paginated_fundraisings,
        'categories': categories,
        'selected_sort': sort_option,
        'selected_category': selected_category,
        'page_range': page_range,
    }
    
    return render(request, 'reports.html', context)


def profile_page(request, user_id=None):
    if user_id:
        profile_user = get_object_or_404(CustomUser, id=user_id)
        is_own_profile = request.user.is_authenticated and request.user.id == profile_user.id
    else:
        if request.user.is_authenticated:
            profile_user = request.user
            is_own_profile = True
        else:
            profile_user = None
            is_own_profile = False
    
    # Split fundraisings into active and closed (with reports)
    if profile_user:
        user_fundraisings = Fundraising.objects.filter(creator=profile_user)
        
        # Separate active and closed fundraisings
        active_fundraisings = [f for f in user_fundraisings if not hasattr(f, 'report') or f.report is None]
        closed_fundraisings = [f for f in user_fundraisings if hasattr(f, 'report') and f.report is not None]
        
        all_active_have_reports = (user_fundraisings.count() > 0) and (len(active_fundraisings) == 0)
        
        # Get user donations
        user_donations = Donation.objects.filter(user=profile_user).order_by('-date')
        
        # Get user achievements
        user_achievements = Achievement.objects.filter(user=profile_user).order_by('-date_earned')
        
        # Check if all donations are anonymous
        all_anonymous = user_donations.exists() and all(donation.anonymous for donation in user_donations)
    else:
        active_fundraisings = []
        closed_fundraisings = []
        all_active_have_reports = False
        user_donations = []
        user_achievements = []
        all_anonymous = False

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_fundraisings': active_fundraisings,
        'closed_fundraisings': closed_fundraisings,
        'all_active_have_reports': all_active_have_reports,
        'user_donations': user_donations,
        'user_achievements': user_achievements,
        'all_anonymous': all_anonymous,
    }

    return render(request, 'profile_page.html', context)


def about_us(request):
    closed_fundraisings_count = Fundraising.objects.filter(status='completed').count()
    total_donated_amount = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Count users who created and closed at least one fundraising
    users_with_closed_fundraisings = Fundraising.objects.filter(
        status='completed'
    ).values('creator').distinct().count()

    # Count users who made at least one donation
    users_with_donations = Donation.objects.filter(user__isnull=False).values('user').distinct().count()

    return render(request, 'about_us.html', {
        'closed_fundraisings_count': closed_fundraisings_count,
        'total_donated_amount': total_donated_amount,
        'users_with_closed_fundraisings': users_with_closed_fundraisings,
        'users_with_donations': users_with_donations,
    })
