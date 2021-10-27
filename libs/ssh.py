import multiprocessing
import paramiko
import os
import time
# import subprocess
#import nmap
import argparse
import socket
import sys
from threading import Thread
from .utils import isExist

PingHost=""
''' ssh-keygen 命令 '''
keygenCmd="ssh-keygen -q -t rsa -P '' -f ~/.ssh/id_rsa && echo yes || echo no"
''' 读取pub文件 '''
readPubCmd="test -f ~/.ssh/id_rsa.pub && cat ~/.ssh/id_rsa.pub || echo"
''' 查看pub文件是否存在 '''
testExistsCmd="test -f ~/.ssh/id_rsa.pub && echo yes || echo no"
''' 追加公钥至authorized_keys中'''
addKeyCmd="echo %s >> ~/.ssh/authorized_keys && echo yes || echo no"
'''进程数'''
Pnum=multiprocessing.cpu_count()

class MyThread(Thread):
    def __init__(self, tname, exec_name,Host_info_list):
        Thread.__init__(self, name = tname)
        self.IsRunning = False
        self.hostList=Host_info_list
        self.ssh_cmd=exec_name
        self.result=[]
    # 执行函数，进行计算
    def run(self):
        self.IsRunning = True;
        host_list=self.hostList[0]
        newList=[] if len(self.hostList[1:])==0 else self.hostList[1:]
        for host_info in host_list:
            newList.insert(0,host_info)
            res=self.ssh_cmd(newList)
            self.result.append(res)
            del(newList[0])
        self.IsRunning = False;
    # 线程退出函数
    def ExitThread(self):
        sys.exit(0)
    def get_result(self):
        if len(self.result)!=0:
            return self.result
        else:
            return []

#socket检查服务器存活
def checkHostExist(ip,port):
    # hostinfo=flist[0]
    hostip=ip
    port=port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((hostip,int(port)))
        s.settimeout(2)
        # print("%s\t处于活跃状态"%ip)
        return [ip,True]
    except:
        # print("%s\t连接错误，服务器可能关闭"%ip)
        return [ip,False]
    #扫描服务器开放的端口

#paramiko连接
def connHost(ip, user, password=None, port=22, id_rsa_file='~/.ssh/id_rsa'):
    try:
        ssh = paramiko.SSHClient()
        if password != None:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=port, username=user, password=password)
        else:
            pkey = paramiko.RSAKey.from_private_key_file(id_rsa_file,)
            ssh.connect(hostname=ip, port=port, username=user, pkey=pkey)
        return True ,ssh
    except Exception as e:
        return False ,str(e)

#配置服务到主机的免密
def configAuthorized(ip, user, password, port=22):
    try:
        is_exist = os.popen(testExistsCmd).read().replace('\n','')
        if is_exist == 'no':
            os.popen(keygenCmd).read().replace('\n','')
        is_success,ssh = connHost(ip ,user ,password ,port)
        if is_success == True:
            if user == 'root':
                authorized_keys_dir = '/root/.ssh/'
            else:
                authorized_keys_dir = '/home/%s/.ssh/' % user
            stdin, stdout, stderr = ssh.exec_command('test -d %s && echo yes || echo no'
                                                     % authorized_keys_dir)
            if stdout.read().decode('utf-8').replace('\n','') == 'no':
                stdin, stdout, stderr = ssh.exec_command('mkdir -p %s' % authorized_keys_dir)
            pub_key = os.popen('cat ~/.ssh/id_rsa.pub || echo').read().replace('\n','')
            stdin, stdout, stderr = ssh.exec_command('echo %s >> %sauthorized_keys' % (pub_key ,authorized_keys_dir))
            ssh.close()
            return True
        else:
            return ssh
    except Exception as e:
        return str(e)

    #初始化ssh连接


def init_ssh():
    server = paramiko.SSHClient()
    server.load_system_host_keys()
    server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return server
#执行命令
def ssh_cmd(host_info_cd):
    try:
        host_info=host_info_cd[0]
        cmd=host_info_cd[1][0]
        server=host_info_cd[1][1]
        ip,username,password,port= host_info[0],host_info[1],host_info[2],host_info[3]
        #print("%s 开始执行命令%s"%(ip,cmd))
        server.connect(ip,int(port),username,password,timeout=5)
        stdin,stdout,stderr = server.exec_command(cmd)
        result=[host_info,(stdout.read().decode('utf-8')).replace('\n','')]
        return result
    except Exception as e:
        print(e)
        return [host_info,'error']
#批量执行命令
def run_cmd(host_info,cargs):
    result=[]
    rpod=split_job(host_info)
    rJob=[]
    for i in range(0,len(rpod)):
        t=MyThread(i,ssh_cmd,[rpod[i],cargs])
        t.setDaemon(True)
        t.start()
        rJob.append(t)
    for i in rJob:
        i.join()
    for i in rJob:
        result+=i.get_result()
    return result
#任务分组
def split_job(items):
    n=Pnum
    return [items[i:i+n] for i in range(0, len(items), n)]
