from django.db import models
from users.models import User
import computed_property
from datetime import datetime, date, timedelta


class MyFrigeInside(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="my_frige_inside")
    title = models.CharField(max_length=50)
    amount = models.CharField(max_length=10, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = computed_property.ComputedIntegerField(compute_from='compute_state', null=True, blank=True)

    def __str__(self):
        return str(self.title)
    
    @property
    def compute_state(self):
        if self.expiration_date:
            if self.expiration_date < datetime.today().date():
                self.state = 1
                return 1
            elif self.expiration_date <= datetime.today().date()+ timedelta(days=3):
                self.state = 2
                return 2
            else:
                self.state = 3
                return 3
