<template>
    <div>
      <el-row style="text-align: center;">
        <el-col :span="11" style="margin-left: 20px;">
          <div class="grid-content bg-purple" v-loading="listLoading">
            <el-divider><span class="title">主库信息</span></el-divider>
            <div v-for="db in dbs" v-if="db.db_role=='PRIMARY'">
              <span class="span">主机ip：{{ db.inst_ip }}<br/></span>
              <span class="span">实例名：{{ db.inst_name }}<br/></span>
            </div>
          </div>
        </el-col>
        <el-col :span="11" style="margin-right: 20px;float: right;">
          <div class="grid-content bg-purple" v-loading="listLoading">
            <el-divider><span class="title">备库信息</span></el-divider>
            <div v-for="db in dbs" v-if="db.db_role=='PHYSICAL STANDBY'">
              <span class="span">主机ip：{{ db.inst_ip }}<br/></span>
              <span class="span">实例名：{{ db.inst_name }}<br/></span>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row style="text-align: center;margin-top: 20px">
        <el-button type="warning" :disabled="bntSwitchNormal" @click="switchADG('normal')">主备切换</el-button>
        <el-button type="danger" :disabled="bntSwitchForce" @click="switchADG('force')">强制切换</el-button>
<!--        <el-button type="danger" @click="testws()">测试</el-button>-->
      </el-row>

      <!-- 切换过程 -->
      <el-row v-if="switchd">
        <el-row>
          <el-divider><span class="title">切换过程</span></el-divider>
        </el-row>
        <el-row>
          <el-row style="margin-bottom: 20px;margin-left: 20px">
            <span style="font-size: 16px;font-weight: bold">切换步骤：</span>
          </el-row>
          <el-row style="margin-bottom: 20px;margin-left: 20px;margin-right: 20px">
            <el-steps :active="activeStep">
              <el-step v-for="step in switchSteps" v-if="step.title != ''" :key="step.title" :title="step.title"
                       :description="step.desc"></el-step>
            </el-steps>
          </el-row>
          <el-row style="margin-bottom: 20px;margin-left: 20px">
            <span style="font-size: 16px;font-weight: bold">切换日志：</span>
          </el-row>
          <el-row style="margin-bottom: 20px;margin-left: 20px;margin-right: 20px">
            <el-input id="show_log" type="textarea" :rows="20" v-model="switchLog" readonly=""></el-input>
          </el-row>
        </el-row>
      </el-row>
    </div>
</template>

