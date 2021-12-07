from rest_framework.views import APIView
from libs.parser import JsonParser, Argument
from libs.utils import json_response, str2List,int2Date
from libs.ssh import *
from libs.dbs import getDbBaseInfo, getDbinfo, \
    getcommonInfo,getInfo,getMysqlInfo,getMlInfo
from .models import *
import logging
from .tasks import *
from channels.layers import get_channel_layer
import os
import json
from asgiref.sync import async_to_sync
# from django.db.models import Count

log = logging.getLogger('mydjango')

# Create your views here.
class GetIndexInfo(APIView):
    def get(self,request):
        # Instance.objects.values('inst_type').filter(is_delete=0).annotate(typecount=Count('inst_type'))
        mysqlCount = Instance.objects.filter(is_delete=0,inst_type='Mysql').count()
        oracleCount = Instance.objects.filter(is_delete=0, inst_type='Oracle').count()
        total = Instance.objects.filter(is_delete=0).count()
        otherCount = total - mysqlCount - oracleCount
        insts = Instance.objects.filter(is_delete=0,db_status='Stoped').\
            values('id','inst_ip',"inst_name", "inst_type", "db_status",
                                 "db_role", "cluster_id", "apps", "reason")
        data = {'total':total,'otherCount':otherCount,'mysqlCount':mysqlCount,
                'oracleCount':oracleCount, 'insts':list(insts)}
        return json_response(data=data)

class AddInst(APIView):
    def post(self,request):
        form, error = JsonParser(
            Argument('inst_ip',),
            Argument('inst_name', ),
            Argument('inst_type', ),
            Argument('apps', ),
            Argument('ssh_user', required=False, default='',),
            Argument('ssh_port', required=False, default='',),
            Argument('ssh_password', required=False, default='',),
            Argument('db_user', ),
            Argument('db_port', ),
            Argument('db_password', ),
            Argument('cluster_id', ),
        ).parse(request.body)
        if error is None:
            if form.inst_type != 'Rds':
                ip, is_active = checkHostExist(form.inst_ip, form.ssh_port)
                if is_active == False:
                    return json_response(message='%s %s' % (ip, '服务器未启动'))
                is_success = configAuthorized(form.inst_ip, form.ssh_user, form.ssh_password, form.ssh_port)
                if is_success == False:
                    return json_response(message=is_success)
            is_success ,cur = connDb(form.inst_ip, form.db_user, form.db_password, form.db_port
                   , service_name=form.inst_name, database=form.inst_name, type=form.inst_type)
            if is_success == False:
                return json_response(message=cur)
            version ,db_role = getDbBaseInfo(cur ,form.inst_type)
            inst = Instance(inst_ip=form.inst_ip ,inst_name=form.inst_name,
                            inst_type=form.inst_type ,ssh_user=form.ssh_user,
                            ssh_port=form.ssh_port ,
                            ssh_password=Instance.make_password(form.ssh_password) if form.ssh_password else form.ssh_password,
                            db_user=form.db_user ,db_port=form.db_port,
                            db_password=Instance.make_password(form.db_password),
                            db_status='Running' ,db_role=db_role,
                            cluster_id=form.cluster_id ,apps=form.apps,db_version=version)
            inst.save()
            return json_response(data='实例添加完成！')
        else:
            log.error(error)
            return json_response(message=error)

class GetInst(APIView):
    def post(self,request):
        form, error = JsonParser(
            Argument('inst_name', required=False,),
            Argument('inst_type', required=False,),
            Argument('inst_ip', required=False,),
            Argument('inst_apps', required=False,),
            Argument('db_status', required=False,),
            Argument('cluster_id', required=False, ),
            Argument('page', default=1, type=int ,required=False,),
        ).parse(request.body)
        if error is None:
            insts = Instance.objects.filter(is_delete=0)
            if form.inst_name:
                insts = insts.filter(inst_name__contains=form.inst_name)
            if form.inst_type and form.inst_type != 'ALL':
                insts = insts.filter(inst_type=form.inst_type)
            if form.inst_ip:
                insts = insts.filter(inst_ip__contains=form.inst_ip)
            if form.db_status and form.db_status != 'ALL':
                insts = insts.filter(db_status=form.db_status)
            if form.inst_apps:
                insts = insts.filter(inst_ip__contains=form.inst_apps)
            if form.cluster_id and form.cluster_id != 'ALL':
                insts = insts.filter(cluster_id=form.cluster_id)
                # 关联查询
            total = insts.count()
            insts = insts.values("id", "inst_ip", "inst_name", "inst_type", "db_status",
                                 "db_role", "cluster_id", "apps", "db_version")[(form.page-1)*10:form.page*10]
            data = {
                'total':total,
                'data':list(insts)
            }
            return json_response(data)
        else:
            return json_response(message=error)

