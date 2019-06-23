from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DetailView, UpdateView
from qanda.forms import QuestionForm, QuestionVoteForm
from qanda.models import Question, QuestionVote, Tag


class CreateQuestion(CreateView):
    template_name = 'qanda/ask_question.html'
    form_class = QuestionForm

    success_url = '/'

    def get_initial(self):
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
                    tag_model = Tag.objects.create(name=tag)
                question.tags.add(tag_model)
                tag_model.save()

            question.save()
            # Save and redirect as usual
            return super().form_valid(form)
        elif action == 'PREVIEW':
            preview = Question(
                title=form.cleaned_data['title'],
                body=form.cleaned_data['body'])
            ctx = self.get_context_data(preview=preview)
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()


class QuestionDetail(DetailView):
    queryset = Question.objects.all_with_related_model_and_score()

    def get_context_data(self, **kwargs):
        ctx = super(QuestionDetail, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            vote = QuestionVote.objects.get_vote_or_unsaved_blank_vote(
                obj_instance=self.object,
                vote_user=self.request.user
            )
            if vote.id:
                vote_form_url = reverse('qanda:question-vote-update', kwargs={
                    'question_id': self.object.id, 'pk': vote.id})
            else:
                vote_form_url = reverse('qanda:question-vote-create', kwargs={
                    'question_id': self.object.id})
            vote_form = QuestionVoteForm(instance=vote)
            ctx['vote_form'] = vote_form
            ctx['vote_form_url'] = vote_form_url
        return ctx


class QuestionVoteCreate(CreateView):
    form_class = QuestionVoteForm

    def get_initial(self):
        return {
            'user': self.request.user.id,
            'question': self.kwargs['question_id'],
        }

    def get_success_url(self):
        return reverse('qanda:question-detail', kwargs={
            'pk': self.object.question.id, 'title': self.object.question.title
        })

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())


class QuestionVoteUpdate(UpdateView):
    form_class = QuestionVoteForm
    queryset = QuestionVote.objects.all()

    def get_object(self, queryset=None):
        vote = super().get_object(queryset)
        if vote.user != self.request.user:
            raise PermissionDenied('Cannot change another user\'s vote')
        return vote

    def get_success_url(self):
        print(self.object)
        return reverse('qanda:question-detail', kwargs={
            'pk': self.object.question.id, 'title': self.object.question.title
        })

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())
