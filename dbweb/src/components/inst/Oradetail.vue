<template>
  <div>
    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="基本信息" name="info">
        <OrabaseInfo :instId="this.instId" ref="orabaseinfo"></OrabaseInfo>
      </el-tab-pane>
      <el-tab-pane label="会话统计" name="session">
        <el-row>
          <Oraactivsession :instId="this.instId" @showExecSql="ShowExecSql" ref="oraactivsession"></Oraactivsession>
        </el-row>
        <el-row>
          <el-col :span="13">
            <Oraconnsession :instId="this.instId" ref="oraconnsession"></Oraconnsession>
          </el-col>
          <el-col :span="10" style="margin-left: 15px">
            <Oraresourcesession :instId="this.instId" ref="oraresourcesession"></Oraresourcesession>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="锁查看" name="lock">
        <el-row>
          <Oralockwaite :instId="this.instId" @showExecSql="ShowExecSql" ref="oralockwaite"></Oralockwaite>
        </el-row>
        <el-row>
          <Orablocksession :instId="this.instId" @showExecSql="ShowExecSql" ref="orablockwaite"></Orablocksession>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="用户" name="user">
        <el-row :gutter="20">
          <Orausers :instId="this.instId" :dbRole="this.dbRole" @showExecSql="ShowExecSql" ref="orausers"></Orausers>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="表空间查看" name="tablespace">
        <el-row>
          <Oratablespace :instId="this.instId" :dbRole="this.dbRole" @showExecSql="ShowExecSql" ref="oratablespace"></Oratablespace>
        </el-row>
        <el-row>
          <Oradatafilesize :instId="this.instId" :dbRole="this.dbRole" @showExecSql="ShowExecSql" ref="oradatafilesize"></Oradatafilesize>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="对象统计" name="object">
        <el-row>
          <el-col :span="15">
            <oraobjectsize :instId="this.instId" ref="oraobjectsize"></oraobjectsize>
          </el-col>
          <el-col :span="8" style="margin-left: 15px">
            <orausersize :instId="this.instId" ref="orausersize"></orausersize>
          </el-col>
        </el-row>
        <el-row>
          <oraparttabsize :instId="this.instId" ref="oraparttabsize"></oraparttabsize>
        </el-row>
        <el-row>
          <Oratabchip :instId="this.instId" ref="oratabchip"></Oratabchip>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="统计信息" name="statics">
        <el-row>
          <Oratabstatics :instId="this.instId" ref="oratabstatics"></Oratabstatics>
        </el-row>
        <el-row>
          <OraIndstatics :instId="this.instId" ref="oraindstatics"></OraIndstatics>
        </el-row>
        <el-row>
          <Orastale :instId="this.instId" ref="orastale"></Orastale>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="归档统计" name="archive">
        <el-row>
          <el-col :span="12">
            <Oraarchday :instId="this.instId" ref="oraarchday"></Oraarchday>
          </el-col>
          <el-col :span="11" style="margin-left: 15px;">
            <Oraarchhour :instId="this.instId" ref="oraarchhour"></Oraarchhour>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="慢sql" name="slow">
        <el-row>
          <Oraslowsql :instId="this.instId" ref="oraslowsql"></Oraslowsql>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="rman备份" name="rman">
        <el-row>
          <Orarmanbackup :instId="this.instId" ref="orarmanbackup"></Orarmanbackup>
        </el-row>
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
  import OrabaseInfo from './Orabaseinfo.vue';
  import Orausers from "./Orausers";
  import Oraactivsession from "./Oraactivsession";
  import Oraconnsession from "./Oraconnsession";
  import Oraresourcesession from "./Oraresourcesession";
  import Oralockwaite from "./Oralockwaite";
  import Orablocksession from "./Orablocksession";
  import Oratablespace from "./Oratablespace";
  import Orarmanbackup from "./Orarmanbackup";
  import Oraslowsql from "./Oraslowsql";
  import Oraarchday from "./Oraarchday";
  import Oraarchhour from "./Oraarchhour";
  import Oraobjectsize from "./Oraobjectsize";
  import Orausersize from "./Orausersize";
  import Oraparttabsize from "./Oraparttabsize";
  import Oratabchip from "./Oratabchip";
  import Oratabstatics from "./Oratabstatics";
  import OraIndstatics from "./OraIndstatics";
  import Orastale from "./Orastale";
  import Oradatafilesize from "./Oradatafilesize";
  export default {
    components:{Oraresourcesession, OrabaseInfo, Orausers, Oraactivsession, Oraslowsql, Oraarchday,
      Oraconnsession, Oralockwaite, Orablocksession, Oratablespace, Orarmanbackup, Oraarchhour, Oraobjectsize,
      Orausersize, Oraparttabsize, Oratabchip, Oratabstatics, OraIndstatics, Orastale, Oradatafilesize},
    data(){
      return{
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

        userStatus: true,
        sessionStatus: true,
        lockStatus: true,
        tablespaceStatus: true,
        objectStatus: true,
        staticsStatus: true,
        archSratus: true,
        slowsqlStatus: true,
        rmanStatus: true,
      };
    },
    methods: {
      //切换页面
      handleClick(tab, event) {
        if (this.activeName == 'user'){
          if (this.userStatus) {
            this.userStatus = false;
            this.$refs.orausers.getUsers();
          }
        }else if (this.activeName == 'session') {
          if (this.sessionStatus) {
            this.sessionStatus = false;
            this.$refs.oraconnsession.getConnSession();
            this.$refs.oraresourcesession.getResourceSession();
            this.$refs.oraactivsession.getActiveSessions();
          }
        }else if (this.activeName == 'lock'){
          if (this.lockStatus) {
            this.lockStatus = false;
            this.$refs.oralockwaite.getLocks();
            this.$refs.orablockwaite.getBlocks();
          }
        }else if(this.activeName == 'tablespace'){
          if(this.tablespaceStatus){
            this.tablespaceStatus = false;
            this.$refs.oratablespace.getTablespaceUsed();
            this.$refs.oradatafilesize.getDataFile();
          }
        }else if(this.activeName == 'rman'){
          if(this.rmanStatus){
            this.rmanStatus = false;
            this.$refs.orarmanbackup.getRmanInfo();
          }
        }else if(this.activeName == 'slow'){
          if(this.slowsqlStatus){
            this.slowsqlStatus = false;
            this.$refs.oraslowsql.getSlowSql();
          }
        }else if(this.activeName == 'archive'){
          if(this.archSratus){
            this.archSratus = false;
            this.$refs.oraarchday.getArchDay();
            this.$refs.oraarchhour.getArchHour();
          }
        }else if (this.activeName == 'object'){
          if(this.objectStatus){
            this.$refs.oraobjectsize.getObjectSize();
            this.$refs.orausersize.getUserSize();
            this.$refs.oraparttabsize.getParttabSize();
            this.$refs.oratabchip.getTabChip();
          }
        }else if (this.activeName == 'statics'){
          if(this.staticsStatus){
            this.$refs.oratabstatics.getTabStatics();
            this.$refs.oraindstatics.getIndStatics();
            this.$refs.orastale.getStale();
          }
        }
      },
      //刷新tab
      // reflashTab(tab){
      //   if(this.activeName == 'tablespace'){
      //     this.$refs.oratablespace.reflashClick();
      //     this.$refs.oradatafilesize.reflashClick();
      //   }else if(this.activeName == 'lock'){
      //     this.$refs.oralockwaite.reflashClick();
      //     this.$refs.orablockwaite.reflashClick();
      //   }else if(this.activeName == 'session'){
      //     this.$refs.oraconnsession.reflashClick();
      //     this.$refs.oraresourcesession.reflashClick();
      //     this.$refs.oraactivsession.reflashClick();
      //   }else if(this.activeName == 'user'){
      //     this.$refs.orausers.reflashClick();
      //   }
      // },
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
          // var room_name = this.common.uuid(8,16)
          // 实例化socket
          // const socketUrl = 'ws://192.168.8.152:8000/ws/execsql/' + localStorage.getItem('login_user') +'/';
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
          this.$refs.oraactivsession.autoReflashClick(true);
        }else if(newVal!='lock' && oldVal == 'lock'){
          this.$refs.oralockwaite.autoReflashClick(true);
          this.$refs.orablockwaite.autoReflashClick(true);
        }
      }
    },
    mounted() {
      this.$refs.orabaseinfo.getDatabaseInfo();
      this.wsServer = this.common.getWsServer();
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
  .box {
    width: 400px;
  }
  .top {
    text-align: center;
  }

  .left {
    float: left;
    width: 60px;
  }

  .right {
    float: right;
    width: 60px;
  }

  .bottom {
    clear: both;
    text-align: center;
  }

  .item {
    margin: 4px;
  }

  .left .el-tooltip__popper,
  .right .el-tooltip__popper {
    padding: 8px 10px;
  }
</style>
