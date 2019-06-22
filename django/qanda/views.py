from django.views.generic import CreateView
from qanda import forms
from qanda.models import Tag


class TestView(CreateView):
    form_class = forms.QuestionForm
    template_name = 'qanda/ask_question.html'

    success_url = '/'

    def get_initial(self):
        print(self.request.user)
        return {
            'user': self.request.user.id
        }

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            question = form.save()
            for tag in form.custom_tags:
                try:
                    tag_model = Tag.objects.get(name=tag)
                except Tag.DoesNotExist:
                    tag_model = Tag(name=tag)
                question.tags.add(tag_model)
                tag_model.save()

            question.save()
            # form.save_m2m()
            # Save and redirect as usual
            return super().form_valid(form)
