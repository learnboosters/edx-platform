import logging
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from util.cache import cache, cache_if_anonymous
from edxmako.shortcuts import render_to_response
from degree_track.models import DegreeTrack

log = logging.getLogger(__name__)

@ensure_csrf_cookie
@cache_if_anonymous()
def track_list(request):
    """
    Render "list tracks" page.
    """
    tracks = DegreeTrack.objects.all()
    return render_to_response('degree_track/list.html', {'tracks': tracks})

@ensure_csrf_cookie
@cache_if_anonymous()
def about_track(request, track_id):
    """
    Render "about track" page.
    """
    track = get_object_or_404(DegreeTrack, pk=track_id)
    return render_to_response('degree_track/about.html', {'track': track})

