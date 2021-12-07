<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">会话连接使用情况</span></el-divider>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="resourceSessionTableData" stripe border
                  v-loading="listLoading" style="width: 100%">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="name" label="name" ></el-table-column>
          <el-table-column prop="current" label="当前连接数"></el-table-column>
          <el-table-column prop="max" label="最大使用连接数"></el-table-column>
          <el-table-column prop="init" label="可分配连接数"></el-table-column>
          <el-table-column prop="limit" label="最大连接数"></el-table-column>
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
        resourceSessionTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getResourceSession(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.resourceSessionTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'session',
                item: 'resourceSessionSql,resourceSession,resourceSessionData',
              }
            }).then((res) => {
              this.resourceSessionTableData = res.result.resourcesessiondata
              this.listLoading = false;
              }, (response) => {
                this.listLoading = false;
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
    },
    mounted() {
      // this.getResourceSession()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
