<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">活跃会话统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col :span="5">
        <el-button @click="autoReflashClick(false)">{{ clickText }}</el-button>
        <el-button style="float: right;margin-bottom: 10px;" type="danger" @click="killSession()">kill选中会话
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
          <el-table-column prop="username" label="username" ></el-table-column>
          <el-table-column prop="status" label="status"></el-table-column>
          <el-table-column prop="machine" label="machine"></el-table-column>
          <el-table-column prop="sql_id" label="sql_id"></el-table-column>
          <el-table-column prop="sql_child_number" label="sql_child_number"></el-table-column>
          <el-table-column prop="row_wait_obj#" label="row_wait_obj#"></el-table-column>
          <el-table-column prop="event" label="event"></el-table-column>
          <el-table-column prop="last_call_et" label="last_call_et"></el-table-column>
          <el-table-column prop="sql_text" label="sql_text">
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
        <el-button type="danger" @click.native="">直接执行</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  export default {
    props: ['instId'],
    data() {
      return{
        sessionTableData: [],
        flag: true,
        listLoading: false,
        clickText:'5秒自动刷新',
        dialogExecSqlShow: false,
        execSql: '',
      }
    },
    methods: {
      getActiveSessions(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.sessionTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'session',
              }
            }).then((res) => {
                this.sessionTableData = res.result.activedata;
                this.listLoading = false;
              }, (response) => {
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
      reflashClick () {
        this.flag = true;
        this.getActiveSessions()
      },
      killSession(){
        var mulSel = this.$refs.sessionMultipleTable.selection
        if(mulSel.length>0){
          this.execSql = '';
          for(var i=0;i<mulSel.length;i++){
            this.execSql = this.execSql + 'alter system kill session \'' + mulSel[i].sid + ','
              + mulSel[i].serial + '\' immediate;' + "<br/>"
          }
          this.dialogExecSqlShow = true
        }else{
          this.$message({type: 'warning',message: '您没有选中任何内容！'});
        }
      },
      onCopy(){
        this.$message.success('复制成功')
      },
      onError(){
        this.$message.console.error('复制失败');
      },
      createTimer(){
        this.timer = setInterval(() => {
          this.flag = true;
          this.getActiveSessions();
        }, 5000);
      },
      stopReflash() {
        clearInterval(this.timer);
      },
      autoReflashClick (is_father) {
        console.log('i am comming')
        console.log(is_father)
        if (!is_father){
          console.log('1111111111111111')
          if (this.clickText == '停止自动刷新') {
            this.clickText = '5秒自动刷新'
            this.stopReflash()
          }else{
            this.clickText = '停止自动刷新'
            this.createTimer()
          }
        }else{
          console.log('2222222222222222222')
          if (this.clickText == '停止自动刷新') {
            this.clickText = '5秒自动刷新'
            this.stopReflash()
          }
        }
      }
    },
    mounted() {
      this.getActiveSessions()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
