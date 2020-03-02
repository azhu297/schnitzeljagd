from django.db.utils import IntegrityError
from django.test import TestCase

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

    def test_qrcode(self):
        from PIL import Image
        u = Uri()
        u.save()
        self.assert_(Image.isImageType(u.generate_qrcode()))


class HuntTest(TestCase):
    def test_unique_name(self):
        h = Hunt(name="hunt")
        h.save()
        j = Hunt(name="hunt")
        self.assertRaises(IntegrityError, j.save)

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
