# ...existing code...

def profile_page(request, user_id=None):
    profile_user = get_object_or_404(User, id=user_id) if user_id else request.user
    is_own_profile = profile_user == request.user

    # Split fundraisings into active and closed (with reports)
    user_fundraisings = Fundraising.objects.filter(creator=profile_user).order_by('-created_at')
    active_fundraisings = [f for f in user_fundraisings if not f.has_report]
    closed_fundraisings = [f for f in user_fundraisings if f.has_report]
    
    all_active_have_reports = user_fundraisings.exists() and len(active_fundraisings) == 0

    # Additional context variables
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_fundraisings': active_fundraisings,
        'closed_fundraisings': closed_fundraisings,
        'all_active_have_reports': all_active_have_reports,
        'user_donations': Donation.objects.filter(user=profile_user).order_by('-date'),
        'user_achievements': Achievement.objects.filter(user=profile_user).order_by('-date_earned'),
    }
    
    return render(request, 'profile_page.html', context)

# ...existing code...