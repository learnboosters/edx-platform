"""
This module creates a coach dashboard for viewing reports.
"""
import logging

from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django_countries import countries
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from opaque_keys.edx.keys import CourseKey
from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from courseware.courses import get_course_by_id, get_course_with_access
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from student.models import UserProfile, CourseEnrollment
from school.models import School
from xmodule.modulestore.django import modulestore

log = logging.getLogger(__name__)


@login_required
@ensure_csrf_cookie
def dashboard(request):
    """
    Provides the coach dashboard view

    Arguments:
        request: The request object.

    Returns:
        The coach dashboard response.

    """
    user = request.user
    user_profile = getattr(user, 'profile')

    # Get the associated school
    school = user_profile and user_profile.school

    # Ensure the user is assigned a coach role for school
    if not (user_profile.is_coach and school):
        return HttpResponseForbidden()


    # Get student profiles
    students = UserProfile.objects.filter(
        school=school
    ).exclude(is_coach=True)

    # Get course enrollments
    enrollments = CourseEnrollment.objects.filter(
        user__in=[student.user.id for student in students],
        is_active=True
    )
    course_wise_enrollments = {}
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        if course not in courses:
            courses.append(course)
        num_enrollment = course_wise_enrollments.get(course.display_name, 0)
        course_wise_enrollments.update({course.display_name: num_enrollment+1})

    return render_to_response(
        'coach/dashboard.html', {
            'students': students,
            'courses': courses,
            'enrollments': course_wise_enrollments,
            'uses_bootstrap': True,
        }
    )

@login_required
@ensure_csrf_cookie
def reports(request, course_id):
    """
    Reports on specific course to be reviewed by a coach.

    Arguments:
        request: The request object.
        course_id: Course ID for which reports needs to be listed.

    Returns:
        The reports response.

    """
    user = request.user
    user_profile = getattr(user, 'profile')

    # Get the associated school
    school = user_profile and user_profile.school

    # Ensure the user is assigned a coach role for school
    if not (user_profile.is_coach and school):
        return HttpResponseForbidden()

    # Get the list of students enrolled in course
    course_key = CourseKey.from_string(course_id)
    course = get_course_by_id(course_key)
    enrolled_students = User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
        profile__school=school
    ).exclude(profile__is_coach=True).order_by('username').select_related("profile")

    students = []
    with modulestore().bulk_operations(course.location.course_key):
        students = [
            {
                'username': student.username,
                'id': student.id,
                'email': student.email,
                'grade_summary': CourseGradeFactory().read(student, course).summary
            }
            for student in enrolled_students
        ]

    return render_to_response(
        'coach/grades.html', {
            'students': students,
            'course': course,
            'ordered_grades': sorted(course.grade_cutoffs.items(), key=lambda i: i[1], reverse=True),
            'uses_bootstrap': True,
        }
    )

@login_required
@ensure_csrf_cookie
def student_progress(request, course_id, student_id):
    """
    Renders the reports for a coach for a specific
    student in specific course.

    Arguments:
        request: The request object.
        course_id: Course ID for which reports needs to be rendered.
        student_id: User id presenting student.

    Returns:
        The HTML response containing reports.

    """
    user = request.user
    user_profile = getattr(user, 'profile')

    # Get the associated school
    school = user_profile and user_profile.school

    # Ensure the user is assigned a coach role for school
    if not (user_profile.is_coach and school):
        return HttpResponseForbidden()

    # Get the student course progress
    if student_id is not None:
        try:
            student_id = int(student_id)
            student = User.objects.get(id=student_id)
        # Check for ValueError if 'student_id' cannot be converted to integer.
        except ValueError:
            raise Http404

    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(student, 'load', course_key, check_if_enrolled=False)
    course_grade = CourseGradeFactory().read(student, course)
    courseware_summary = course_grade.chapter_grades.values()

    return render_to_response('coach/student_progress.html', {
        'student': student,
        'course': course,
        'courseware_summary': courseware_summary,
        'uses_bootstrap': True,
    })

@login_required
@ensure_csrf_cookie
@transaction.atomic
def import_users(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    error = []
    message = ""
    if request.method == 'POST':
        csv_file = request.FILES["csvfile"]
        file_data = csv_file.read().decode("utf-8")
        lines = file_data.split("\n")
        for line_num, line in enumerate(lines):
            if not line_num:
                continue
            fields = line.split(",")
            try:
                with transaction.atomic():
                    user = User.objects.create(username=fields[0], first_name=fields[2], last_name=fields[3],
                        email=fields[4], is_active=True)
                    user.set_password(fields[5])
                    user.save()
                    school, created = School.objects.get_or_create(name=fields[7])
                    country = countries.by_name(fields[14])
                    profile = UserProfile.objects.create(user=user, name=fields[1],
                        is_coach=fields[6].lower() != 'student', school=school, level=fields[8],
                        section=fields[9], idkit=fields[10], city=fields[12], region=fields[13],
                        country=country)
                    course = CourseOverview.objects.filter(display_name=fields[11])
                    if course.count():
                        course_key = course[0].id
                        CourseEnrollment.enroll(user, course_key)
            except Exception as e:
                log.info(str(e))
                error.append("Line number: "+ str(line_num+1) + " > " + line)
        message = "Data import success!" if not error else "Could not import data!"

    return render_to_response('coach/import_users.html', {'message': message, 'error': error})
