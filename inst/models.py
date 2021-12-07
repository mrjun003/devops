from django.db import models
from libs.utils import Prpcrypt

# Create your models here.
class Instance(models.Model):
    id =  models.AutoField(primary_key=True)
    inst_ip = models.CharField(max_length=20, blank=False)
    inst_name = models.CharField(max_length=20)
    inst_type = models.CharField(max_length=10)
    ssh_user = models.CharField(max_length=60)
    ssh_port = models.CharField(max_length=10)
    ssh_password = models.CharField(max_length=100)
    db_user = models.CharField(max_length=60)
    db_port = models.CharField(max_length=10)
    db_password = models.CharField(max_length=100)
    db_status = models.CharField(max_length=10)
    db_role = models.CharField(max_length=20)
    cluster_id = models.IntegerField(default=0)
    apps = models.CharField(max_length=60)
    db_version = models.CharField(max_length=200)
    is_delete = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=300,default='')
    operate = models.BooleanField(default=False)

    @staticmethod
    def make_password(plain_password: str) -> str:
        a = Prpcrypt()
        text = a.encrypt(plain_password)
        return text

    @property
    def get_db_password(self):
        a = Prpcrypt()
        return a.decrypt(self.db_password)

    @property
    def get_ssh_password(self):
        a = Prpcrypt()
        return a.decrypt(self.ssh_password)

    def __str__(self):
        self.id

    class Meta:
        db_table='instances'

class Cluster(models.Model):
    id = models.AutoField(primary_key=True)
    cluster_name = models.CharField(max_length=20)
    is_delete = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.id

    class Meta:
        db_table='cluster'

# class ExecSqlLog(models.Model):
#     def __str__(self):
#         self.id
#
#     class Meta:
#         db_table='cluster'