<script>
    export default {
        data(){
          return{
            clusterId: this.$route.query.clusterId,
            bntSwitchNormal: false,
            bntSwitchForce: false,
            wsServer: '',
            listLoading: true,
            switchd: false,
            switchLog: '',
            switchSteps: [
              {'title':'','desc':''}
            ],
            activeStep: 0,
            dbs:[
            ],
            socket: '',
          }
        },
      methods:{
        switchADG(switchType){
          if(switchType == 'force'){
            var confirMessage =  '强制切换可能会导致主备关系被破坏！！！';
            var cancelMessage = '取消强制切换';
          }else if (switchType == 'normal'){
            var confirMessage =  '由于主备硬件配置差异，切换后可能导致性能差异！！！';
            var cancelMessage = '取消主备切换';
          };
          this.$confirm(confirMessage, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
            center: true,
          }).then(() => {
            this.switchd = true;
            this.switch(switchType)
          }).catch(() => {
            this.$message({type: 'info',message: cancelMessage});
          })
          },
        getDatabases(){
          this.$http.post('/api/inst/getinstances/', {'cluster_id':this.clusterId}).then(res => {
            this.dbs = res.result.data
          }, response => {
            this.error = response.result
          }).finally(() => this.listLoading = false)
        },
        switch(switchType){
          const _this = this;
          if (typeof (WebSocket) == 'undefined') {
            this.$notify({
              title: '提示',
              message: '当前浏览器无法接收实时报警信息，请使用谷歌浏览器！',
              type: 'warning',
              duration: 0
            });
          } else {
            this.bntSwitchNormal = true;
            this.bntSwitchForce = true;
            // 实例化socket
            // const socketUrl = 'ws://192.168.8.152:8000/ws/switchadg/' + localStorage.getItem('login_user') +'/';
            const socketUrl = _this.wsServer + '/ws/switchadg/' + localStorage.getItem('login_user') +'/';
            this.socket = new WebSocket(socketUrl);
            // 监听socket打开
            this.socket.onopen = function() {
              console.log('浏览器WebSocket已打开');
              //发送字符:
              _this.socket.send(JSON.stringify({
                'switchtype': switchType,
                'clusterid': _this.clusterId,
                'username': localStorage.getItem('login_user'),
              }));
            };
            // 监听socket消息接收
            this.socket.onmessage = function(msg) {
              // console.log('i am here');
              var data = msg.data;
              // console.log(data);
              data = eval('('+data+')');
              if(data.hasOwnProperty('steplist')){
                _this.switchSteps = data.steplist;
                _this.activeStep = data.activestep;
              }else{
                if(data.opt == 'log' || data.opt == '执行sql'){
                  _this.switchLog = _this.switchLog +  data.sql;
                  const textarea = document.getElementById('show_log');
                  textarea.scrollTop = textarea.scrollHeight;
                };
                if(data.hasOwnProperty('activestep')){
                  _this.activeStep = data.activestep;
                };
                if(data.hasOwnProperty('tip')){
                  _this.$alert('<span>' + data.tip + '</span>', '可根据以下提示快速恢复新备库', {
                    dangerouslyUseHTMLString: true
                  });
                };
                if(data.opt == '切换完成'){
                  if(switchType=='force'){
                    _this.$alert('<span>强制切换完成！</span>', '', {
                      dangerouslyUseHTMLString: true
                    });
                  }else{
                    _this.$alert('<span>切换完成！</span>', '', {
                      dangerouslyUseHTMLString: true
                    });
                  }
                  _this.socket.close()
                  _this.getDatabases();
                };
              }
            };
            // 监听socket错误
            this.socket.onerror = function() {
              console.log('WebSocket错误');
            };
            // 监听socket关闭
            this.socket.onclose = function() {
              console.log('WebSocket已关闭');
            };
          };
        },
        testws(){
          this.$http.get('/api/inst/testws/', {
            params: {
              username: localStorage.getItem('login_user'),
            }
          }).then((res) => {
              console.log('sucessed')
            }, (response) => {
              this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
            }
          )
        },
        initWebpack () { //  初始化websocket
          const wsuri = 'ws://192.168.8.156:8000/ws/switchadg/' + localStorage.getItem('login_user') +'/';
          this.sock = new WebSocket(wsuri)//  这里面的this都指向vue
          this.sock.onopen = this.websocketopen
          this.sock.onmessage = this.websocketonmessage
          this.sock.onclose = this.websocketclose
          this.sock.onerror = this.websocketerror
        },
        websocketopen () { //  打开
          console.log('WebSocket连接成功')
        },
        websocketonmessage (e) { //  数据接收
          var data = JSON.parse(e.data)
          console.log(data)
        },
        websocketsend () { //  数据发送
          this.sock.send(JSON.stringify({
            'message': this.commnd
          }))
        },
        websocketclose () { //  关闭
          console.log('WebSocket关闭')
        },
        websocketerror () { //  失败
          console.log('WebSocket连接失败')
        },
        },
      mounted() {
        this.bntSwitchNormal = this.common.has_permission('devops_switch_normal');
        this.bntSwitchForce = this.common.has_permission('devops_switch_force');
        this.getDatabases();
        // this.initWebpack();
        this.wsServer = this.common.getWsServer();
      },
    }
</script>

<style scoped>
  .span{
    margin-bottom: 10px;
    margin-left: 20px;
  }
  .grid-content {
    padding-top:20px;
    border-radius: 4px;
    min-height: 100px;
    line-height: 35px;
  }
  .bg-purple {
    background: #ffffff;
  }
  .title{
    font-weight: bold;
    font-size:16px
  }
</style>
