from __future__ import absolute_import
# from celery import task
from celery import shared_task
import time
from .models import Instance
from libs.dbs import connDb
from libs.ssh import conn_paramiko
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from libs.dbs import checkDatabaseExist
from libs.ssh import checkHostExist


@periodic_task(run_every=60)
def checkInstAlived():
    insts = list(Instance.objects.filter(is_delete=0,operate=0).values('id', 'inst_ip',
                'ssh_port','db_status', 'inst_type','operate','db_user'))
    for inst in insts:
        ip, alived = checkHostExist(inst['inst_ip'], inst['ssh_port'])
        if alived:
            res = checkDatabaseExist(inst['id'],inst['inst_type'])
            if inst['inst_type'] == 'Oracle':
                if res != 'X' and inst['db_status'] == 'Running':
                    Instance.objects.filter(id=inst['id'],operate=0).update(db_status='Stoped', reason=res)
                if res == 'X' and inst['db_status'] == 'Stoped':
                    Instance.objects.filter(id=inst['id'],operate=0).update(db_status='Running', reason='')
            elif inst['inst_type'] == 'Mysql':
                if res != 1 and inst['db_status'] == 'Running':
                    Instance.objects.filter(id=inst['id'],operate=0).update(db_status='Stoped', reason=res)
                if res == 1 and inst['db_status'] == 'Stoped':
                    Instance.objects.filter(id=inst['id'],operate=0).update(db_status='Running', reason='')
        else:
            if inst['db_status'] == 'Running':
                Instance.objects.filter(id=inst['id'],operate=0).update(db_status='Stoped', reason='主机无法连接')


# @shared_task
# def add(x=1, y=2):
#     print('开始---------------------------')
#     "%d + %d = %d" % (x, y, x + y)
#     time.sleep(15)
#     print(x+y)
#     print('结束---------------------------')
#     return x + y
#
# @shared_task
# def mul(x, y):
#     print
#     "%d * %d = %d" % (x, y, x * y)
#     return x * y
#
# @shared_task
# def sub(x, y):
#     print
#     "%d - %d = %d" % (x, y, x - y)
#     return x - y

@shared_task
def execSql(instId,sql):
    print(sql)
    inst = Instance.objects.filter(id=instId).first()
    res, cur = connDb(inst.inst_ip, inst.db_user, inst.get_db_password, inst.db_port,
                 service_name=inst.inst_name,database=inst.inst_name, type=inst.inst_type)
    sqlList = sql.split(';')
    time.sleep(5)
    for execSql in sqlList:
        print(execSql)
        cur.execute(execSql)
    # cur.close()

@shared_task
def execCommand(instId,sqlList):
    inst = Instance.objects.filter(id=instId).first()
    ssh = conn_paramiko(inst.inst_ip, )
    if inst.ssh_user == 'root':
        command = 'su - oracle -c \'echo "$sql" |sqlplus -s sys/oracle as sysdba \''
    elif inst.ssh_user == 'oracle':
        command = 'echo "$sql" |sqlplus -s sys/oracle as sysdba'
    for sql in sqlList:
        command = command.replace('$sql',sql + ';')
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        print(command)
        print(stdout.read())
    ssh.close()

@shared_task
def test(username,text):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(username, {"type": "message",
                                                           'text': text})