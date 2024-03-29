import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question

def create_question(question_text, days):
  # Creates a question with given text and published given number of
  # days offset to now
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text,pub_date=time)

class QuestionViewTests(TestCase):

  def test_index_view_with_no_questions(self):
    # if no questions exist, appropriate message should be shown
    response = self.client.get(reverse('polls:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No polls are available")
    self.assertQuerysetEqual(response.context["latest_question_list"], [])

  def test_index_view_with_past_question(self):
    # Question with pub_date in the past
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

  def test_index_view_with_future_question(self):
    # Question with pub_date in the future
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertContains(response, "No polls are available")
    self.assertQuerysetEqual(response.context["latest_question_list"], [])

  def test_index_view_with_future_and_past_question(self):
    # only past question should be shown when both future and past are available
    create_question(question_text="Past question.", days=-30)
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

  def test_index_view_with_two_past_questions(self):
    # should display multiple past published questions
    create_question(question_text="Past question 1.", days=-30)
    create_question(question_text="Past question 2.", days=-20)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
      response.context['latest_question_list'],
      ['<Question: Past question 2.>', '<Question: Past question 1.>']
    )

class QuestionIndexDetailTests(TestCase):
  def test_detail_view_with_future_question(self):
    # detail view of question with future pub_date returns 404
    future_question = create_question(question_text="Future question.", days=30)
    url = reverse('polls:detail', args=(future_question.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 404)

  def test_detail_view_with_past_question(self):
    # detail view of question with past pub_date should show question
    past_question = create_question(question_text="Past question.", days=-30)
    url = reverse('polls:detail', args=(past_question.id,))
    response = self.client.get(url)
    self.assertContains(response, past_question.question_text)

class QuestionMethodTests(TestCase):

  def test_was_published_recently_with_future_question(self):
    # should return false for question whose pub_date is in future
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertEqual(future_question.was_published_recently(), False)

  def test_was_published_recently_with_old_question(self):
    # should return false for question whose pub_date is older than 1 day
    time = timezone.now() - datetime.timedelta(days=30)
    old_question = Question(pub_date=time)
    self.assertEqual(old_question.was_published_recently(), False)

  def test_was_published_recently_with_recent_question(self):
    # should return true for question whose pub_date is within last day
    time = timezone.now() - datetime.timedelta(hours=1)
    recent_question = Question(pub_date=time)
    self.assertEqual(recent_question.was_published_recently(), True)
