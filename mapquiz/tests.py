from django.db.utils import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse

from .models import *


class UriTest(TestCase):
    def test_uri_generate(self):
        u = Uri()
        u.save()
        self.assertIsNotNone(u.code)

    def test_uri_uniqueness(self):
        u = Uri()
        u.code = "String"
        u.save()

        v = Uri()
        v.code = "String"
        self.assertRaises(IntegrityError, v.save)

    def test_qr_code(self):
        from PIL import Image
        u = Uri()
        u.save()
        self.assert_(Image.isImageType(u.qr_code()))


class HuntTest(TestCase):
    def test_uri(self):
        """ Has a randomly generated unique resource identifier """
        h = Hunt(name="Hunt")
        self.assert_(hasattr(h, "uri"))


class QuizTest(TestCase):
    def test_unique_stage(self):
        """ Every stage has to be unique """
        h = Hunt(name="Hunt")
        h.save()
        q = Quiz(name="Quiz 1", hunt=h, stage=1)
        q.save()
        r = Quiz(name="Quiz 2", hunt=h, stage=2)
        try:
            r.save()
        except ValidationError as e:
            self.fail(f"Raised ValidationError unexpectedly: {e.message}")
        s = Quiz(name="Quiz 3", hunt=h, stage=1)
        self.assertRaises(ValidationError, s.save)


def generate_quiz(stage=0):
    h = Hunt(name="Hunt")
    h.save()
    q = Quiz(name=f"Quiz {stage}", hunt=h, stage=stage)
    q.save()
    return q


def generate_location(hint="A", stage=0):
    loc = Location(quiz=generate_quiz(stage=stage), hint=hint, found_text="Found")
    loc.save()
    return loc


class LocationViewTest(TestCase):
    def test_valid_location(self):
        """ Can reach a valid location by uri code"""
        loc = generate_location()
        url = reverse('mapquiz:location', args=(loc.uri.code,))
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)  # Valid Http Response

    def test_missing_location(self):
        """ Cannot reach a missing url """
        # Get a non existing url by generating a new location but not saving it -> guaranteed missing url
        l = Location(quiz=generate_quiz(), hint="H", found_text="F")
        url = reverse('mapquiz:location', args=(l.uri.code,))
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 404)  # Not found
