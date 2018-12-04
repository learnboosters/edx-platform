# -*- coding: utf-8 -*-

import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext as _
from opaque_keys.edx.django.models import CourseKeyField
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from django.utils.encoding import python_2_unicode_compatible


class Degree(models.Model):
    """
    This model represents courses
    """
    course_id = CourseKeyField(db_index=True, max_length=255)
    name = models.CharField(
        verbose_name=_("Course Name"),
        max_length=255
    )
    image_url = models.CharField(max_length=255)
    short_description = models.TextField(max_length=255, null=True)

    class Meta:
        verbose_name = _("Degree Course")
        verbose_name_plural = _("Degree Courses")
        ordering = ('name',)

    def __str__(self):
        return self.name


class DegreeTrack(models.Model):
    """
    This model represents group of courses
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        verbose_name=_("Track Name"),
        max_length=255
    )
    short_description = models.TextField(
        verbose_name=_("Short Description"),
        max_length=255
    )
    image = models.ImageField(upload_to='tracks')
    courses = models.ManyToManyField(Degree)

    class Meta:
        verbose_name = _("Degree Track")
        verbose_name_plural = _("Degree Tracks")
        ordering = ('name',)

    def __str__(self):
        return self.name

@receiver([post_save], sender=CourseOverview)
def course_name_handler(sender, instance, **kwargs):
    try:
        course = Degree.objects.get(course_id=instance.id)
        course.name = instance.display_name
        course.image_url = instance.course_image_url
        course.short_description = instance.short_description
        course.save()
    except:
        course = Degree.objects.create(
            course_id=instance.id,
            name=instance.display_name,
            image_url=instance.course_image_url,
            short_description=instance.short_description
        )

@receiver([post_delete], sender=CourseOverview)
def course_remove_handler(sender, instance, **kwargs):
    try:
        Degree.objects.filter(course_id=instance.id).delete()
    except:
        pass


class CourseObjective(models.Model):
    """
    This model represents course objectives.
    """
    course = models.ForeignKey(Degree, on_delete=models.CASCADE)
    title = models.CharField(
        verbose_name=_("Objective"),
        max_length=255
    )
    number = models.PositiveSmallIntegerField(
        verbose_name=_("Objective number")
    )

    class Meta:
        verbose_name = _("Course Objective")
        verbose_name_plural = _("Course Objectives")
        ordering = ('number',)

    def __str__(self):
        return "{} - {}".format(self.course.name, self.number)

@python_2_unicode_compatible
class ObjectivePoint(models.Model):
    """
    This model represents course abjective points.
    """
    objective = models.ForeignKey(CourseObjective, on_delete=models.CASCADE)
    point = models.CharField(
        verbose_name=_("Objective point"),
        max_length=255
    )

    class Meta:
        verbose_name = _("Objective Point")
        verbose_name_plural = _("Objective Points")
        ordering = ('point',)

    def __str__(self):
        return self.point

