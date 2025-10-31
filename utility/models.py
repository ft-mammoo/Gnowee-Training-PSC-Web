from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import Signal

User = get_user_model()
soft_deleted = Signal()

class BaseModel(models.Model):
    class Meta:
        abstract = True
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="%(class)s_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="%(class)s_updated_by"
    )
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

class SoftDeleteModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="a")

class SoftDeleteModel(BaseModel):
    objects = SoftDeleteModelManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True

    def delete(self, using = None, keep_parents = False):
        self.status = "i"
        self.save()
        soft_deleted.send(sender=self.__class__, instance=self)

    def activate(self):
        self.status = "i"
        self.save()
