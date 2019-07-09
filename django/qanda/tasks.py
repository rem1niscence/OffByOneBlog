from celery import shared_task


@shared_task
def build_new_answer_email(question_id):
    # Import at function level to avoid circular dependency error
    from qanda.models import QuestionSubscription
    subscribers = QuestionSubscription.objects.filter(question_id=question_id)
    return [sub.email_new_answer() for sub in subscribers]


@shared_task
def send_email(user_id, subject, message):
    from django.contrib.auth import get_user_model as User
    user = User().objects.get(id=user_id)
    user.email_user(subject, message)
