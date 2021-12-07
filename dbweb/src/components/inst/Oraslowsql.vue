<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">执行时长慢sql</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="currentDaySlowTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="40"></el-table-column>
          <el-table-column prop="username" label="用户" ></el-table-column>
          <el-table-column prop="sql_id" label="sql_id" ></el-table-column>
          <el-table-column prop="execs" label="执行次数"></el-table-column>
          <el-table-column prop="exec_time" label="执行时长"></el-table-column>
          <el-table-column prop="last_time" label="最后执行时间"></el-table-column>
          <el-table-column prop="module" label="module"></el-table-column>
          <el-table-column prop="cost" label="cost"></el-table-column>
          <el-table-column prop="sorts" label="sorts"></el-table-column>
          <el-table-column prop="prb" label="物理读（Bytes）"></el-table-column>
          <el-table-column prop="pwr" label="物理写"></el-table-column>
          <el-table-column prop="dr" label="直接路径读"></el-table-column>
          <el-table-column prop="dw" label="直接路径写"></el-table-column>
          <el-table-column prop="rrows" label="返回行数"></el-table-column>
          <el-table-column prop="sql" label="sql">
            <template slot-scope="scope">
              <el-popover
                placement="right"
                width="400"
                trigger="hover">
                <div>
                  <el-row>
                    {{ scope.row.full_sql }}
                  </el-row>
                  <el-row style="text-align: center">
                    <el-button type="info" v-clipboard:copy="scope.row.full_sql"
                               v-clipboard:success="onCopy"
                               v-clipboard:error="onError">复制
                    </el-button>
                  </el-row>
                </div>
                <el-button slot="reference" type="text" style="margin:auto 0px auto 10px;">{{ scope.row.sql }}</el-button>
              </el-popover>
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
        currentDaySlowTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      //获取慢sql
      getSlowSql(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.currentDaySlowTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'slow',
                item: 'currentDaySlowSql,currentDaySlowNameList,currentDaySlowData',
              }
            }).then((res) => {
                this.currentDaySlowTableData = res.result.currentdayslowdata;
                this.listLoading = false;
              }, (response) => {
                this.listLoading = false;
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
        }
      },
      //刷新
      reflashClick () {
        this.flag = true;
        this.getSlowSql()
      },
      //复制成功
      onCopy(){
        this.$message.success('复制成功')
      },
      //复制失败
      onError(){
        this.$message.console.error('复制失败');
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
