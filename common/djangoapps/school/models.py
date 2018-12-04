import uuid
from django.db import models
from django.utils.translation import ugettext as _


class School(models.Model):
    """
    This model represents school master
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        verbose_name=_("School Name"),
        max_length=255
    )

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        ordering = ('name',)

    def __str__(self):
        return self.name

