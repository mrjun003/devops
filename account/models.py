from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

# # Create your models here.
class User(models.Model):
    id =  models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=False)
    password_hash = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    role_id = models.CharField(max_length=80)
    permission = models.CharField(max_length=400)
    phone = models.CharField(max_length=12)
    token = models.CharField(max_length=32,default='')
    token_expired = models.IntegerField(null=True,default=0)
    last_login_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now_add=True)


    @staticmethod
    def make_password(plain_password: str) -> str:
        return make_password(plain_password, settings.SECRET_KEY, hasher='pbkdf2_sha256')

    def verify_password(self, plain_password: str) -> bool:
        return check_password(plain_password,settings.SECRET_KEY, self.password_hash)

    @property
    def get_roles(self):
        return self.role_id.split('|')

    @property
    def get_permission(self):
        permission = []
        if self.role_id:
            for id in self.role_id.split('|'):
                permission=list(set(permission).union(set(Role.objects.filter(id=id).first().get_permission)))
        if self.permission:
            permission=list(set(permission).union(set(self.permission.split('|'))))
        return permission

    def __str__(self):
        self.id

    class Meta:
        db_table='users'

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=60, blank=False)
    permission = models.CharField(max_length=400, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def set_permission(plain_permission: list)-> str:
        return '|'.join(plain_permission)

    @property
    def get_permission(self):
        return self.permission.split('|')

    def __str__(self):
        self.id

    class Meta:
        db_table = 'roles'

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    permission = models.CharField(max_length=200, blank=False)
    desc = models.CharField(max_length=200, default='', blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.id

    class Meta:
        db_table = 'permissions'
