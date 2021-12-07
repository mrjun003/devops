import cx_Oracle
import MySQLdb
from .utils import toDic,cutList
import configparser
import os,time
from inst.models import *

#连接数据库
def connDb2(instId):
    try:
        inst = Instance.objects.filter(id=instId).first()
        if inst.inst_type == 'Oracle':
            conn = cx_Oracle.connect('%s/%s@%s:%s/%s' % (inst.db_user,
                        inst.get_db_password, inst.inst_ip,inst.db_port, inst.inst_name))
        else:
            conn = MySQLdb.connect(inst.inst_ip, inst.db_user, inst.get_db_password,
                                   'information_schema', port=int(inst.db_port), charset='utf8')
        cur = conn.cursor()
        return True, cur
    except Exception as e:
        return False, str(e)

def connDb(ip, user, password, port, service_name=None, database='mysql', type='Oracle' ,charset='utf8'):
    try:
        if type == 'Oracle':
            conn = cx_Oracle.connect('%s/%s@%s:%s/%s' % (user, password, ip, port, service_name))
        elif type in ('Mysql','Rds'):
            conn = MySQLdb.connect(ip, user, password, database, port=int(port), charset=charset)
        cur = conn.cursor()
        return True, cur
    except Exception as e:
        print(str(e))
        return False, str(e)

#获取数据库基础信息
def getDbBaseInfo(cur ,type='Oracle'):
    if type=='Oracle':
        ver_sql = "select version from v$instance"
        role_sql = "select database_role from v$database"
        cur.execute(role_sql)
        db_role = cur.fetchone()[0]
        # clus_sql = "SELECT value FROM v$parameter where name = 'cluster_database'"
        # cur.execute(clus_sql)
    elif type in ('Mysql','Rds'):
        ver_sql = "SELECT version()"
        role_sql = "show variables like 'read_only';"
        cur.execute(role_sql)
        db_role = 'Master' if cur.fetchone()[1] == 'OFF' else 'Slave'
    cur.execute(ver_sql)
    version = cur.fetchone()[0]
    cur.close()
    return version ,db_role

#获取oracle数据库信息
def getDbinfo(inst_type ,tab ,cur ,item=None, filter=None):
    try:
        data = {}
        if inst_type == 'Oracle':
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
            orgList = config.options(tab)
            if item == None:
                [sqlList, nameList, dataList] = cutList(orgList, 3)
                i = 0
                for sql in sqlList:
                # print(config.get(tab, sql))
                    cur.execute(config.get(tab, sql).replace('$$$',''))
                    tempList = cur.fetchall()
                    data[dataList[i]] = toDic(config.get(tab, nameList[i]).split(','), tempList)
                    i = i + 1
            else:
                if filter == None:
                    cur.execute(config.get(tab, item[0]).replace('$$$',''))
                else:
                    cur.execute(config.get(tab, item[0]).replace('$$$', filter))
                    # time.sleep(10)
                tempList = cur.fetchall()
                data[config.get(tab, item[2])] = toDic(config.get(tab, item[1]).split(','), tempList)
            # print(data)
        else:
            pass
        return True, data
    except Exception as e:
        print(str(e))
        return False, str(e)

#获取mysql数据库信息
def getMlInfo(instId,item,filter=None):
    try:
        conn , cur = connDb2(instId)
        if conn:
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.abspath('.'), 'libs/mysqlinfo.ini'))
            if filter == None:
                cur.execute(config.get(item, 'sql').replace('$$$', ''))
            else:
                cur.execute(config.get(item, 'sql').replace('$$$', filter))
            tempList = cur.fetchall()
            data = {item:toDic(config.get(item, 'namelist').split(','), tempList)}
            return True, data
        else:
            return False, cur
    except Exception as e:
        print(str(e))
        return False, str(e)


