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
          <el-table-column prop="s_id" label="阻塞会话ID"></el-table-column>
          <el-table-column prop="s_state" label="会话状态"></el-table-column>
          <el-table-column prop="s_start" label="会话开始时间#"></el-table-column>
          <el-table-column prop="s_start_waite" label="会话开始等待时间" ></el-table-column>
          <el-table-column prop="s_part_sql" label="执行sql" >
            <template slot-scope="scope">
              <el-popover
                placement="right"
                width="400"
                trigger="hover">
                <div>
                  <el-row>
                    {{ scope.row.s_sql }}
                  </el-row>
                  <el-row style="text-align: center">
                    <el-button type="info" v-clipboard:copy="scope.row.s_sql"
                               v-clipboard:success="onCopy"
                               v-clipboard:error="onError">复制
                    </el-button>
                  </el-row>
                </div>
                <el-button slot="reference" type="text" style="margin:auto 0px auto 10px;">{{ scope.row.s_part_sql }}</el-button>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column prop="b_id" label="被阻塞会话ID"></el-table-column>
          <el-table-column prop="b_state" label="会话状态"></el-table-column>
          <el-table-column prop="b_start" label="会话开始时间"></el-table-column>
          <el-table-column prop="b_start_waite" label="会话开始等待时间"></el-table-column>
          <el-table-column prop="b_part_sql" label="执行sql">
            <template slot-scope="scope">
              <el-popover
                placement="right"
                width="400"
                trigger="hover">
                <div>
                  <el-row>
                    {{ scope.row.b_sql }}
                  </el-row>
                  <el-row style="text-align: center">
                    <el-button type="info" v-clipboard:copy="scope.row.b_sql"
                               v-clipboard:success="onCopy"
                               v-clipboard:error="onError">复制
                    </el-button>
                  </el-row>
                </div>
                <el-button slot="reference" type="text" style="margin:auto 0px auto 10px;">{{ scope.row.b_part_sql }}</el-button>
              </el-popover>
            </template>
          </el-table-column>
          ,,,,,s_sql,,,,,,b_sql
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
            this.$http.get('/api/inst/getmlinfo/', {
              params: {
                id: instId,
                item: 'block_lock',
              }
            }).then((res) => {
                this.blockTableData = res.result.block_lock;
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
            execSql = execSql + 'kill ' + mulSel[i].s_id + ';' + "<br/>"
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
