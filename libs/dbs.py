import cx_Oracle
import MySQLdb
from .utils import toDic,cutList
import configparser
import os

#连接数据库
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
        clus_sql = "SELECT value FROM v$parameter where name = 'cluster_database'"
        cur.execute(clus_sql)
        is_cluster = False if cur.fetchone()[0] == 'FALSE' else True
    elif type in ('Mysql','Rds'):
        ver_sql = "SELECT version()"
        role_sql = "show variables like 'read_only';"
        cur.execute(role_sql)
        db_role = 'Master' if cur.fetchone()[1] == 'OFF' else 'Slave'
        is_cluster = True
    cur.execute(ver_sql)
    version = cur.fetchone()[0]
    if is_cluster == True:
        cluster_id = '111111111111'
    else:
        cluster_id = '00000000000'
    cur.close()
    return version ,db_role ,is_cluster ,cluster_id

#获取数据库信息
def getDbinfo(inst_type ,tab ,cur):
    try:
        data = {}
        if inst_type == 'Oracle':
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.abspath('.'), 'libs/orainfo.ini'))
            orgList = config.options(tab)
            [sqlList, nameList, dataList] = cutList(orgList, 3)
            i = 0
            for sql in sqlList:
                # print(config.get(tab, sql))
                cur.execute(config.get(tab, sql))
                tempList = cur.fetchall()
                data[dataList[i]] = toDic(config.get(tab, nameList[i]).split(','), tempList)
                i = i + 1
            print(data)
        else:
            pass
        return True, data
    except Exception as e:
        print(str(e))
        return False, str(e)