#获取数据库某些信息
def getcommonInfo(cur,item,filter=None):
    try:
        data={}
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        if filter == None:
            cur.execute(config.get('common', item + 'sql'))
        else:
            cur.execute(config.get('common', item + 'sql').replace('$$$',' and ' + filter))
        tempList = cur.fetchall()
        data[config.get('common', item + 'data')] = \
            toDic(config.get('common', item + 'namelist').split(','), tempList)
        return True, data
    except Exception as e:
        print(str(e))
        return False, str(e)

#ADG切换完成改变数据库角色
def changeDbRole(culsterId):
    pdbs = Instance.objects.filter(cluster_id=culsterId, is_delete=0,
                                   db_role='PRIMARY').values('id')
    sdbs = Instance.objects.filter(cluster_id=culsterId, is_delete=0,
                                   db_role='PHYSICAL STANDBY').values('id')
    pdbsList = []
    sdbsList = []
    for db in pdbs:
        pdbsList.append(db['id'])
    for db in sdbs:
        sdbsList.append(db['id'])
    for id in pdbsList:
        Instance.objects.filter(id=id).update(db_role='PHYSICAL STANDBY')
    for id in sdbsList:
        Instance.objects.filter(id=id).update(db_role='PRIMARY')

#当备库和主库有多个节点时关闭多余节点
def closeDb(culsterId,dbRole):
    pass

#获取数据库alter日志文件
def getAlertLog(instId):
    conn , cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        cur.execute(config.get('common', 'getalertsql'))
        alertFile = cur.fetchone()[0]
        return alertFile
    else:
        return None

#判断数据库是否开启日志应用节点
def getMrp(instId):
    conn , cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        cur.execute(config.get('common', 'getmrpsql'))
        if cur.fetchone():
            return True
    else:
        return None

#ADG主备参数设置
def getParam(instId):
    conn, cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        cur.execute(config.get('common', 'getparamsql'))
        data = {}
        data['param'] = cur.fetchall()
        cur.execute(config.get('common', 'getredologsql'))
        data['redolog'] = cur.fetchall()
        cur.execute(config.get('common', 'getstandbylogsql'))
        data['standbylog'] = cur.fetchall()
        return data
    else:
        return None

#获取ADG状态
def getStatus(instId):
    conn, cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        cur.execute(config.get('common', 'checkadgstatssql'))
        for res in cur.fetchall():
            print(res)
        cur.execute(config.get('common', 'checkmrgsql'))
        for res in cur.fetchall():
            print(res)
        return None
    else:
        return None

#获取ADG是否可切换
def getSwitchoverStatus(instId):
    conn, cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        res = cur.execute(config.get('common', 'checksql')).fetchone()
        if res[0] in ('TO PRIMARY','SESSIONS ACTIVE'):
            return True
        else:
            return False
    else:
        return None

#检查数据库是否存活
def checkDatabaseExist(instId,instType):
    conn, cur = connDb2(instId)
    if conn:
        if instType=='Oracle':
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
            checkSql = config.get('common', 'checkdatabaseexsitsql')
            res = cur.execute(checkSql).fetchone()
            return res[0]
        elif instType=='Mysql':
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.abspath('.'), 'libs/mysqlinfo.ini'))
            checkSql = config.get('common', 'checkdatabaseexsitsql')
            res = cur.execute(checkSql)
            return res
    else:
        return cur

#获取指定信息
def getInfo(instId,item):
    conn, cur = connDb2(instId)
    if conn:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
        cur.execute(config.get('common', item))
        res = cur.fetchall()
        return res
    else:
        return conn

#获取mysql相关信息
def getMysqlInfo(instId,item,firters=''):
    inst = Instance.objects.filter(id=instId).first()
    is_success, cur = connDb(inst.inst_ip, inst.db_user, inst.get_db_password,
                             inst.db_port, service_name=inst.inst_name,
                             database=inst.inst_name, type=inst.inst_type)
    if is_success:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'libs/mysqlinfo.ini'))
        cur.execute(config.get('common', item) + firters)
        res = cur.fetchall()
        return res
    else:
        return is_success