#获取公匙
def GetPublicKey(host_info,cargs):
    existAkeyList=run_cmd(host_info,cargs)
    #未存在公匙的
    nokey=[]
    #已经存在公匙集合
    AllKey=[]
    for i in existAkeyList:
        if len(i)>1:
            if i[1]!='error':
                if len(i[1])>0:
                    AllKey.append(i)
                else:
                    nokey.append(i[0])
        else:
            nokey.append(i[0])
    return nokey,AllKey
def write_key(write_List,keys,server):
    addcmd=addKeyCmd%(keys)
    writeResult=run_cmd(write_List,[addcmd,server])
    for i in writeResult:
        if len(i)>1:
            if i[1]!='error':
                if i[1]=='yes':
                    print(i[0][0],"互信完成")
                else:
                    print(i[0][0],"互信失败，请手动检查")
#Linux 服务器互信
def AuthSShKey(file):
    if not os.path.exists(file):
        print("请检查输入文件路径是否正确,将在5s后退出")
        time.sleep(2)
        sys.exit()
    Ilist=[]
    action_host=[]
    noaction_host=[]
    with open(file,'r') as f:
        for i in f.readlines():
            line=i.strip().split(' ')
            if len(line)==4:
                Ilist.append(line)
    if len(Ilist)==0:
        print("请检查文件是否为空文件，或者确认文件内容格式是否正确")
        time.sleep(3)
        sys.exit()
    az=split_job(Ilist)
    aresult=[]
    pid=[]
    for i in range(0,len(az)):
        Tpod=MyThread(i,checkHostExist,[az[i]])
        Tpod.setDaemon(True)
        Tpod.start()
        pid.append(Tpod)
    for i in pid:
        i.join()
    for i in pid:
        aresult+=i.get_result()
    for res in aresult:
        if res[1]:
            action_host.append(res[0])
        else:
            noaction_host.append(res[0])
    print("存活服务器%s\n"%[i[0] for i in action_host])

    print("未存活服务器%s\n"%[i[0] for i in noaction_host])
    if len(action_host)==0:
        print("没有检测到存活机器,程序结束")
        sys.exit(0)
    server=init_ssh()
      #开始为没有公匙的服务器创建公匙
    nokey,Allkey=GetPublicKey(action_host,[readPubCmd,server])
    if len(Allkey)>0:
        for i in Allkey:
            print(i[0][0],"已经获得key")
    if len(nokey)>0:
        for i in nokey:
            print(i[0],'未检测到key')
        print("开始为没有公匙的服务器创建公匙")
        createKey=run_cmd(nokey,[keygenCmd,server])
        error_createList=[]
    #新创建公匙列表
        new_keyList=[]
        for i in createKey:
            if i[1]!='error':
                if i[1]=='yes':
                    print(i[0][0],"key创建成功")
                    new_keyList.append(i[0])
            else:
                error_createList.append(i[0])
        nokey,newAllkey=GetPublicKey(new_keyList,[readPubCmd,server])
        Allkeys=[keys[1] for keys in Allkey]+[keys[1] for keys in newAllkey]
        write_List=[keys[0] for keys in Allkey]+[keys[0] for keys in newAllkey]
        print("开始写入key")
        for kcs in Allkeys:
            write_key(write_List,kcs,server)
    else:
        write_List=[key[0] for key in Allkey]
        Allkeys=[keys[1] for keys in Allkey]
        for kcs in Allkeys:
            write_key(write_List,kcs,server)
    print("程序执行完毕，将在5s后退出")
    time.sleep(5)
# if __name__=='__main__':
#     multiprocessing.freeze_support()
#     paras=argparse.ArgumentParser()
#     #paras.add_argument('-H',dest="help",help="目前本脚本支持做linux服务器互信，做服务器端口扫描，端口扫描分为制定端口扫描，全部端口扫描,其中参数-A -L 单独使用，-I -P 组合使用")
#     paras.add_argument('-L',dest="HostListFile",help="HostListFilePath like : /home/test/1.txt ,\n 文件内容由 (host    username    password    port)一行一个服务器信息,由' '隔开(一个空格)")
#     #paras.add_argument('-I',dest="IP",nargs='+',help="IP like: 192.168.1.1")
#     #paras.add_argument('-P',dest="Port",nargs="+",type=int,help="Port like: 3306")
#     #paras.add_argument('-A',dest="AllPortScan",help="Port like: 192.168.1.1 (scan 1-65536)")
#     args=paras.parse_args()
#     Arlist={}
#     for i,k in args.__dict__.items():
#         if k!=None:
#             Arlist[i]=k
#     #print(Arlist)
#     if len(Arlist)>2:
#         print("请查看帮助 %s -h"%sys.argv[0])
#         sys.exit()
#     #elif len(Arlist)==2:
#     #    if "Port" in Arlist and "IP" in Arlist:
#     #        pass
#     #    else:
#     #        pass
#     elif len(Arlist)==1:
#         if "HostListFile" in Arlist or "AllPortScan" in Arlist:
#             if "HostListFile"  in Arlist.keys():
#                 if os.path.exists(Arlist['HostListFile']) and os.path.isfile(Arlist['HostListFile']):
#                     AuthSShKey(Arlist['HostListFile'])
#     else:
#         filepath=input("请输入服务器信息文件(如果不知道格式请查看本脚本帮助提示，-h):")
#         AuthSShKey(filepath)