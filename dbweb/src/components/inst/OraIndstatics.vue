<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">统计信息失效索引</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="indexstaticsTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="owner" label="用户" ></el-table-column>
          <el-table-column prop="index_name" label="索引名" ></el-table-column>
          <el-table-column prop="table_owner" label="表用户"></el-table-column>
          <el-table-column prop="table_name" label="表名"></el-table-column>
          <el-table-column prop="last_analyzed" label="最后收集时间"></el-table-column>
          <el-table-column prop="stale_stats" label="是否过期"></el-table-column>
          <el-table-column label="操作" width="110">
            <template slot-scope="scope">
              <el-button type="primary" size="small" @click="">重新收集</el-button>
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
        indexstaticsTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getIndStatics(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.indexstaticsTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'statics',
                item: 'indexStaticsSql,indexStaticsNameList,indexStaticsData',
              }
            }).then((res) => {
                this.indexstaticsTableData = res.result.indexStaticsdata;
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
        this.getIndStatics()
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
