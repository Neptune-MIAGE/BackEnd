from django.test import TestCase

# Create your tests here.
class BasicTest(TestCase):
    def test_home_page(self):
        response = self.client.get("/moods")
        self.assertEqual(response.status_code, 200)