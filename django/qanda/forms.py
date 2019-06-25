from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField)
from django.utils.translation import gettext_lazy as _
from qanda.models import Answer, AnswerVote, Question, QuestionVote


class ColorizedErrorFormMixin(forms.ModelForm):
    error_css_class = 'is-danger'

    def is_valid(self):
        valid = super(ColorizedErrorFormMixin, self).is_valid()
        self.add_error_css_class()
        return valid

    def add_error_css_class(self):
        for field in self.errors:
            self.fields[field].widget.attrs.update(
                {'class': self.fields[field].widget.attrs.get('class', '') +
                 f' {self.error_css_class}'})


class QuestionForm(ColorizedErrorFormMixin, forms.ModelForm):
    error_css_class = 'is-danger'
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True
    )
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input', 'name': 'input-title', },), max_length=250)
    custom_tags = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'name': 'tags',
        'placeholder': 'Please add between 2 and 4 tags...'},))

    class Meta:
        model = Question
        fields = ('title', 'body', 'user')
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'textarea',
                'name': 'question-body',
                'placeholder': 'Remember, you can use markdown here...'}),
        }

    def is_valid(self):
        MIN_TAGS = 2
        MAX_TAGS = 4
        valid = super(QuestionForm, self).is_valid()
        if not valid:
            return valid

        tags = self.cleaned_data['custom_tags'].split(',')
        if len(tags) >= MIN_TAGS and len(tags) < MAX_TAGS:
            # Clean tags input
            tags = list(map(lambda x: x.strip(), tags))
            self.custom_tags = list(map(lambda x: x.lower(), tags))
            return valid
        else:
            if len(tags) < MIN_TAGS:
                self.add_error('custom_tags', 'You must add at least two tags')
            elif len(tags) > MAX_TAGS:
                self.add_error(
                    'custom_tags', 'You cannot add more than six tags')
            valid = False

        self.add_error_css_class()
        return valid


class QuestionVoteForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True
    )

    question = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=Question.objects.all(),
        disabled=True
    )

    value = forms.ChoiceField(
        label='Vote',
        widget=forms.RadioSelect,
        choices=QuestionVote.VALUE_CHOICES
    )

    class Meta:
        model = QuestionVote
        fields = ('user', 'question', 'value')


class AnswerForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True
    )

    question = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=Question.objects.all(),
        disabled=True
    )

    class Meta:
        model = Answer
        fields = ('user', 'question', 'body')
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'textarea', 'name': 'answer-body', 'rows': 4}), }


class AnswerVoteForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True
    )

    answer = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=Answer.objects.all(),
        disabled=True
    )

    value = forms.ChoiceField(
        label='Vote',
        widget=forms.RadioSelect,
        choices=AnswerVote.VALUE_CHOICES
    )

    class Meta:
        model = AnswerVote
        fields = ('user', 'answer', 'value')


class AnswerAcceptanceForm(forms.ModelForm):
    accepted = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False
    )

    class Meta:
        model = Answer
        fields = ('accepted', )


class CustomAuhthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'input'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'input'}))


class CustomUserCreationForm(ColorizedErrorFormMixin, UserCreationForm):
    first_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={"class": "input"}))

    last_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={"class": "input"}))

    email = forms.EmailField(
        max_length=254, widget=forms.TextInput(attrs={"class": "input"}))

    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'input'}))

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "input",
                   "placeholder": "min 8 characters, alphanumeric"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"class": "input"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email',
                  'username', 'password1', 'password2')
