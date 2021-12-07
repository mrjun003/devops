<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">前30大表</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="tablesizeTableData" show-summary stripe border
                  v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="table_schema" label="数据库名" ></el-table-column>
          <el-table-column prop="table_name" label="表名"></el-table-column>
          <el-table-column prop="sum_row" label="记录数"></el-table-column>
          <el-table-column prop="size_data" label="数据大小(MB)"></el-table-column>
          <el-table-column prop="size_index" label="索引大小(MB)" width="80px"></el-table-column>
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
        tablesizeTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getTableSize(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.connTableData = [],
            this.$http.get('/api/inst/getmlinfo/', {
              params: {
                id: instId,
                item: 'size_table',
              }
            }).then((res) => {
                this.tablesizeTableData = res.result.size_table;
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
        this.getTableSize()
      },
    },
    mounted() {
      // this.getConnSession()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
