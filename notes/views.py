from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Note, Category, Tag, Profile
from .forms import NoteForm, ProfileImageForm
import logging

logger = logging.getLogger(__name__)


@login_required
def check_reminders(request):
    current_time = timezone.now()
    due_reminders = Note.objects.filter(
        user=request.user,
        reminder__isnull=False,
        reminder__lte=current_time,
        is_active=True
    )

    reminders = []
    for note in due_reminders:
        reminders.append({'id': note.id, 'title': note.title})
        note.is_active = False
        note.reminder = None
        note.save()  # Bu, modeldeki save metodunu çağıracak

    return JsonResponse({'reminders': reminders})


@login_required
def dashboard(request):
    current_time = timezone.now()

    # Geçmiş hatırlatıcıları güncelle
    past_reminders = Note.objects.filter(
        user=request.user,
        reminder__isnull=False,
        reminder__lte=current_time,
        is_active=True
    )
    for note in past_reminders:
        note.is_active = False
        note.reminder = None
        note.save()

    notes = Note.objects.filter(user=request.user).select_related('category').prefetch_related('tags')
    profile_image = Profile.objects.filter(user=request.user).first()
    categories = Category.objects.filter(user=request.user)
    tags = Tag.objects.filter(user=request.user)

    active_reminders = Note.objects.filter(
        user=request.user,
        reminder__isnull=False,
        reminder__gt=current_time,
        is_active=True
    ).order_by('reminder')

    context = {
        'notes': notes,
        'categories': categories,
        'tags': tags,
        'active_reminders': active_reminders,
        'profile_image': profile_image
    }
    return render(request, 'notes/dashboard.html', context)





@login_required
def create_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            reminder = form.cleaned_data.get('reminder')
            if reminder and reminder <= timezone.now():
                messages.error(request, 'Hatırlatıcı tarihi geçmiş bir tarih olamaz.')
                return render(request, 'notes/note_form.html', {'form': form, 'action': 'Create'})
            note.user = request.user
            note.save()
            form.save_m2m()  # Save many-to-many fields
            messages.success(request, 'Not başarıyla oluşturuldu!')
            return redirect('dashboard')
    else:
        form = NoteForm(user=request.user)
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Create'})


@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Not başarıyla güncellendi!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Edit'})



@login_required
@require_POST
def add_category(request):
    name = request.POST.get('name')
    if name:
        category = Category.objects.create(name=name, user=request.user)
        return JsonResponse({'id': category.id, 'name': category.name})
    return JsonResponse({'error': 'Geçersiz kategori adı'}, status=400)

@login_required
@require_POST
def delete_note(request, pk):
    try:
        note = get_object_or_404(Note, pk=pk, user=request.user)
        note.delete()
        return JsonResponse({'success': True})
    except Note.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def delete_category(request, pk):
    try:
        category = get_object_or_404(Category, pk=pk, user=request.user)
        category.delete()
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Kategori bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def filter_notes_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id, user=request.user)
    notes = Note.objects.filter(user=request.user, tags=tag)
    return JsonResponse({'notes': list(notes.values())})

@login_required
def filter_notes_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id, user=request.user)
    notes = Note.objects.filter(user=request.user, category=category)
    return JsonResponse({'notes': list(notes.values())})

@require_POST
def add_tag(request):
    name = request.POST.get('name')
    if name:
        tag, created = Tag.objects.get_or_create(name=name, user=request.user)
        return JsonResponse({'id': tag.id, 'name': tag.name})
    return JsonResponse({'error': 'Invalid tag name'}, status=400)


from django.http import JsonResponse

@login_required
def update_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            return JsonResponse({
                'success': True,
                'image_url': profile.profile_image.url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': form.errors
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})







