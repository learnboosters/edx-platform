from django.conf import settings
from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.dashboard, name='coach_dashboard'),
    url(
        r'^reports/{}/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        views.reports,
        name='coach_reports',
    ),
    url(
        r'^reports/{}/(?P<student_id>[0-9]+)/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        views.student_progress,
        name='coach_student_progress',
    ),
]
