from django.test import TestCase
from tournaments.models import Tournament

class ScoreTestCase(TestCase):
    def setUp(self):
        Tournament.objects.create(name='hmmm',slug='hmmm')

    def test_tournamnet(self):
        tournament = Tournament.objects.get(name='hmmm')

        self.assertEqual(tournament.speak(),'hmmm')
# Create your tests here.
