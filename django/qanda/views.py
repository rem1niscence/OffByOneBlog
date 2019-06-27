from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)
from qanda.forms import (AnswerAcceptanceForm, AnswerForm, AnswerVoteForm,
                         CustomUserCreationForm, QuestionForm,
                         QuestionVoteForm)
from qanda.models import Answer, AnswerVote, Question, QuestionVote, Tag


class CreateQuestion(LoginRequiredMixin, CreateView):
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
    queryset = Question.objects.all_with_relations_and_score()

    def get_vote_data(self, model, obj, url_id, create_url, update_url):
        vote = model.objects.get_vote_or_unsaved_blank_vote(
            obj_instance=obj,
            vote_user=self.request.user)
        if vote.id:
            vote_form_url = reverse(update_url, kwargs={
                url_id: obj.id, 'pk': vote.id})
        else:
            vote_form_url = reverse(create_url, kwargs={
                url_id: obj.id})

        return {'instance': vote, 'url': vote_form_url}

    def get_context_data(self, **kwargs):
        self.object.viewed += 1
        self.object.save()
        ctx = super(QuestionDetail, self).get_context_data(**kwargs)
        ctx['answers'] = []
        answers = Answer.objects.all_with_score() \
            .filter(question=self.object.id)

        for ans in answers:
            answer_dict = {}
            answer_dict['info'] = ans
            ctx['answers'].append(answer_dict)

        if self.object.can_accept_answers(self.request.user):
            ctx['accept_form'] = \
                AnswerAcceptanceForm(initial={'accepted': True})
            ctx['reject_form'] = \
                AnswerAcceptanceForm(initial={'accepted': False})

        if self.request.user.is_authenticated:
            vote_data = self.get_vote_data(
                QuestionVote, self.object, 'question_id',
                'qanda:question-vote-create',
                'qanda:question-vote-update')
            vote_form = QuestionVoteForm(instance=vote_data['instance'])
            ctx['vote_form'] = vote_form
            ctx['vote_form_url'] = vote_data['url']

            i = 0
            for ans in answers:
                answer_dict = {}
                ans_vote_data = self.get_vote_data(
                    AnswerVote, ans, 'answer_id', 'qanda:answer-vote-create',
                    'qanda:answer-vote-update')

                answer_dict['vote_form'] = AnswerVoteForm(
                    instance=ans_vote_data['instance'])
                answer_dict['vote_url'] = ans_vote_data['url']
                ctx['answers'][i].update(answer_dict)
                i += 1

            ctx['answer_form'] = AnswerForm()
            ctx['answer_form_url'] = reverse('qanda:answer-create', kwargs={
                'question_id': self.object.id})

        return ctx


class QuestionVoteCreate(LoginRequiredMixin, CreateView):
    form_class = QuestionVoteForm

    def get_initial(self):
        return {
            'user': self.request.user.id,
            'question': self.kwargs['question_id'],
        }

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())


class QuestionVoteUpdate(LoginRequiredMixin, UpdateView):
    form_class = QuestionVoteForm
    queryset = QuestionVote.objects.all()

    def get_object(self, queryset=None):
        vote = super().get_object(queryset)
        if vote.user != self.request.user:
            raise PermissionDenied('Cannot change another user\'s vote')
        return vote

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())


class AnswerCreate(LoginRequiredMixin, CreateView):
    form_class = AnswerForm

    def get_initial(self):
        return {
            'user': self.request.user.id,
            'question': self.kwargs['question_id'],
        }

    def get_success_url(self):
        return self.object.question.get_absolute_url()


class AnswerVoteCreate(LoginRequiredMixin, CreateView):
    form_class = AnswerVoteForm

    def get_initial(self):
        return {
            'user': self.request.user.id,
            'answer': self.kwargs['answer_id'],
        }

    def get_success_url(self):
        return self.object.answer.question.get_absolute_url()

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())


class AnswerVoteUpdate(LoginRequiredMixin, UpdateView):
    form_class = AnswerVoteForm
    queryset = AnswerVote.objects.all()

    def get_object(self, queryset=None):
        vote = super().get_object(queryset)
        if vote.user != self.request.user:
            raise PermissionDenied('Cannot change another user\'s vote')
        return vote

    def get_success_url(self):
        return self.object.answer.question.get_absolute_url()

    def render_to_response(self, context, **response_kwargs):
        return redirect(to=self.get_success_url())


class UpdateAnswerAcceptanceView(LoginRequiredMixin, UpdateView):
    form_class = AnswerAcceptanceForm
    queryset = Answer.objects.all()

    def get_success_url(self):
        return self.object.question.get_absolute_url()


class HomePageView(TemplateView):
    template_name = 'qanda/homepage.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomePageView, self).get_context_data(**kwargs)

        sort_by = self.request.GET.get('sort', None)
        if (sort_by == 'newest'):
            ctx["questions"] = \
                Question.objects.all_with_relations_and_score()
        elif (sort_by == 'answered'):
            ctx["questions"] = \
                Question.objects.all_with_answer_score() \
                .order_by('-ans_score')
        else:
            ctx["questions"] = \
                Question.objects.all_with_relations_and_score() \
                .order_by("-score")

        ctx['last_answers'] = Answer.objects.all_with_score() \
            .order_by('-created')[:5]
        return ctx


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('qanda:homepage')
