<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">当前事务</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-col :span="5">
          <el-button @click="autoReflashClick(false)">{{ clickText }}</el-button>
          <el-button style="float: right;margin-bottom: 10px;" type="danger"
                     @click="killSession()" :disabled="bntSessionKill">kill选中会话</el-button>
        </el-col>
        <el-col :span="19">
          <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
        </el-col>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="lockTableData" ref="sessionMultipleTable" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="selection" width="60"></el-table-column>
          <el-table-column prop="trx_mysql_thread_id" label="会话id"></el-table-column>
          <el-table-column prop="trx_id" label="事务ID" ></el-table-column>
          <el-table-column prop="trx_state" label="事务状态" ></el-table-column>
          <el-table-column prop="trx_started" label="事务开始时间"></el-table-column>
          <el-table-column prop="trx_wait_started" label="事务开始等待时间"></el-table-column>
          <el-table-column prop="part_trx_query" label="执行sql">
            <template slot-scope="scope">
              <el-popover
                placement="right"
                width="400"
                trigger="hover">
                <div>
                  <el-row>
                    {{ scope.row.trx_query }}
                  </el-row>
                  <el-row style="text-align: center">
                    <el-button type="info" v-clipboard:copy="scope.row.trx_query"
                               v-clipboard:success="onCopy"
                               v-clipboard:error="onError">复制
                    </el-button>
                  </el-row>
                </div>
                <el-button slot="reference" type="text" style="margin:auto 0px auto 10px;">{{ scope.row.part_trx_query }}</el-button>
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
        lockTableData: [],
        flag: true,
        listLoading: false,
        clickText:'5秒自动刷新',
        timer:'',
      }
    },
    methods: {
      //复制成功
      onCopy(){
        this.$message.success('复制成功')
      },
      //复制失败
      onError(){
        this.$message.console.error('复制失败');
      },
      getLocks(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.lockTableData = [],
            this.$http.get('/api/inst/getmlinfo/', {
              params: {
                id: instId,
                item: 'trx_lock',
              }
            }).then((res) => {
                this.lockTableData = res.result.trx_lock;
                this.listLoading = false;
              }, (response) => {
                this.listLoading = false;
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
      reflashClick () {
        this.flag = true;
        this.getLocks()
      },
      //获取kill session的sql
      killSession(){
        var mulSel = this.$refs.sessionMultipleTable.selection
        if(mulSel.length>0){
          var execSql = '';
          for(var i=0;i<mulSel.length;i++){
            execSql = execSql + 'kill ' + mulSel[i].trx_mysql_thread_id + ';' + "<br/>"
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
        console.log()
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
    },
    mounted(){
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