class DelInst(APIView):
    def get(self,request):
        form, error = JsonParser(
            Argument('id',),
        ).parse(request.GET)
        if error is None:
            print(form.id)
            Instance.objects.filter(id=form.id).update(is_delete=1)
            log.info('成功')
            log.error('error')
            return json_response(data='成功！')
        else:
            return json_response(message=error)

class EditInst(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('id', ),
        ).parse(request.GET)
        if error is None:
            Instance.objects.filter(id=form.id).update(is_delete=1)
            return json_response(data='成功！')
        else:
            return json_response(message=error)

class GetInfo(APIView):
    def get(self,request):
        form, error = JsonParser(
            Argument('id',),
            Argument('tab', ),
            Argument('item', default=None, required=False,),
            Argument('filter', default=None, required=False, ),
        ).parse(request.GET)
        if error is None:
            # print("filter: %s" % form.filter if form.filter!=None else 'None')
            if form.item != None:
                item = form.item.split(',')
            else:
                item = None
            inst = Instance.objects.filter(id=form.id).first()
            is_success, cur = connDb(inst.inst_ip, inst.db_user, inst.get_db_password,
                                     inst.db_port, service_name=inst.inst_name,
                                     database=inst.inst_name,type=inst.inst_type)
            if is_success == False:
                return json_response(message=cur)
            is_success, data = getDbinfo(inst.inst_type, form.tab, cur, item, form.filter)
            if is_success == False:
                return json_response(message=data)
            if form.tab == 'info':
                clusterInfo = []
                isDataguard = False
                if inst.cluster_id !=0:
                    cluster = Cluster.objects.filter(id=inst.cluster_id).first()
                    insts = Instance.objects.filter(cluster_id=inst.cluster_id,is_delete=0)
                    for i in insts:
                        clusterInfo.append({'ip':i.inst_ip, 'db_role':i.db_role,
                                            'cluster_id':inst.cluster_id,
                                            'cluster_name':cluster.cluster_name})
                        if i.db_role == 'PHYSICAL STANDBY':
                            isDataguard = True
                        # print(i.inst_ip,i.db_role)
                data['clusterinfo'] = clusterInfo
                print(data.keys())
                data['instanceinfodata'][0]['inst_port'] = inst.db_port
                data['databaseinfodata'][0]['guard_status'] = isDataguard
            return json_response(data=data)
        else:
            return json_response(message=error)

class GetMLInfo(APIView):
    def get(self,request):
        form, error = JsonParser(
            Argument('id',),
            Argument('item',),
            Argument('filter', default=None, required=False, ),
        ).parse(request.GET)
        if error is None:
            print(form.id,form.item,form.filter)
            is_success, data = getMlInfo(form.id, form.item, form.filter)
            if is_success == False:
                return json_response(message=data)
            return json_response(data=data)
        else:
            return json_response(message=error)

class GetCommonInfo(APIView):
    def get(self, request):
        # res = add.delay(4,6)
        # print(res)
        form, error = JsonParser(
            Argument('id', ),
            Argument('item', default=None, required=False, ),
            Argument('filter', default=None, required=False, ),
        ).parse(request.GET)
        if error is None:
            inst = Instance.objects.filter(id=form.id).first()
            is_success, cur = connDb(inst.inst_ip, inst.db_user, inst.get_db_password,
                                     inst.db_port, service_name=inst.inst_name,
                                     database=inst.inst_name, type=inst.inst_type)
            if is_success == False:
                return json_response(message=cur)
            is_success, data = getcommonInfo(cur, form.item, form.filter)
            print(data)
            return json_response(data=data)
        else:
            return json_response(message=error)

