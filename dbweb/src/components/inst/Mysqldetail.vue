<template>
  <div>
    <el-tabs v-model="activeName" tab-position="top" type="border-card"  @tab-click="handleClick">
      <!--      在info中连接keepalived的切换-->
      <el-tab-pane label="基础信息" name="info">基础信息</el-tab-pane>
      <el-tab-pane label="会话统计" name="session">
        <el-row>
          <Mysqlactivesession :instId="this.instId" @showExecSql="ShowExecSql" ref="mysqlactivsession"></Mysqlactivesession>
        </el-row>
        <el-row>
          <el-col :span="13">
            <Mysqlconnsession :instId="this.instId" ref="mysqlconnsession"></Mysqlconnsession>
          </el-col>
          <el-col :span="10" style="margin-left: 15px">
            <Mysqlsourcesession :instId="this.instId" ref="mysqlresourcesession"></Mysqlsourcesession>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="锁查看" name="lock">
        <el-row>
          <Mysqllockwaite :instId="this.instId" @showExecSql="ShowExecSql" ref="mysqllockwaite"></Mysqllockwaite>
        </el-row>
        <el-row>
          <Mysqlblocklock :instId="this.instId" @showExecSql="ShowExecSql" ref="mysqlblockwaite"></Mysqlblocklock>
        </el-row>
        <el-row>
          <Mysqlinfolock :instId="this.instId" ref="mysqlinfolock"></Mysqlinfolock>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="用户" name="user">
        <el-row :gutter="20">
          <Mysqlusers :instId="this.instId" :dbRole="this.dbRole" @showExecSql="ShowExecSql" ref="mysqlusers"></Mysqlusers>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="库操作" name="database">
        <el-row :gutter="20">
          <Mysqldatabases :instId="this.instId" :dbRole="this.dbRole" @showExecSql="ShowExecSql" ref="mysqldatabases"></Mysqldatabases>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="对象大小统计" name="object">
        <el-row>
          <Mysqldbsize :instId="this.instId" ref="mysqldbsize"></Mysqldbsize>
        </el-row>
        <el-row>
          <Mysqltablesize :instId="this.instId" ref="mysqltablesize"></Mysqltablesize>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="慢sql" name="slow">
        <el-row>
          <Mysqlslowsql :instId="this.instId" ref="mysqlslowsql"></Mysqlslowsql>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="binlog解析" name="binlog">
        <Mysqlbinlog :instId="this.instId" ref="binlogsql"></Mysqlbinlog>
      </el-tab-pane>
    </el-tabs>

    <!--sql执行提示界面-->
    <el-dialog title="SQL执行" visible v-if="dialogExecSqlShow" @close="dialogExecSqlShow = false"
               :close-on-click-modal="false" width="50%" append-to-body>
      <div v-html="execSql"></div>
      <div slot="footer" style="text-align: center">
        <el-button type="text" @click.native="dialogExecSqlShow = false">取消</el-button>
        <el-button type="info" v-clipboard:copy="execSql.replaceAll('<br/>','\n')"
                   v-clipboard:success="onCopy"
                   v-clipboard:error="onError">复制
        </el-button>
        <el-button type="danger" v-loading="execLoading" @click.once="onSubumit()">直接执行</el-button>
      </div>
    </el-dialog>

    <!--sql执行过程界面-->
    <el-dialog title="SQL执行日志" :visible.sync="dialogVisible" width="70%"
               :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false" center>
      <el-row>
        <span style="font-size: 16px;font-weight: 700;">执行进度条：</span>
        <el-progress :percentage="percentage"></el-progress>
      </el-row>

      <el-table :data="execSQLTableData" style="width: 100%;" border>
        <el-table-column prop="sql" label="SQL"></el-table-column>
        <el-table-column prop="reason" label="失败原因" width="160"></el-table-column>
        <el-table-column prop="status" label="执行状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status == 'Successed' ?  'success' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" :disabled="bntExecSql" @click.native="closeExecDialog(finished)">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import Mysqlslowsql from './Mysqlslowsql';
  import Mysqlbinlog from './Mysqlbinlog';
  import Mysqlactivesession from './Mysqlactivesession';
  import Mysqlconnsession from './Mysqlconnsession';
  import Mysqlsourcesession from './Mysqlsourcesession';
  import Mysqllockwaite from './Mysqllockwaite';
  import Mysqlinfolock from './Mysqlinfolock';
  import Mysqlblocklock from './Mysqlblocklock';
  import Mysqlusers from "./Mysqlusers";
  import Mysqldatabases from './Mysqldatabases';
  import Mysqldbsize from './Mysqldbsize';
  import Mysqltablesize from './Mysqltablesize';

  export default {
    components:{
      Mysqlusers, Mysqlslowsql, Mysqlbinlog, Mysqlactivesession, Mysqlconnsession, Mysqlsourcesession,
      Mysqllockwaite, Mysqlinfolock, Mysqlblocklock, Mysqldatabases, Mysqldbsize, Mysqltablesize},
    data () {
      return {
        instId:this.$route.query.instId,
        dbRole:this.$route.query.dbRole,
        bntExecSql: false,
        wsServer: '',
        activeName: 'info',
        execSQLTableData:[],
        dialogVisible:false,
        taskId:'testid',
        finished: false,
        socket:'',

        dialogExecSqlShow: false,
        execSql: '',
        execLoading: false,
        percentage:0,

        sessionStatus: true,
        lockStatus: true,
        userStatus: true,
        databaseStatus: true,
        objectStatus: true,
      }
    },
    mounted () {
      this.wsServer = this.common.getWsServer();
    },
    methods: {
      //tab切换方法
      handleClick(tab, event) {
        if (this.activeName == 'binlog'){
          this.$refs.binlogsql.getBinLogs();
          this.$refs.binlogsql.getDbs();
        }else if(this.activeName == 'slow'){
          this.$refs.mysqlslowsql.getUsers();
        }else if(this.activeName == 'session'){
          if (this.sessionStatus) {
            this.sessionStatus = false;
            this.$refs.mysqlconnsession.getConnSession();
            this.$refs.mysqlresourcesession.getResourceSession();
            this.$refs.mysqlactivsession.getActiveSessions();
          }
        }else if (this.activeName == 'lock'){
          if (this.lockStatus) {
            this.lockStatus = false;
            this.$refs.mysqllockwaite.getLocks();
            this.$refs.mysqlinfolock.getBlocks();
            this.$refs.mysqlblockwaite.getBlocks();
          }
        }else if (this.activeName == 'user'){
          if (this.userStatus) {
            this.userStatus = false;
            this.$refs.mysqlusers.getUsers();
          }
        }else if (this.activeName == 'database'){
          if (this.databaseStatus) {
            this.databaseStatus = false;
            this.$refs.mysqldatabases.getDatabases();
          }
        }else if(this.activeName == 'object'){
          if(this.objectStatus){
            this.objectStatus = false;
            this.$refs.mysqldbsize.getDbSize();
            this.$refs.mysqltablesize.getTableSize();
          }
        }
        console.log(tab, event);
      },
      //显示执行sql详情
      ShowExecSql(data){
        this.execSql = data
        this.dialogExecSqlShow = true
      },
      //复制成功
      onCopy(){
        this.$message.success('复制成功')
      },
      //复制失败
      onError(){
        this.$message.console.error('复制失败');
      },
      //关闭执行日志窗口
      closeExecDialog(status){
        console.log(status);
        console.log(this.finished);
        if (!this.finished){
          this.$message({
            type: 'success',
            message: '如果执行未完成，SQL会在后台继续执行，可通过 '+ this.taskId +' 在任务页面查看最终执行结果。'
          });
        };
        this.dialogVisible = false;
        this.dialogExecSqlShow = false;
        this.socket.close();
        // this.reflashTab(this.activeName);
      },
      //执行sql
      onSubumit(){
        this.bntExecSql = true;
        this.dialogVisible = true;
        this.percentage = 0;
        // 清空消息
        this.execSQLTableData = []
        // 执行webSocket
        this.webSocket()
      },
      webSocket() {
        const _this = this;
        if (typeof (WebSocket) == 'undefined') {
          this.$notify({
            title: '提示',
            message: '当前浏览器无法接收实时报警信息，请使用谷歌浏览器！',
            type: 'warning',
            duration: 0
          });
        } else {
          const socketUrl = _this.wsServer + '/ws/execsql/' + localStorage.getItem('login_user') +'/';
          console.log(socketUrl)
          this.socket = new WebSocket(socketUrl);
          // 监听socket打开
          this.socket.onopen = function() {
            console.log('浏览器WebSocket已打开');
            //发送字符:
            _this.socket.send(JSON.stringify({
              'id': _this.instId,
              'sql': _this.execSql,
              'username': localStorage.getItem('login_user'),
            }));
          };
          // 监听socket消息接收
          this.socket.onmessage = function(msg) {
            // 追加到内容显示列表中
            var data = msg.data
            console.log('i am here')
            console.log(data)
            if(data == 'END'){
              _this.finished = true;
              _this.bntExecSql = false;
            }else if(data.search("Connect the database error") != -1){
              _this.finished = true;
              _this.bntExecSql = false;
              _this.$message({
                type: 'error',
                message: data
              });
            }else{
              var tabledate = eval('('+data+')')
              _this.execSQLTableData.push(tabledate)
              _this.percentage = tabledate.pct
            }
          };
          // 监听socket错误
          this.socket.onerror = function() {
            if(!this.finished){
              this.$message({
                type: 'success',
                message: '如果执行未完成，SQL会在后台继续执行，可通过 '+ this.taskId +' 在任务页面查看最终执行结果。'
              });
              this.dialogVisible = false;
            }
          };
          // 监听socket关闭
          this.socket.onclose = function() {
            console.log('WebSocket已关闭');
          };
        }
      },
    },
    watch:{
      //监控页面切换
      activeName:function(newVal, oldVal) {
        if(newVal!='session' && oldVal == 'session'){
          this.$refs.mysqlactivsession.autoReflashClick(true);
        }else if(newVal!='lock' && oldVal == 'lock'){
          this.$refs.mysqllockwaite.autoReflashClick(true);
          this.$refs.mysqlinfolock.autoReflashClick(true);
          this.$refs.mysqlblockwaite.autoReflashClick(true);
        }
      }
    },
  }

</script>
