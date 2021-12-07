<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">最近15次rman备份</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="rmanTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="40"></el-table-column>
          <el-table-column prop="start_time" label="备份开始时间" ></el-table-column>
          <el-table-column prop="end_time" label="备份结束时间" ></el-table-column>
          <el-table-column prop="input" label="备份输入大小（GB）"></el-table-column>
          <el-table-column prop="output" label="备份输出大小（GB）"></el-table-column>
          <el-table-column prop="status" label="备份状态"></el-table-column>
          <el-table-column prop="runtime" label="备份运行时长"></el-table-column>
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
        rmanTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getRmanInfo(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.rmanTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'rman',
                item: 'rmanSql,rmanNameList,rmanData',
              }
            }).then((res) => {
              this.rmanTableData = res.result.rmandata;
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
        this.getRmanInfo()
      },
    },
    mounted() {
      // this.getUsers()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