class AddCluster(APIView):
    def post(self, request):
        form, error = JsonParser(
            Argument('cluster_name', ),
        ).parse(request.body)
        if error is None:
            cluster = Cluster(cluster_name=form.cluster_name)
            cluster.save()
            return json_response(data='群组添加完成！')

class GetOraCluster(APIView):
    def get(self,request):
        data = []
        insts = Instance.objects.filter(inst_type='Oracle',is_delete=0,
         cluster_id__gt = 0).values('cluster_id').distinct()
        clusterIdList = []
        for cluster in insts:
            clusterIdList.append(cluster['cluster_id'])
        clusters = Cluster.objects.filter(id__in=clusterIdList)
        for cluster in clusters:
            data.append({'label':cluster.cluster_name,'value':cluster.id})
        return json_response(data=data)

class GetCluster(APIView):
    def get(self,request):
        data = [{'label':'单实例','value':0}]
        clusters = Cluster.objects.all()
        for cluster in clusters:
            data.append({'label':cluster.cluster_name,'value':cluster.id})
        return json_response(data=data)

class GetClusterList(APIView):
    def post(self,request):
        form, error = JsonParser(
            Argument('inst_name', required=False,),
            Argument('inst_ip', required=False,),
            Argument('inst_apps', required=False,),
            Argument('cluster_id', required=False, ),
            Argument('page', default=1, type=int ,required=False,),
        ).parse(request.body)
        if error is None:
            insts = Instance.objects.filter(is_delete=0,inst_type='Oracle',
                                        cluster_id__gt = 0)
            _insts = insts
            if form.cluster_id and form.cluster_id != 'ALL':
                insts = insts.filter(cluster_id=form.cluster_id)
            if form.inst_name:
                _insts = _insts.filter(inst_name__contains=form.inst_name)
            if form.inst_ip:
                _insts = _insts.filter(inst_ip__contains=form.inst_ip)
            if form.inst_apps:
                _insts = _insts.filter(apps__contains=form.inst_apps)
            _insts = insts.values('cluster_id').distinct()
            clusterIdList = []
            for cluster in _insts:
                clusterIdList.append(cluster['cluster_id'])
            if clusterIdList:
                insts = insts.filter(cluster_id__in = clusterIdList)
            total = insts.count()
            insts = insts.values("id", "inst_ip", "inst_name", "inst_type", "db_status",
                                 "db_role", "cluster_id", "apps",
                                 "db_version")[(form.page - 1) * 10:form.page * 10]
            data = {
                'total': total,
                'data': list(insts)
            }
            return json_response(data)
        else:
            return json_response(message=error)

class ExecSql(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('id',),
            Argument('sql',),
            Argument('background', default='true'),
        ).parse(request.GET)
        if error is None:
            if form.background=='true':
                res = execSql.delay(form.id, form.sql)
                print('22222222222', res)
                return json_response(data='sql后台执行,任务号：' + str(res))
            inst = Instance.objects.filter(id=form.id).first()
            if inst:
                is_success, cur = connDb(inst.inst_ip, inst.db_user, inst.get_db_password,
                                         inst.db_port, service_name=inst.inst_name,
                                         database=inst.inst_name, type=inst.inst_type)
                if is_success == False:
                    return json_response(message=cur)
                sqlList = form.sql.split(';')
                for sql in sqlList:
                    # cur.execute(sql)
                    print(sql)
                return json_response(data='sql执行完毕！')
            else:
                return json_response(message='未查询到实例信息！')
        else:
            return json_response(message=error)

class GetClusterInsts(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('clusterId', ),
        ).parse(request.GET)
        if error is None:
            insts = Instance.objects.filter(is_delete=0,cluster_id=form.clusterId)
            insts = insts.values("id", "inst_ip", "inst_name", "inst_type", "db_status",
                                 "db_role", "cluster_id", "apps","db_version")
        else:
            return json_response(message=error)

