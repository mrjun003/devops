<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">最近7天归档统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="daylyArchiveTableData" stripe border v-loading="listLoading"
                  style="width: 100%">
          <el-table-column type="index" width="40"></el-table-column>
          <el-table-column prop="day" label="日期"></el-table-column>
          <el-table-column prop="size" label="归档大小（GB）"></el-table-column>
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
        daylyArchiveTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getArchDay(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.daylyArchiveTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'archive',
                item: 'daylyArchiveSql,daylyArchiveNameList,daylyArchiveData',
              }
            }).then((res) => {
                this.daylyArchiveTableData = res.result.daylyarchivedata;
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
        this.getArchDay()
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
