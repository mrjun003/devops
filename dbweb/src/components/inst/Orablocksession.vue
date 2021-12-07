<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">会话阻塞</span></el-divider>
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
        <el-table :data="blockTableData" ref="sessionMultipleTable" stripe border v-loading="listLoading"
                  style="width: 100%" max-height="500">
          <el-table-column type="selection" width="60"></el-table-column>
          <el-table-column prop="blocker_instance_id" label="造成阻塞会话实例"></el-table-column>
          <el-table-column prop="blocker_sid" label="造成阻塞会话"></el-table-column>
          <el-table-column prop="blocker_sess_serial" label="blocker_sess_serial#"></el-table-column>
          <el-table-column prop="sid" label="被阻塞会话" ></el-table-column>
          <el-table-column prop="sess_serial" label="sess_serial#" ></el-table-column>
          <el-table-column prop="wait_id" label="wait_id"></el-table-column>
          <el-table-column prop="wait_event" label="wait_event"></el-table-column>
          <el-table-column prop="wait_event_text" label="wait_event_text"></el-table-column>
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
        blockTableData: [],
        flag: true,
        listLoading: false,
        clickText:'5秒自动刷新',
        timer:'',
      }
    },
    methods: {
      getBlocks(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.blockTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'lock',
                item: 'blockSql,blockNameList,blockData',
              }
            }).then((res) => {
              this.blockTableData = res.result.blockdata;
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
        this.getBlocks()
      },
      //获取kill session的sql
      killSession(){
        var mulSel = this.$refs.sessionMultipleTable.selection
        if(mulSel.length>0){
          var execSql = '';
          for(var i=0;i<mulSel.length;i++){
            execSql = execSql + 'alter system kill session \'' + mulSel[i].blocker_sid + ','
              + mulSel[i].blocker_sess_serial + '\' immediate;' + "<br/>"
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
