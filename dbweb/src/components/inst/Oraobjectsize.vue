<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">占用空间前30的对象</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="segmentTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="owner" label="用户" ></el-table-column>
          <el-table-column prop="segment_name" label="对象名" ></el-table-column>
          <el-table-column prop="segment_type" label="对象类型"></el-table-column>
          <el-table-column prop="size" label="对象大小（GB）" width="140px">
            <template slot-scope="scope">
              <el-tag :type="scope.row.size >= 10 ?  'danger' : 'success'" size="small">
                {{ scope.row.size }}
              </el-tag>
            </template>
          </el-table-column>
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
        segmentTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getObjectSize(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.segmentTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'object',
                item: 'segmentSql,segmentNameList,segmentData',
              }
            }).then((res) => {
                this.segmentTableData = res.result.segmentdata;
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
        this.getObjectSize()
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
