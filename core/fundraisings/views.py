from django.shortcuts import render, redirect
from fundraisings.models import Fundraising, Category
from fundraisings.forms import UpdateFundraisingForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def create_fundraising(request):
    all_categories = Category.objects.all()
    if request.method == "POST":
        form = UpdateFundraisingForm(request.POST, request.FILES)
        
        if form.is_valid():
            fundraising = form.save(commit=False)
            fundraising.creator = request.user
            fundraising.save()
            
            selected_categories = request.POST.getlist("selected_categories")
            for cat_id in selected_categories:
                try:
                    category = Category.objects.get(id=cat_id)
                    fundraising.categories.add(category)
                except Category.DoesNotExist:
                    pass
            
            new_category_names = request.POST.getlist("new_category_names[]")
            for name in new_category_names:
                if name.strip():
                    new_category = Category.objects.create(name=name.strip())
                    fundraising.categories.add(new_category)
            
            return redirect('donate', pk=fundraising.pk)
        else:
            print("Форма невалідна. Помилки:", form.errors)
    else:
        form = UpdateFundraisingForm()

    return render(request, 'create_fundraising.html', {'form': form, 'categories': all_categories})
    


def update_fundraising(request, pk):
    fundraising = get_object_or_404(Fundraising, pk=pk)
    all_categories = Category.objects.all()

    if request.user != fundraising.creator:
        return redirect('donate', pk=pk)

    if request.method == "POST":
        form = UpdateFundraisingForm(request.POST, request.FILES, instance=fundraising)
        if form.is_valid():
            form.save()
            return redirect('donate', pk=pk)
    else:
        form = UpdateFundraisingForm(instance=fundraising)

    return render(request, 'update_fundraising.html', {'form': form, 'fundraising': fundraising, 'categories': all_categories})


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
    return render(request, 'donate.html', {'fundraising': fundraising, 'other_fundraisings': other_fundraisings})
