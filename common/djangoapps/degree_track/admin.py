# -*- coding: utf-8 -*-

from django.contrib import admin
from degree_track.models import (
    Degree, DegreeTrack,
    CourseObjective, ObjectivePoint
)

class DegreeTrackAdmin(admin.ModelAdmin):
    list_display = ('name', )
    fields = ('name', 'short_description', 'image', 'courses', )
    search_fileds = ('name',)
    ordering = ('name',)
    filter_horizontal = ('courses',)


class ObjectivePointInline(admin.StackedInline):
    model = ObjectivePoint
    extra = 0

class CourseObjectiveAdmin(admin.ModelAdmin):
    inlines = (ObjectivePointInline,)


admin.site.register(DegreeTrack, DegreeTrackAdmin)
admin.site.register(Degree)
admin.site.register(CourseObjective, CourseObjectiveAdmin)

