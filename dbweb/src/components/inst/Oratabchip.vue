<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">表碎片率高于70%</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="tabChipTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="owner" label="用户" ></el-table-column>
          <el-table-column prop="table_name" label="表名" ></el-table-column>
          <el-table-column prop="theory_size" label="理论大小（MB）"></el-table-column>
          <el-table-column prop="true_size" label="实际大小（MB）"></el-table-column>
          <el-table-column prop="used_pct" label="使用率（%）"></el-table-column>
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
        tabChipTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getTabChip(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.tabChipTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'object',
                item: 'tabChipSql,tabChipNameList,tabChipData',
              }
            }).then((res) => {
                this.tabChipTableData = res.result.tabchipdata;
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
        this.getTabChip()
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