class SwitchADG(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('switchtype', ),
            Argument('cluster_id', ),
        ).parse(request.GET)
        if error is None:
            print(form.cluster_id,form.switchtype)
            # time.sleep(10)
            data = [
                {'title':'步骤1','desc':'检查参数'},
                {'title': '步骤2', 'desc': '关闭主库节点2'},
                {'title': '步骤3', 'desc': '关闭主库节点2'},
                {'title': '步骤4', 'desc': '检查主库当前状态'},
                {'title': '步骤5', 'desc': '切换主库变备库'},
                {'title': '步骤6', 'desc': '切换备库变主库'},
                {'title': '步骤7', 'desc': '切换备库变主库'},
                    ]
            return json_response(data=data)
        else:
            return json_response(message=error)

class getCreateTspInfo(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('instId', ),
        ).parse(request.GET)
        if error is None:
            normalTsps = getInfo(form.instId,'getnormaltablespacenamesql')
            normalTspList = []
            for tsp in normalTsps:
                normalTspList.append({'label':tsp[0],'value':tsp[0]})
            tempTsps = getInfo(form.instId,'gettemptablespacenamesql')
            tempTspList = []
            for tsp in tempTsps:
                tempTspList.append({'label': tsp[0], 'value': tsp[0]})
            roles = getInfo(form.instId,'getrolesql')
            roleList = []
            for role in roles:
                roleList.append({'label': role[0], 'key': role[0],'disabled':False})
            users = getInfo(form.instId,'getusersql')
            userList = []
            for user in users:
                userList.append({'label': user[0], 'key': user[0],'disabled':False})
            return json_response(data={'normalTspList':normalTspList,'tempTspList':tempTspList,
                                       'roleList':roleList, 'userList':userList})

class GetMysqlInfo(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('id', ),
            Argument('item', ),
            Argument('filters', required=False,),
        ).parse(request.GET)
        if error is None:
            res = getMysqlInfo(form.id,form.item,(' and ' + form.filters) if form.filters else '')
            data = []
            for re in res:
                data.append({'label':re[0],'value':re[0]})
            if form.item == 'getbinlogs':
                data = getBinlogLastModifyTime(form.id,data)
            return json_response(data=data)
        else:
            return json_response(message=error)

class BinlogAnaly(APIView):
    def post(self, request):
        form, error = JsonParser(
            Argument('instId', ),
            Argument('startBinlog', ),
            Argument('endBinlog', required=False,),
            Argument('beginEndTime', required=False,),
            Argument('isFlashBack', ),
            Argument('isOnlyDml', ),
            Argument('dbs', required=False,),
            Argument('tables', required=False,),
            Argument('sqlType', required=False,),
        ).parse(request.body)
        if error is None:
            print(form.instId,form.startBinlog,form.endBinlog,form.beginEndTime,
                  form.isFlashBack,form.isOnlyDml,form.dbs,form.tables,form.sqlType)
            inst = Instance.objects.filter(id=form.instId).first()
            cmd = 'python3 /opt/binlog2sql-master/binlog2sql/binlog2sql.py -h%s -P%s -u%s -p\'%s\' --start-file=\'%s\' ' \
                  '--stop-file=\'%s\' ' % \
                  (inst.inst_ip, inst.db_port, inst.db_user, inst.get_db_password, form.startBinlog, form.endBinlog,)
            if form.beginEndTime:
                beginEndtimes = form.beginEndTime.strip('[').strip(']').split(',')
                cmd = cmd + '--start-datetime=\'%s\' --stop-datetime=\'%s\' ' % \
                      (beginEndtimes[0].replace('\'',''),beginEndtimes[1].replace('\'','').strip(' '))
            dbs = form.dbs.strip('[').strip(']').replace('\'','').split(',')
            if '' not in dbs:
                tmp = ' -d '
                for db in dbs:
                    tmp = tmp + db + ' '
                cmd = cmd + tmp
                tables = form.tables.strip('[').strip(']').replace('\'','').split(',')
                if '' not in tables:
                    tmp = ' -t '
                    for tab in tables:
                        tmp = tmp + tab + ' '
                    cmd = cmd + tmp
            sqlTypes = form.sqlType.strip('[').strip(']').replace('\'','').split(',')
            if '' not in sqlTypes:
                tmp = ' --sql-type '
                for type in sqlTypes:
                    tmp = tmp + type + ' '
                cmd = cmd + tmp
            if form.isOnlyDml == '1':
                cmd = cmd + ' --only-dml '
            if form.isFlashBack == '1':
                cmd = cmd + ' --flashback '
            print(cmd)
            data = os.popen(cmd).read()
            # print(data)
            return json_response(data=data)
        else:
            return json_response(message=error)

