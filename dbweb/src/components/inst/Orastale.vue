<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">表统计信息失效原因</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="stalereasondataTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="table_owner" label="表用户"></el-table-column>
          <el-table-column prop="table_name" label="表名"></el-table-column>
          <el-table-column prop="inserts" label="插入数"></el-table-column>
          <el-table-column prop="updates" label="更新数"></el-table-column>
          <el-table-column prop="deletes" label="删除数"></el-table-column>
          <el-table-column prop="timestamp" label="截至时间"></el-table-column>
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
        stalereasondataTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getStale(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.stalereasondataTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'statics',
                item: 'staleReasonSql,staleReasonNameList,staleReasonData',
              }
            }).then((res) => {
              this.stalereasondataTableData = res.result.stalereasondata;
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
        this.getStale()
      },
    },
    mounted() {
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
