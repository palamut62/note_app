from django import forms
from django.utils import timezone
from .models import Note, Tag


class NoteForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'data-role': 'tagsinput'}))
    reminder_active = forms.BooleanField(required=False, label="Hatırlatıcıyı Etkinleştir")
    reminder = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    created_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'color', 'category', 'tags', 'reminder_active', 'reminder', 'created_at']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
            if self.instance.reminder:
                self.fields['reminder'].initial = self.instance.reminder.strftime('%Y-%m-%dT%H:%M')
                self.fields['reminder_active'].initial = True
            self.fields['created_at'].initial = self.instance.created_at.strftime('%Y-%m-%dT%H:%M')
        else:
            self.fields['created_at'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        reminder_active = cleaned_data.get('reminder_active')
        reminder = cleaned_data.get('reminder')
        created_at = cleaned_data.get('created_at')

        if reminder_active and not reminder:
            self.add_error('reminder', "Hatırlatıcı etkinleştirildiğinde bir tarih seçmelisiniz.")
        elif reminder_active and reminder and reminder < timezone.now():
            self.add_error('reminder', "Hatırlatıcı geçmiş bir tarih olamaz.")

        if created_at and created_at > timezone.now():
            self.add_error('created_at', "Oluşturma tarihi gelecekte bir tarih olamaz.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user

        if not self.cleaned_data.get('reminder_active'):
            instance.reminder = None

        if commit:
            instance.save()

            # Tags'i kaydetme işlemini buraya taşıdık
            if 'tags' in self.cleaned_data:
                instance.tags.clear()
                tag_names = [t.strip() for t in self.cleaned_data['tags'].split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={'user': self.user})
                    instance.tags.add(tag)

        return instance

from django import forms
from .models import Profile

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']
