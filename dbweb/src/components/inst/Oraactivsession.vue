<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">活跃会话统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col :span="5">
        <el-button @click="autoReflashClick(false)">{{ clickText }}</el-button>
        <el-button style="float: right;margin-bottom: 10px;" type="danger" :disabled="bntSessionKill"
                   @click="killSession()" >kill选中会话
        </el-button>
      </el-col>
      <el-col :span="19">
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table ref="sessionMultipleTable" :data="sessionTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="selection" width="60"></el-table-column>
          <el-table-column prop="sid" label="sid" ></el-table-column>
          <el-table-column prop="serial" label="serial#" ></el-table-column>
          <el-table-column prop="username" label="用户名" ></el-table-column>
          <el-table-column prop="status" label="状态"></el-table-column>
          <el-table-column prop="machine" label="连接主机"></el-table-column>
          <el-table-column prop="sql_id" label="sql_id"></el-table-column>
<!--          <el-table-column prop="sql_child_number" label="sql_child_number"></el-table-column>-->
<!--          <el-table-column prop="row_wait_obj#" label="row_wait_obj#"></el-table-column>-->
          <el-table-column prop="event" label="等待事件"></el-table-column>
          <el-table-column prop="last_call_et" label="执行时间"></el-table-column>
          <el-table-column prop="sql_text" label="执行sql">
            <template slot-scope="scope">
              <el-popover
                placement="right"
                width="400"
                trigger="hover">
                <div>
                  <el-row>
                    {{ scope.row.full_sql }}
                  </el-row>
                  <el-row style="text-align: center">
                    <el-button type="info" v-clipboard:copy="scope.row.full_sql"
                               v-clipboard:success="onCopy"
                               v-clipboard:error="onError">复制
                    </el-button>
                  </el-row>
                </div>
                <el-button slot="reference" type="text" style="margin:auto 0px auto 10px;">{{ scope.row.sql_text }}</el-button>
              </el-popover>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  export default {
    props: ['instId'],
    data() {
      return{
        bntSessionKill: false,
        sessionTableData: [],
        flag: true,
        listLoading: false,
        clickText:'5秒自动刷新',
        timer:'',
      }
    },
    methods: {
      //获取活跃会话
      getActiveSessions(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.sessionTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'session',
                item: 'activeSessionSql,activeNameList,activeData',
              }
            }).then((res) => {
                this.sessionTableData = res.result.activedata;
                this.listLoading = false;
              }, (response) => {
                this.listLoading = false;
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
      //刷新
      reflashClick () {
        this.flag = true;
        this.getActiveSessions()
      },
      //获取kill session的sql
      killSession(){
        var mulSel = this.$refs.sessionMultipleTable.selection
        if(mulSel.length>0){
          var execSql = '';
          for(var i=0;i<mulSel.length;i++){
            execSql = execSql + 'alter system kill session \'' + mulSel[i].sid + ','
              + mulSel[i].serial + '\' immediate;' + "<br/>"
          }
          this.$emit('showExecSql',execSql)
        }else{
          this.$message({type: 'warning',message: '您没有选中任何内容！'});
        }
      },
      //设置定时刷新
      createTimer(){
        this.timer = setInterval(() => {
          this.reflashClick()
        }, 5000);
      },
      //停止定时刷新
      stopReflash() {
        clearInterval(this.timer);
      },
      //改变定时刷新按钮状态及定时任务
      autoReflashClick (is_father) {
        if (!is_father){
          if (this.clickText == '停止自动刷新') {
            this.clickText = '5秒自动刷新'
            this.stopReflash()
          }else{
            this.clickText = '停止自动刷新'
            this.createTimer()
          }
        }else{
          if (this.clickText == '停止自动刷新') {
            this.clickText = '5秒自动刷新'
            this.stopReflash()
          }
        }
      },
      //复制成功
      onCopy(){
        this.$message.success('复制成功')
      },
      //复制失败
      onError(){
        this.$message.console.error('复制失败');
      },
    },
    mounted() {
      this.bntSessionKill = this.common.has_permission('operate_session_kill')
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
