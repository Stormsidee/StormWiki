from django import forms
from .models import Article, Tag

class ArticleForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label='Теги',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python, django, web, programming'
        }),
        help_text='Введите теги через запятую'
    )
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Начните писать свою статью здесь...'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = self.instance.get_tags_list()
    
    def clean_tags_input(self):
        tags_str = self.cleaned_data.get('tags_input', '')
        if not tags_str:
            return []
        
        tag_names = [name.strip().lower() for name in tags_str.split(',') if name.strip()]
        tag_names = list(set(tag_names))
        
        tags = []
        for name in tag_names:
            if len(name) > 50:
                raise forms.ValidationError(f'Тег "{name}" слишком длинный')
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        
        return tags
    
    def save(self, commit=True):
        article = super().save(commit=False)
        
        if commit:
            article.save()
            if 'tags_input' in self.cleaned_data:
                article.tags.set(self.cleaned_data['tags_input'])
        
        return article