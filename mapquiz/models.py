from urllib.parse import urljoin

from django.core.validators import ValidationError
from django.db import models

from .id_generator import *


def generate_code():
    return generate_uri_code(32)


class Resource(models.Model):
    """ Abstract base class for all models that have a uri code and name"""
    code = models.SlugField(max_length=32, unique=True, editable=False, default=generate_code)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generates a new code in case it is not unique
        # Only has a limited number of retries,
        # so that other model fields with uniqueness constraint don't lead to an infinite loop
        for retry in range(10):
            try:
                self.validate_unique()
            except ValidationError:
                self.code = generate_uri_code(32)
            else:
                break

        super(Resource, self).save(*args, **kwargs)

    def qr_code(self, path):
        text = urljoin(path, self.code)
        image = generate_qrcode(text)
        return image

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
            .exclude(code=self.code)
        if same_stage.exists():
            raise ValidationError(f"Quiz '{self}' has same stage as: '{same_stage[0]}'")
        super(Resource, self).save(*args, **kwargs)

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