class SlowlogAnaly(APIView):
    def post(self, request):
        form, error = JsonParser(
            Argument('instId', ),
            Argument('beginEndTime', required=False, ),
            Argument('user', required=False, ),
        ).parse(request.body)
        if error is None:
            print(form.instId,form.beginEndTime,form.user)
            slowLog = getMysqlInfo(form.instId, 'getslowlog')[0][1]
            inst = Instance.objects.filter(id=form.instId).first()
            logName = '/tmp/slow_' + str(uuid.uuid1()) + '.log'
            cmd = ('scp -o "StrictHostKeyChecking no" -P %s  %s@%s:%s %s') % \
                  (str(inst.ssh_port), inst.ssh_user, inst.inst_ip, slowLog, logName)
            rs = os.system(cmd)
            print(rs)
            if rs == 0:
                cmd = 'pt-query-digest --limit=100% ' + logName
                if form.beginEndTime:
                    newtimes = str2List(form.beginEndTime)
                    cmd = cmd + ' --since \'%s\' --until \'%s\' ' % (newtimes[0],newtimes[1])
                if form.user:
                    cmd = cmd + ' --filter \'($event->{user} || "") =~ m/^%s/i\'' % form.user
                print(cmd)
                res = os.popen(cmd).read()
                print(res)
                if '# No events processed' in res:
                    return json_response(data='None')
                else:
                    return json_response(data=res)
            else:
                return json_response(message=rs)
        else:
            return json_response(message=error)

class Tailperform(APIView):
    """
        执行 tail_log  命令
    """
    def post(self, request):
        print('i am here !')
        mes = {'status': True, 'error': None, }
        try:
            channel_layer = get_channel_layer()
            user = 'mrjun'
            ssh = conn_paramiko('192.168.8.155',)
            stdin, stdout, stderr = ssh.exec_command('tail -1f /u01/app/oracle/diag/rdbms/orcldg/orcl/trace/alert_orcl.log', get_pty=True)
            # for i in range(10):
            #     print(i)
            #     time.sleep(1)
            #     result = {"status": 0, 'data': i}
            #     result_all = json.dumps(result)
            #     async_to_sync(channel_layer.group_send)\
            #         (user, {"type": "user.message", 'text': result_all})
            for line in iter(stdout.readline, ""):
                if os.environ.get("mrjun") == 'false':
                    break
                print('views:',line)
                if os.environ.get("mrjun") == 'false':
                    break
                result = {"status": 0, 'data': line}
                result_all = json.dumps(result)
                async_to_sync(channel_layer.group_send)(user, {"type": "user.message", 'text': result_all})
        except Exception as e:
            mes['status'] = False
            mes['error'] = "错误{0}".format(e)
            # logger.error(e)
        return json_response(message=mes)

class TestWS(APIView):
    def get(self, request):
        form, error = JsonParser(
            Argument('username', ),
        ).parse(request.GET)
        channel_layer = get_channel_layer()
        ssh = conn_paramiko('192.168.8.155', )
        stdin, stdout, stderr = ssh.exec_command(
            'tail -3f /u01/app/oracle/diag/rdbms/orcldg/orcl/trace/alert_orcl.log', get_pty=True)
        for line in iter(stdout.readline, ""):
            print(line)
            async_to_sync(channel_layer.group_send)(form.username,{"type": "log.message",
                                        'text':json.dumps({'status':True, 'data':line})})
        # i = 0
        # while i<2:
        #     async_to_sync(channel_layer.group_send)(form.username,
        #                      {"type": "log.message",'text': json.dumps({'status':True, 'data':i})})
        #     print(i)
        #     i += 1
        #     time.sleep(1)
        #     # test.delay(form.username,result_all)
        #     # channel_layer.group_send(form.username,{"type": "message",'text': result_all})
        # time.sleep(2)
        print('---------------finish')
        return json_response(data='mes')

