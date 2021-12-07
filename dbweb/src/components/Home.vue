<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <span class="el-span">总实例<br></span>
          <a class="el-a" href="">{{ total_inst }}</a>&nbsp;个
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <span class="el-span">Oracle实例<br></span>
          <a class="el-a" href="">{{ ora_inst }}</a>&nbsp;个
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <span class="el-span">Mysql实例<br></span>
          <a class="el-a" href="">{{ mysql_inst }}</a>&nbsp;个
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <span class="el-span">其他实例<br></span>
          <a class="el-a" href="">{{ other_inst }}</a>&nbsp;个
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" v-if="insts.length>0">
      <el-col :span="24">
        <div class="grid-content bg-purple" style="padding-bottom: 20px">
          <div class="center_text">
            <el-divider><span style="font-weight: bold;font-size:16px;">无法连接实例</span></el-divider>
            <el-table :data="insts" stripe border v-loading="listLoading" style="width: 100%">
              <el-table-column type="index" width="40"></el-table-column>
              <el-table-column prop="inst_ip" label="ip" sortable width="140"></el-table-column>
              <el-table-column prop="inst_name" label="实例名" sortable width="120"></el-table-column>
              <el-table-column prop="inst_type" label="实例类型" sortable width="120"></el-table-column>
              <el-table-column prop="db_status" label="状态" sortable width="90">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.db_status == 'Running' ? 'success' : 'danger'" size="small">
                    {{ scope.row.db_status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="db_role" label="角色" sortable width="90"></el-table-column>
              <el-table-column prop="cluster_id" label="是否群组" width="90">
                <template slot-scope="scope">
                  {{ scope.row.cluster_id == 0 ? '否':'是' }}
                </template>
              </el-table-column>
              <el-table-column prop="apps" label="应用"></el-table-column>
              <el-table-column prop="reason" label="原因"></el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  export default {
    data () {
      return {
        total_inst:0,
        ora_inst:0,
        mysql_inst:0,
        other_inst:0,
        insts: [],
        listLoading: false,
      }
    },
    methods:{
      getIndexInfo(){
        this.$http.get('/api/inst/getindexinfo/', ).then((res) => {
          var data = res.data.data;
          console.log(data)
          this.total_inst = data.total;
          this.ora_inst = data.oracleCount;
          this.mysql_inst = data.mysqlCount;
          this.other_inst = data.otherCount;
          this.insts = data.insts;
          }, (response) =>
          console.log(response.result),
        )
      }
    },
    mounted() {
      this.getIndexInfo()
    }
  }
</script>
<style>
  .el-row {
    margin-bottom: 20px;
  }
  .el-col {
    border-radius: 4px;
  }
  .bg-purple-dark {
    background: #99a9bf;
  }
  .bg-purple {
    background: #ffffff;
  }
  .bg-purple-light {
    background: #ffffff;
  }
  .grid-content {
    padding-top:20px;
    border-radius: 4px;
    min-height: 100px;
    line-height: 35px;
  }
  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }
  .el-a {
    margin-left: 35px;
    font-size:20px;
    color: #1890ff;
    text-decoration:none;
  }
  .el-span {
    margin-left: 35px;
    font-size:14px;
    color: #9a9fa1;
  }
  .center_text{
    display: block;
    width: 98%;
    margin: 0 auto;
  }
</style>
