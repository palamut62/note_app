from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import Note, Category, Tag, Profile
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

    # Sadece notlara kayıtlı olan benzersiz etiketleri çek
    tags = Tag.objects.filter(note__user=request.user).annotate(
        num_notes=Count('note')
    ).filter(num_notes__gt=0).distinct()

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
        logger.debug(f"POST data: {request.POST}")
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            logger.debug(f"Form is valid. Cleaned data: {form.cleaned_data}")
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()
            messages.success(request, 'Not başarıyla oluşturuldu!')
            return redirect('dashboard')
        else:
            logger.error(f"Form is invalid. Errors: {form.errors}")
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
    logger.debug(f"Filtering notes for tag_id: {tag_id}")
    tag = get_object_or_404(Tag, id=tag_id)
    logger.debug(f"Tag found: {tag.name}")

    notes = Note.objects.filter(user=request.user, tags=tag).distinct()
    logger.debug(f"Number of notes found: {notes.count()}")

    notes_data = []
    for note in notes:
        logger.debug(f"Processing note: {note.id} - {note.title}")
        notes_data.append({
            'id': note.id,
            'title': note.title,
            'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
            'color': note.color,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'reminder': note.reminder.strftime('%Y-%m-%d %H:%M:%S') if note.reminder else None,
            'is_active': note.is_active,
        })

    logger.debug(f"Returning {len(notes_data)} notes")
    return JsonResponse({'notes': notes_data})


@login_required
def filter_notes_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    notes = Note.objects.filter(user=request.user, category=category)

    notes_data = [{
        'id': note.id,
        'title': note.title,
        'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
        'color': note.color,
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'reminder': note.reminder.strftime('%Y-%m-%d %H:%M:%S') if note.reminder else None,
        'is_active': note.is_active,
        'category': note.category.name
    } for note in notes]

    return JsonResponse({'notes': notes_data})

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


@login_required
def get_all_notes(request):
    notes = Note.objects.filter(user=request.user)
    notes_data = [{
        'id': note.id,
        'title': note.title,
        'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
        'color': note.color,
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'reminder': note.reminder.strftime('%Y-%m-%d %H:%M:%S') if note.reminder else None,
        'is_active': note.is_active,
        'category': note.category.name if note.category else 'Uncategorized'
    } for note in notes]

    return JsonResponse({'notes': notes_data})


@login_required
def get_note_details(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note_data = {
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'color': note.color,
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'reminder': note.reminder.strftime('%Y-%m-%d %H:%M:%S') if note.reminder else None,
        'is_active': note.is_active,
        'category': note.category.name if note.category else 'Uncategorized',
        'tags': [tag.name for tag in note.tags.all()]
    }
    return JsonResponse(note_data)







