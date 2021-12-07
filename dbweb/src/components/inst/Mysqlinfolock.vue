<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">当前锁信息</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-col :span="5">
          <el-button @click="autoReflashClick(false)">{{ clickText }}</el-button>
<!--          <el-button style="float: right;margin-bottom: 10px;" type="danger"-->
<!--                     @click="killSession()" :disabled="bntSessionKill">kill选中会话</el-button>-->
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
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="engine_transaction_id" label="事务ID"></el-table-column>
          <el-table-column prop="thread_id" label="线程号"></el-table-column>
          <el-table-column prop="object_schema" label="用户"></el-table-column>
          <el-table-column prop="object_schema" label="对象" ></el-table-column>
          <el-table-column prop="index_name" label="索引" ></el-table-column>
          <el-table-column prop="lock_type" label="锁类型"></el-table-column>
          <el-table-column prop="lock_mode" label="锁模式"></el-table-column>
          <el-table-column prop="lock_status" label="锁状态"></el-table-column>
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
                item: 'info_lock',
              }
            }).then((res) => {
                this.blockTableData = res.result.info_lock;
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
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
