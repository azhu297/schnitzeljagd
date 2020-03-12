from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor

from .models import *


def delete_unused_uri():
    """ Delete all uris in the database that are not mapped to """
    used_uris = []

    def add_reverse_set(s):
        """ Add all uris that the set maps to """
        for element in s.get_queryset().all():
            used_uris.append(element.uri)

    def find_all_resources():
        """" Find all classes that contain the uri in a one to one relationship """
        for v in dict(vars(Uri)).values():
            if type(v) == ReverseOneToOneDescriptor:
                add_reverse_set(v)

    find_all_resources()

    for uri in Uri.objects.all():
        if uri not in used_uris:
            uri.delete()
