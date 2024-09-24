from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your models here.
# tạo form đăng kí
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

# bảng dữ liệu snapshot
from django.db import models

class SnapshotList(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.TimeField()
    event = models.CharField(max_length=50, default='Chụp hình')
    image_url = models.CharField(max_length=255)
    end_time = models.TimeField()
    camera = models.IntegerField()
    date = models.DateField()

    class Meta:
        db_table = 'snapshot_list'  # Đảm bảo ánh xạ đúng tên bảng trong MySQL

    def __str__(self):
        return f"{self.date} - {self.event} at {self.time}"

