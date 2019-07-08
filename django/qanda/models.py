from django.contrib.auth import get_user_model as User
from django.db import models
from django.db.models import IntegerField, OuterRef, Subquery
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from qanda.service import elasticsearch


class VoteManager(models.Manager):
    def __init__(self, vote_model, *args, **kwargs):
        self.vote_model = vote_model
        return super(VoteManager, self).__init__(*args, **kwargs)

    def get_vote_or_unsaved_blank_vote(self, obj_instance, vote_user):
        try:
            return self.model.objects.get(user=vote_user, **{
                self.vote_model: obj_instance})
        except self.model.DoesNotExist:
            return self.model(user=vote_user, **{
                self.vote_model: obj_instance})


class QuestionManager(models.Manager):
    def all_with_prefetch_tags(self, filter=None):
        qs = self.get_queryset()
        if filter:
            qs = qs.filter(**filter)
        return qs.prefetch_related('tags')

    def all_with_relations_and_score(self, filter=None):
        qs = self.all_with_prefetch_tags()
        if filter:
            qs = qs.filter(**filter)
        qs = qs.annotate(score=Coalesce(Sum('questionvote__value'), 0))
        return qs

    def all_with_answer_score(self, filter=None):
        # Have to resort to subqueries to avoid annotation bug, for more info
        # check: https://code.djangoproject.com/ticket/10060
        score = self.get_queryset().annotate(
            score=Coalesce(
                Sum('questionvote__value'), 0)) \
            .filter(pk=OuterRef('pk'))
        ans_score = self.get_queryset().annotate(
            ans_score=Coalesce(
                Sum('answer__answervote__value'), 0)) \
            .filter(pk=OuterRef('pk'))
        qs = self.all_with_prefetch_tags()
        if filter:
            qs = qs.filter(**filter)
        qs = qs.annotate(score=Subquery(score.values('score'),
                                        output_field=IntegerField()),
                         ans_score=Subquery(ans_score.values('ans_score'),
                                            output_field=IntegerField()))
        return qs


class AnswerManager(models.Manager):
    def all_with_score(self):
        qs = self.get_queryset() \
            .annotate(score=Coalesce(Sum('answervote__value'), 0))
        return qs


class Publishable(models.Model):
    user = models.ForeignKey(User(), on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Publishable, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Votable(models.Model):
    UP = 1
    DOWN = -1
    VALUE_CHOICES = (
        (UP, '👍'),
        (DOWN, '👎')
    )
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    user = models.ForeignKey(User(), on_delete=models.CASCADE)
    voten_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Question(Publishable):
    title = models.CharField(max_length=250)
    viewed = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)

    objects = QuestionManager()

    def __str__(self):
        return f'{self.user} | {self.title}'

    def get_absolute_url(self):
        return reverse('qanda:question_detail', kwargs={
            'pk': self.pk, 'title': self.title_as_hyphen()})

    def can_accept_answers(self, user):
        return self.user == user

    def question_text(self):
        return f'{self.title} \n{self.body}'

    def title_as_hyphen(self):
        return self.title.replace(' ', '-')

    class Meta:
        ordering = ["-created", ]

    def as_elastic_search_dict(self):
        return {
            '_id': self.id,
            '_type': 'doc',
            'text': f'{self.title}\n{self.body}',
            'body': self.body,
            'title': self.title,
            'created': self.created,
            'modified': self.modified,
            'id': self.id,
        }

    # Update the elasticsearch server when the model change
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert,
                     force_update=force_update, using=using,
                     update_fields=update_fields)
        elasticsearch.upsert(self)


class Tag(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)


class Answer(Publishable):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    objects = AnswerManager()

    def save(self, *args, **kwargs):
        # There can only be one accepted answer per question
        if self.accepted:
            try:
                tmp = Answer.objects.get(
                    question=self.question.id, accepted=True)
                if self != tmp:
                    tmp.accepted = False
                    tmp.save()
            except Answer.DoesNotExist:
                pass
        super(Answer, self).save(*args,  **kwargs)

    class Meta:
        ordering = ["-accepted", ]

    def __str__(self):
        return f'{self.user} | {self.question.title}'

    def get_absolute_url(self):
        return reverse('qanda:question_detail', kwargs={
            'pk': self.question.pk, 'title':
            self.question.title_as_hyphen()})


class Comment(Publishable):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)


class QuestionVote(Votable):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    objects = VoteManager('question')

    class Meta:
        unique_together = ('user', 'question')


class AnswerVote(Votable):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)

    objects = VoteManager('answer')

    class Meta:
        unique_together = ('user', 'answer')


class ProfileManager(models.Manager):
    # Score for an user is based on the sum of upvotes of all their answers.
    def all_with_user_score(self):
        qs = self.get_queryset()
        qs = qs.annotate(score=Coalesce(
            Sum('user__answer__answervote__value'), 0))
        return qs


class Profile(models.Model):
    user = models.OneToOneField(
        User(), on_delete=models.CASCADE, primary_key=True)
    email_confirmed = models.BooleanField(default=False)

    objects = ProfileManager()

    def __str__(self):
        return f'{self.user}'

    @receiver(post_save, sender=User())
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()


class QuestionSubscriptionManager(models.Manager):
    def is_subscribed(self, user, question):
        return self.model.objects.filter(user=user, question=question).exists()


class QuestionSubscription(models.Model):
    user = models.ForeignKey(User(), on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    objects = QuestionSubscriptionManager()

    def __str__(self):
        return f'{self.user} | {self.question.title}'

    class Meta:
        unique_together = ('user', 'question')
