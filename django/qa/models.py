from django.db import models
from django.contrib.auth import get_user_model as User
from django.utils import timezone
from django.db.models.aggregates import Sum


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
    def all_with_related_model_and_score(self):
        qs = self.get_queryset()
        qs = qs.annotate(score=Sum('questionvote__value'))
        return qs


class AnswerManager(models.Manager):
    def all_with_related_model_and_score(self):
        qs = self.get_queryset()
        qs = qs.annotate(score=Sum('answervote__value'))
        return qs


class Publishable(models.Model):
    user = models.ForeignKey(User(), on_delete=models.CASCADE)
    body = models.TextField()
    votes = models.IntegerField(default=0)
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
        (UP, 'Up'),
        (DOWN, 'Down')
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


class Tag(models.Model):
    name = models.CharField(max_length=40)


class Answer(Publishable):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)

    objects = AnswerManager()


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
