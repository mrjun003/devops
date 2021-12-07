<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">最近48小时归档统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="hourlyArchiveTableData" stripe border v-loading="listLoading"
                  style="width: 100%" max-height="500">
          <el-table-column type="index" width="40"></el-table-column>
          <el-table-column prop="hour" label="时间"></el-table-column>
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
        hourlyArchiveTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getArchHour(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.hourlyArchiveTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'archive',
                item: 'hourlyArchiveSql,hourlyArchiveNameList,hourlyArchiveData',
              }
            }).then((res) => {
                this.hourlyArchiveTableData = res.result.hourlyarchivedata
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
        this.getArchHour()
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
