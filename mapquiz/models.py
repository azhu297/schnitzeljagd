from urllib.parse import urljoin

from django.core.validators import ValidationError
from django.db import models

from .id_generator import *


class Uri(models.Model):
    code = models.SlugField(max_length=32, unique=True, editable=False)

    def __str__(self):
        return self.code

    def qr_code(self, path):
        text = urljoin(path, self.code)
        image = generate_qrcode(text)
        return image


def generate_uri():
    while True:
        code = generate_uri_code(32)
        if not Uri.objects.filter(code=code).exists():
            break

    uri = Uri(code=code)
    uri.save()
    return uri


class Resource(models.Model):
    """ Abstract base class for all models that have a uri and name"""
    uri = models.OneToOneField(Uri, on_delete=models.CASCADE, blank=True, primary_key=True, default=generate_uri)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Hunt(Resource):
    def stages(self) -> int:
        """ Return number of stages in the Hunt """
        return self.quiz_set.count()


class Quiz(Resource):
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)
    stage = models.IntegerField()

    def save(self, *args, **kwargs):
        same_stage = Quiz.objects.filter(hunt=self.hunt, stage=self.stage) \
            .exclude(uri__code=self.uri.code)
        if same_stage.exists():
            raise ValidationError(f"Quiz '{self}' has same stage as: '{same_stage[0]}'")

    class Meta:
        verbose_name_plural = "quizzes"


class Location(Resource):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    # Providing hint to find this location
    hint = models.TextField(max_length=1_000)
    # Success text, provided once this location has been found
    found_text = models.TextField(max_length=1_000)
    lat = models.FloatField("latitude", null=True, blank=True)
    lng = models.FloatField("longitude", null=True, blank=True)


class Team(Resource):
    name = models.CharField(max_length=32, unique=True)
    logo = models.ImageField(blank=True, null=True)
    hunt = models.ForeignKey(Hunt, blank=True, null=True, on_delete=models.SET_NULL)
    last_location = models.ForeignKey(Location, default=None, blank=True, null=True, on_delete=models.SET_NULL)

