from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time
import math
import json
from libs.dbs import *
from .tasks import execSql,execCommand
from libs.ssh import conn_paramiko
import logging
from .models import Instance
from asgiref.sync import async_to_sync

log = logging.getLogger('mydjango')

#执行sql
class execSqlService(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.scope['url_route']['kwargs']['user_name'], self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        print('----------close')
        async_to_sync(self.channel_layer.group_discard)(
            self.scope['url_route']['kwargs']['user_name'], self.channel_name)

    def receive(self, text_data):
        """
        接收消息
        :param text_data: 客户端发送的消息
        :return:
        """
        data = json.loads(text_data)
        print(data)
        sqlList = data['sql'].replace('<br/>','').split(';')
        sqlList.pop()
        nums = len(sqlList)
        num = 0
        conn, cur = connDb2(data['id'])
        if conn:
            for sql in sqlList:
                num += 1
                try:
                    cur.execute(sql)
                    reason = ''
                    status = 'Successed'
                except Exception as e:
                    reason = str(e)
                    status = 'Failed'
                tmpList = {
                    'sql':sql + ';',
                    'reason':reason,
                    'status':status,
                    'pct':math.ceil(num/nums*100)
                }
                log.info(data['username']+ ':' + str(tmpList))
                self.send(str(tmpList))
        else:
            log.error('Connect the database error,' + cur + '.')
            self.send('Connect the database error,' + cur + '.')
        self.send('END')

#切换ADG
class switchADG(WebsocketConsumer):
    def connect(self):
        print('----------connect')
        async_to_sync(self.channel_layer.group_add)(
            self.scope['url_route']['kwargs']['user_name'], self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        print('----------close')
        async_to_sync(self.channel_layer.group_discard)(
            self.scope['url_route']['kwargs']['user_name'], self.channel_name)

    def receive(self, text_data):
        """
        接收消息
        :param text_data: 客户端发送的消息
        :return:
        """
        data = json.loads(text_data)
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        flag = False
        mrpInstId = ''
        mrpInstIp = ''
        Instance.objects.filter(is_delete=0, cluster_id=data['clusterid'],
                                db_status='Running',operate=0).update(operate=1)
        insts = Instance.objects.filter(is_delete=0, cluster_id=data['clusterid'],
                             db_role='PHYSICAL STANDBY',db_status='Running',operate=1)
        sdbs = insts.values('id', 'inst_ip')
        total = insts.count()
        activestep = 0
        alterList = []
        if data['switchtype'] == 'force':#强制切换
            if total==1:
                steps = [
                    {'title': '步骤1', 'desc': '强制结束物理备库应用'},
                    {'title': '步骤2', 'desc': '强制切换成主库'},
                    {'title': '步骤3', 'desc': '启动主库'},
                    {'title': '步骤4', 'desc': '切换完成'},
                ]
                mrpInstId = insts.first().id
                mrpInstIp = insts.first().inst_ip
            else:
                steps = [
                    {'title': '步骤1', 'desc': '关闭其余节点，保留日志应用节点'},
                    {'title': '步骤2', 'desc': '强制结束物理备库应用'},
                    {'title': '步骤3', 'desc': '强制切换成主库'},
                    {'title': '步骤4', 'desc': '启动主库'},
                    {'title': '步骤5', 'desc': '启动其余节点'},
                    {'title': '步骤6', 'desc': '切换完成'},
                ]
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            # 当备库节点大于1时关闭其他多余数据库节点
            if total > 1:
                self.send(str({'opt': 'log', 'sql': '------------开始关闭非日志应用的备库实例------------\r\n'}))
                for db in sdbs:
                    if getMrp(db['id']):
                        mrpInstId = db['id']
                        mrpInstIp = db['inst_ip']
                        self.send(str({'opt': 'log', 'sql': '------------备库'+ db['inst_ip'] +'是日志应用节点跳过------------\r\n'}))
                        continue
                    if mrpInstId == '' and db['id'] == list(sdbs)[-1]['id']:
                        mrpInstId = db['id']
                        mrpInstIp = db['inst_ip']
                        self.send(
                            str({'opt': 'log', 'sql': '------------所有备库实例都未开启日志应用，保留当前实例' + db['inst_ip'] + '------------\r\n'}))
                        continue
                    self.send(str({'opt': 'log', 'sql': '------------开始关闭备库实例' + db['inst_ip'] + '------------\r\n'}))
                    execCommand.delay(db['id'], [config.get('common', 'closedatabasesql')])
                    command = 'tail -10f ' + getAlertLog(db['id'])
                    alterList.append(command)
                    ssh = conn_paramiko(db['inst_ip'], )
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    for line in iter(stdout.readline, ""):
                        if 'Shutting down instance (immediate)' in line:
                            flag = True
                        if flag:
                            self.send(str({'opt': 'log', 'sql': line}))
                        if 'Instance shutdown complete' in line:
                            flag = False
                            break
                self.send(str({'opt': 'log', 'sql': '------------关闭非日志应用的备库实例完成------------\r\n\r\n\r\n'}))

            # 强制结束备库应用
            self.send(str({'opt': 'log', 'sql':'', 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始强制结束备库应用------------\r\n'}))
            command = 'tail -10f ' + getAlertLog(mrpInstId)
            execCommand.delay(mrpInstId, [config.get('common', 'forcefinishsql')])
            ssh = conn_paramiko(mrpInstIp, )
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'forcefinishsql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'forcefinishsql') \
                        in line:
                    flag = False
                    break
            self.send(str({'opt': 'log', 'sql': '------------强制结束备库应用完成------------\r\n\r\n\r\n'}))

            #备库强制转换成主库
            self.send(str({'opt': 'log', 'sql':'', 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始备库强制转换成主库------------\r\n'}))
            execCommand.delay(mrpInstId, [config.get('common', 'switchtoprimarysql')])
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'switchtoprimarysql') in line:
                    flag = True
                if flag:
                    print(line)
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'switchtoprimarysql') \
                        in line:
                    flag = False
                    break
            self.send(str({'opt': 'log', 'sql': '------------备库强制转换成主库完成------------\r\n\r\n\r\n'}))

            #开启新主库
            self.send(str({'opt': 'log', 'sql':'', 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始开启新主库------------\r\n'}))
            execCommand.delay(mrpInstId, [config.get('common', 'opendatabasesql')])
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'opendatabasesql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'opendatabasesql') \
                        in line:
                    break
            self.send(str({'opt': 'log', 'sql': '------------开启新主库完成------------\r\n\r\n\r\n'}))

            #打开其他实例
            if total > 1:
                self.send(str({'opt': 'log', 'sql': '------------开启打开其他新主库实例------------\r\n'}))
                self.send(str({'opt': 'log', 'sql': '','activestep': activestep}))
                activestep += 1
                i = 0
                for db in sdbs:
                    if db['id'] != mrpInstId:
                        self.send(
                            str({'opt': 'log', 'sql': '------------打开新主库实例' + db['inst_ip'] + '------------\r\n'}))
                        execCommand.delay(db['id'], [config.get('common', 'startupdatabasesql')])
                        command = alterList[i]
                        ssh = conn_paramiko(db['inst_ip'], )
                        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                        for line in iter(stdout.readline, ""):
                            if 'Starting ORACLE instance (normal)' in line:
                                flag = True
                            if flag:
                                self.send(str({'opt': 'log', 'sql': line}))
                            if 'Completed: ALTER DATABASE OPEN' in line:
                                flag = False
                                break
                        self.send(
                            str({'opt': 'log', 'sql': '------------新主库实例' + db['inst_ip'] + '打开完成------------\r\n\r\n\r\n'}))
                        i += 1
                self.send(str({'opt': 'log', 'sql': '------------打开其他新主库实例完成------------\r\n\r\n\r\n'}))

            tip = """#新主端<br/>
            select to_char(standby_became_primary_scn) from v$database;<br/>
            #新备端<br/>
            startup mount;<br/>
            flashback database to scn standby_became_primary_scn;<br/>
            alter database convert to physical standby;<br/>
            shutdown immediate;<br/>
            startup mount;<br/>
            alter database recover managed standby database using current logfile disconnect;<br/>
            recover managed standby database cancel;<br/>
            alter database open;<br/>
            alter database recover managed standby database using current logfile disconnect from session;
                        """
            self.send(str({'tip': tip, }))
        else:#正常切换
            pinsts = Instance.objects.filter(is_delete=0, cluster_id=data['clusterid'],
                                    db_role='PRIMARY',db_status='Running',operate=1)
            ptotal = pinsts.count()
            pdbs = pinsts.values('id', 'inst_ip')
            pinstId = ''
            pinstIp = ''
            palterList = []
            if total == 1:
                if ptotal == 1:
                    steps = [
                        {'title': '步骤1', 'desc': '检查主备参数设置'},
                        {'title': '步骤2', 'desc': '切换主库为备库'},
                        {'title': '步骤3', 'desc': '检查原主库状态'},
                        {'title': '步骤4', 'desc': '切换备库到主库'},
                        {'title': '步骤5', 'desc': '启动新主库'},
                        {'title': '步骤6', 'desc': '启动新备库'},
                        {'title': '步骤7', 'desc': '开启备库实时应用'},
                        {'title': '步骤8', 'desc': '切换完成'},
                    ]
                else:
                    steps = [
                        {'title': '步骤1', 'desc': '检查主备参数设置'},
                        {'title': '步骤2', 'desc': '保留一个主库实例，关闭其他实例'},
                        {'title': '步骤3', 'desc': '切换主库为备库'},
                        {'title': '步骤4', 'desc': '检查原主库状态'},
                        {'title': '步骤5', 'desc': '切换备库到主库'},
                        {'title': '步骤6', 'desc': '启动新主库'},
                        {'title': '步骤7', 'desc': '启动新备库'},
                        {'title': '步骤8', 'desc': '开启备库实时应用'},
                        {'title': '步骤9', 'desc': '切换完成'},
                    ]
            else:
                if ptotal == 1:
                    steps = [
                        {'title': '步骤1', 'desc': '检查主备参数设置'},
                        {'title': '步骤2', 'desc': '保留一个备库实例，关闭其他实例'},
                        {'title': '步骤3', 'desc': '切换主库为备库'},
                        {'title': '步骤4', 'desc': '检查原主库状态'},
                        {'title': '步骤5', 'desc': '切换备库到主库'},
                        {'title': '步骤6', 'desc': '启动新主库'},
                        {'title': '步骤7', 'desc': '启动新备库'},
                        {'title': '步骤8', 'desc': '开启备库实时应用'},
                        {'title': '步骤9', 'desc': '切换完成'},
                    ]
                else:
                    steps = [
                        {'title': '步骤1', 'desc': '检查主备参数设置'},
                        {'title': '步骤2', 'desc': '保留一个主库实例，关闭其他实例'},
                        {'title': '步骤3', 'desc': '保留一个备库实例，关闭其他实例'},
                        {'title': '步骤4', 'desc': '切换主库为备库'},
                        {'title': '步骤5', 'desc': '检查原主库状态'},
                        {'title': '步骤6', 'desc': '切换备库到主库'},
                        {'title': '步骤7', 'desc': '启动新主库'},
                        {'title': '步骤8', 'desc': '启动新备库'},
                        {'title': '步骤9', 'desc': '开启备库实时应用'},
                        {'title': '步骤10', 'desc': '切换完成'},
                    ]
            #检查主备参数
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始检查主备库参数设置------------\r\n'}))
            params = ''
            sparams = getParam(insts.first().id)
            params += '------------备库参数设置------------\r\n'
            params += '%-40s|-%-60s\r\n' % ('name----------------'
                            '-------------------','value---------------------------')
            for param in sparams['param']:
                log = '%-40s| %-60s\r\n' % (param[0],('NULL' if param[1] == None else param[1].lstrip()))
                params += log
            params += '\r\n\r\n------------备库日志设置------------\r\n'
            params += '--inst_id--|--group--|--thread--|--size--|--type--\r\n'
            for redolog in sparams['redolog']:
                log = '%11s|%9s|%10s|%8s|%8s\r\n' % \
                      (redolog[0],redolog[1],redolog[2],redolog[3],redolog[4])
                params += log
            for standbylog in sparams['standbylog']:
                log = '%11s|%9s|%10s|%8s|%8s\r\n' % \
                      (standbylog[0], standbylog[1], standbylog[2], standbylog[3], standbylog[4])
                params += log

            pparams = getParam(pinsts.first().id)
            params += '\r\n\r\n------------主库参数设置------------\r\n'
            params += '%-40s|-%-60s\r\n' % ('name----------------'
                                            '-------------------', 'value---------------------------')
            for param in pparams['param']:
                log = '%-40s| %-60s\r\n' % (param[0], ('NULL' if param[1] == None else param[1].lstrip()))
                params += log
            params += '\r\n\r\n------------主库日志设置------------\r\n'
            params += '--inst_id--|--group--|--thread--|--size--|--type--\r\n'
            for redolog in pparams['redolog']:
                log = '%11s|%9s|%10s|%8s|%8s\r\n' % \
                      (redolog[0], redolog[1], redolog[2], redolog[3], redolog[4])
                params += log
            for standbylog in pparams['standbylog']:
                log = '%11s|%9s|%10s|%8s|%8s\r\n' % \
                      (standbylog[0], standbylog[1], standbylog[2], standbylog[3], standbylog[4])
                params += log
            self.send(str({'opt': 'log','sql':params}))
            self.send(str({'opt': 'log', 'sql': '------------检查主备库参数设置完成------------\r\n\r\n\r\n'}))

            if ptotal > 1:#保留一个主实例，点关闭其他实例
                self.send(str({'opt': 'log', 'sql': '------------开始关闭其余主库实例，保留一个主库实例------------\r\n'}))
                self.send(str({'steplist': steps, 'activestep': activestep}))
                activestep += 1
                for db in pdbs:
                    if pinstId == '':
                        pinstId = db['id']
                        pinstIp = db['inst_ip']
                        command = 'tail -10f ' + getAlertLog(db['id'])
                        palterList.append(command)
                        self.send(str({'opt': 'log', 'sql': '------------保留实例' + db['inst_ip'] + '------------\r\n'}))
                        continue
                    self.send(str({'opt': 'log', 'sql': '------------开始关闭备库实例' + db['inst_ip'] + '------------\r\n'}))
                    execCommand.delay(db['id'], [config.get('common', 'closedatabasesql')])
                    command = 'tail -10f ' + getAlertLog(db['id'])
                    palterList.append(command)
                    ssh = conn_paramiko(db['inst_ip'], )
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    for line in iter(stdout.readline, ""):
                        if 'Shutting down instance (immediate)' in line:
                            flag = True
                        if flag:
                            self.send(str({'opt': 'log', 'sql': line}))
                        if 'Instance shutdown complete' in line:
                            flag = False
                            break
                self.send(str({'opt': 'log', 'sql': '------------关闭其余主库实例，保留一个主库实例完成------------\r\n\r\n\r\n'}))
            else:
                pinstId = pinsts.first().id
                pinstIp = pinsts.first().inst_ip

            if total > 1:  # 关闭非日志应用备实例
                self.send(str({'steplist': steps, 'activestep': activestep}))
                activestep += 1
                self.send(str({'opt': 'log', 'sql': '------------开始关闭非日志应用的备库实例------------\r\n'}))
                for db in sdbs:
                    if getMrp(db['id']):
                        mrpInstId = db['id']
                        mrpInstIp = db['inst_ip']
                        self.send(str(
                            {'opt': 'log', 'sql': '------------备库' + db['inst_ip'] + '是日志应用节点跳过------------\r\n'}))
                        continue
                    if mrpInstId == '' and db['id'] == list(sdbs)[-1]['id']:
                        mrpInstId = db['id']
                        mrpInstIp = db['inst_ip']
                        self.send(
                            str({'opt': 'log',
                                 'sql': '------------所有备库实例都未开启日志应用，保留当前实例' + db['inst_ip'] + '------------\r\n'}))
                        continue
                    self.send(
                        str({'opt': 'log', 'sql': '------------开始关闭备库实例' + db['inst_ip'] + '------------\r\n'}))
                    execCommand.delay(db['id'], [config.get('common', 'closedatabasesql')])
                    command = 'tail -10f ' + getAlertLog(db['id'])
                    alterList.append(command)
                    ssh = conn_paramiko(db['inst_ip'], )
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    for line in iter(stdout.readline, ""):
                        if 'Shutting down instance (immediate)' in line:
                            flag = True
                        if flag:
                            self.send(str({'opt': 'log', 'sql': line}))
                        if 'Instance shutdown complete' in line:
                            flag = False
                            break
                self.send(str({'opt': 'log', 'sql': '------------关闭非日志应用的备库实例完成------------\r\n\r\n\r\n'}))
            else:
                mrpInstId = insts.first().id
                mrpInstIp = insts.first().inst_ip

            #切换主库为备库
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始切换主库为备库------------\r\n'}))
            print('-----i am here 1')
            execCommand.delay(pinstId, [config.get('common', 'switchlogfilesql')])
            execCommand.delay(pinstId, [config.get('common', 'switchlogfilesql')])
            print('-----i am here 2')
            pcommand = 'tail -10f ' + getAlertLog(pinstId)
            execCommand.delay(pinstId, [config.get('common', 'switchp2ssql')])
            print('-----i am here 3')
            ssh = conn_paramiko(pinstIp, )
            stdin, stdout, stderr = ssh.exec_command(pcommand, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'switchp2ssql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Instance shutdown complete' in line:
                    flag = False
                    break
            self.send(str({'opt': 'log', 'sql': '------------切换主库为备库完成------------\r\n\r\n\r\n'}))

            #检查原备库状态
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始检查原备库状态------------\r\n'}))
            while True:
                if getSwitchoverStatus(mrpInstId):
                    break
                else:
                    self.send(str({'opt': 'log', 'sql': '------------当前备库状态不可切换成主库，等待60s再检查------------\r\n'}))
                    time.sleep(60)
            self.send(str({'opt': 'log', 'sql': '------------检查原备库状态完成------------\r\n\r\n\r\n'}))

            # 切换备库到主库
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始切换主库为备库------------\r\n'}))
            command = 'tail -10f ' + getAlertLog(mrpInstId)
            execCommand.delay(mrpInstId, [config.get('common', 'switchs2psql')])
            ssh = conn_paramiko(mrpInstIp, )
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'switchs2psql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'switchs2psql') in line:
                    flag = False
                    break
            self.send(str({'opt': 'log', 'sql': '------------切换主库为备库完成------------\r\n\r\n\r\n'}))

            # 启动新主库
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始启动新主库------------\r\n'}))
            self.send(str({'opt': 'log', 'sql': '------------开始打开新主库实例' + mrpInstIp + '------------\r\n'}))
            execCommand.delay(mrpInstId, [config.get('common', 'mount2opensql')])
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'mount2opensql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'mount2opensql') in line:
                    flag = False
                    break
            self.send(
                str({'opt': 'log', 'sql': '------------新主库实例' + mrpInstIp + '打开完成------------\r\n\r\n\r\n'}))
            i = 0
            for db in sdbs:
                if db['id'] != mrpInstId:
                    self.send(str({'opt': 'log', 'sql': '------------开始打开新主库实例' + db['inst_ip'] + '------------\r\n'}))
                    execCommand.delay(db['id'], [config.get('common', 'startupdatabasesql')])
                    command = alterList[i]
                    ssh = conn_paramiko(db['inst_ip'], )
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    for line in iter(stdout.readline, ""):
                        if 'Starting ORACLE instance (normal)' in line:
                            flag = True
                        if flag:
                            self.send(str({'opt': 'log', 'sql': line}))
                        if 'Completed: ALTER DATABASE OPEN' in line:
                            flag = False
                            break
                    self.send(
                        str({'opt': 'log', 'sql': '------------新主库实例' + db['inst_ip'] + '打开完成------------\r\n\r\n\r\n'}))
                i += 1
            self.send(str({'opt': 'log', 'sql': '------------启动新主库完成------------\r\n\r\n\r\n'}))

            # 启动新备库
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始启动新备库实例------------\r\n'}))
            i = 0
            for db in pdbs:
                self.send(str({'opt': 'log', 'sql': '------------开始打开新备库实例' + db['inst_ip'] + '------------\r\n'}))
                execCommand.delay(db['id'], [config.get('common', 'startupdatabasesql')])
                if db['id'] == pinstId:
                    command = pcommand
                else:
                    command = palterList[i]
                ssh = conn_paramiko(db['inst_ip'], )
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                for line in iter(stdout.readline, ""):
                    if 'Starting ORACLE instance (normal)' in line:
                        flag = True
                    if flag:
                        self.send(str({'opt': 'log', 'sql': line}))
                    if 'Completed: ALTER DATABASE OPEN' in line:
                        flag = False
                        break
                i += 1
                self.send(
                    str({'opt': 'log', 'sql': '------------新备库实例' + db['inst_ip'] + '打开完成------------\r\n\r\n\r\n'}))
            self.send(str({'opt': 'log', 'sql': '------------启动新备库完成------------\r\n\r\n\r\n'}))

            # 开启备库实时应用
            self.send(str({'steplist': steps, 'activestep': activestep}))
            activestep += 1
            self.send(str({'opt': 'log', 'sql': '------------开始开启新备库实时应用------------\r\n'}))
            command = 'tail -10f ' + getAlertLog(pinstId)
            execCommand.delay(pinstId, [config.get('common', 'tealtimesql')])
            ssh = conn_paramiko(pinstIp, )
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                if config.get('common', 'tealtimesql') in line:
                    flag = True
                if flag:
                    self.send(str({'opt': 'log', 'sql': line}))
                if 'Completed: ' + config.get('common', 'tealtimesql') in line:
                    flag = False
                    break
            #返回ADG的状态
            getStatus(pinstId)
            self.send(str({'opt': 'log', 'sql': '------------开启新备库实时应用完成------------\r\n\r\n\r\n'}))


        #修改运维系统数据库角色
        print('开始修改运维系统数据库角色')
        self.send(str({'opt': 'log', 'sql': '------------开始修改运维系统数据库角色------------\r\n'}))
        changeDbRole(data['clusterid'])
        self.send(str({'opt': 'log', 'sql': '------------修改运维系统数据库角色完成------------\r\n\r\n\r\n'}))
        print('修改运维系统数据库角色完成')
        self.send(str({'steplist': steps, 'activestep': activestep}))
        activestep += 1
        Instance.objects.filter(is_delete=0, cluster_id=data['clusterid'],
                                db_status='Running', operate=1).update(operate=0)
        #完成整个切换
        self.send(str({'opt': 'log', 'sql': '------------成功切换------------\r\n\r\n\r\n'}))
        self.send(str({'opt': '切换完成', 'sql': '', 'activestep': activestep}))
        print('切换完成')


    def log_message(self, event):
        # 消费
        print('-----------------ws send')
        message = event["text"]
        print(message)
        self.send(text_data=message)

#异步
class AsyncSqlService(AsyncWebsocketConsumer):
    async def connect(self):  # 连接时触发
        self.room_name = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = 'notice_%s' % self.room_name  # 直接从用户指定的房间名称构造Channels组名称，不进行任何引用或转义。

        # 将新的连接加入到群组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):  # 断开时触发
        # 将关闭的连接从群组中移除
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):  # 接收消息时触发
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 信息群发
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'system_message',
                'message': message
            }
        )

    # Receive message from room group
    async def message(self, event):
        print('-----------------ws send')
        message = event["text"]
        print(message)
        await self.send(text_data=message)
        # Send message to WebSocket单发消息
        # await self.send(text_data=json.dumps({
        #     'message': message
        # }))

# 同步方式，仅作示例，不使用
class SyncConsumer(WebsocketConsumer):
    def connect(self):
        # 从打开到使用者的WebSocket连接的chat/routing.py中的URL路由中获取'room_name'参数。
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print('WebSocket建立连接：', self.room_name)
        # 直接从用户指定的房间名称构造通道组名称
        self.room_group_name = 'msg_%s' % self.room_name

        # 加入房间
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )  # async_to_sync(…)包装器是必需的，因为ChatConsumer是同步WebsocketConsumer，但它调用的是异步通道层方法。(所有通道层方法都是异步的。)

        # 接受WebSocket连接。
        self.accept()
        simple_username = self.scope["session"]["session_simple_nick_name"]  # 获取session中的值

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': '@{} 已加入房间'.format(simple_username)
            }
        )

    def disconnect(self, close_code):
        print('WebSocket关闭连接')
        # 离开房间
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # 从WebSocket中接收消息
    def receive(self, text_data=None, bytes_data=None):
        print('WebSocket接收消息：', text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 发送消息到房间
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # 从房间中接收消息
    def chat_message(self, event):
        message = event['message']

        # 发送消息到WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

class lookLogConsumer(WebsocketConsumer):
    def connect(self):
        # 创建channels group， 命名为：用户名，并使用channel_layer写入到redis
        #async_to_sync(self.channel_layer.group_add)(self.scope['user'].username, self.channel_name)
        print('-----------------ws connect')
        print(self.scope['url_route']['kwargs']['user_name'], self.channel_name)
        async_to_sync(self.channel_layer.group_add)(self.scope['url_route']['kwargs']['user_name'], self.channel_name)
        # # 返回给receive方法处理
        self.accept()

    def receive(self, text_data):
        print('-----------------ws receive')
        print(text_data)
        for i in range(3):
            print(i)
            time.sleep(1)
            result = {"status": 0, 'data': i}
            result_all = json.dumps(result)
            self.send(result_all)
            # async_to_sync(self.channel_layer.group_send) \
            #     ('mrjun', {"type": "user.message", 'text': result_all})
        # async_to_sync(self.channel_layer.group_send)(
        #     self.scope['url_route']['kwargs']['user_name'],
        #     {
        #         "type": "user.message",
        #         "text": text_data,
        #     },
        # )


    def user_message(self, event):
        # 消费
        print('-----------------ws send')
        message = event["text"]
        print(message)
        self.send(text_data=message)

    def disconnect(self, close_code):
        print('-----------------ws disconnect')
        async_to_sync(self.channel_layer.group_discard)(self.scope['url_route']['kwargs']['user_name'], self.channel_name)
