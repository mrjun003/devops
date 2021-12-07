<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">分区表统计</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="parttableTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="table_owner" label="用户" ></el-table-column>
          <el-table-column prop="table_name" label="表名" ></el-table-column>
          <el-table-column prop="parttion_name" label="表分区名"></el-table-column>
          <el-table-column prop="part_size" label="表分大小(GB)"></el-table-column>
          <el-table-column prop="high_value" label="分区最大值"></el-table-column>
          <el-table-column prop="partition_position" label="分区位"></el-table-column>
          <el-table-column label="操作" width="290">
            <template slot-scope="scope">
              <el-button type="warning" size="small" @click="">清空分区</el-button>
              <el-button type="danger" size="small" @click="">删除分区</el-button>
              <el-button type="primary" size="small" @click="">添加分区</el-button>
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
        parttableTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getParttabSize(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.parttableTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'object',
                item: 'parttableSql,parttableNameList,parttableData',
              }
            }).then((res) => {
                this.parttableTableData = res.result.parttabledata;
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
        this.getParttabSize()
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
