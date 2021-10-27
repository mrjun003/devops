<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">会话连接数统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="connTableData" show-summary stripe border
                  v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="username" label="username" ></el-table-column>
          <el-table-column prop="machine" label="machine"></el-table-column>
          <el-table-column prop="status" label="status"></el-table-column>
          <el-table-column prop="cnt" label="连接数" width="80px"></el-table-column>
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
        connTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getConnSession(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.connTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'session',
              }
            }).then((res) => {
              this.connTableData = res.result.conndata;
                this.listLoading = false;
              }, (response) => {
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
      reflashClick () {
        this.flag = true;
        this.getConnSession()
      },
    },
    mounted() {
      this.getConnSession()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
