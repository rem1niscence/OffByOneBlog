from django import forms
from django.contrib.auth import get_user_model
from qanda.models import Question, QuestionVote, Answer, AnswerVote


class QuestionForm(forms.ModelForm):
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

        for field in self.errors:
            self.fields[field].widget.attrs.update(
                {'class': self.fields[field].widget.attrs.get('class', '') +
                 f' {self.error_css_class}'})
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
