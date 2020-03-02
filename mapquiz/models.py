from django.core.validators import ValidationError
from django.db import models

from .id_generator import *


class Uri(models.Model):
    code = models.CharField(max_length=32, null=True, blank=True, unique=True, editable=False)

    def __str__(self):
        return self.code

    def generate_qrcode(self):
        return generate_qrcode(self.code)

    def save(self):
        while self.code is None:
            code = generate_uri_code(32)
            if not Uri.objects.filter(code=code).exists():
                self.code = code

        super(Uri, self).save()


def generate_uri():
    uri = Uri()
    uri.save()
    return uri


class Resource(models.Model):
    """ Abstract base class for all models that have a uri """
    uri = models.OneToOneField(Uri, on_delete=models.CASCADE, primary_key=True, default=generate_uri)

    class Meta:
        abstract = True


class Hunt(Resource):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Quiz(Resource):
    name = models.CharField(max_length=32, unique=True)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)
    stage = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self):
        same_stage = Quiz.objects.filter(hunt=self.hunt, stage=self.stage)
        if same_stage.exists():
            raise ValidationError(f"Quiz '{self}' has same stage as: '{same_stage[0]}'")

        super(Quiz, self).save()


class Location(Resource):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    hint = models.TextField(max_length=1_000)  # Providing hint to find this location
    found_text = models.TextField(max_length=1_000)  # Success text, provided once this location has been found
    lat = models.FloatField("latitude", null=True)
    lng = models.FloatField("longitude", null=True)

    def __str__(self):
        return self.hint


class Team(Resource):
    name = models.CharField(max_length=32, unique=True)
    logo = models.ImageField(blank=True, null=True)
    hunt = models.ForeignKey(Hunt, blank=True, null=True, on_delete=models.SET_NULL)
    last_location = models.ForeignKey(Location, default=None, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
