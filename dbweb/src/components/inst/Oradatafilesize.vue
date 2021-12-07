<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">数据文件</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="dataFileTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="file_id" label="文件号" ></el-table-column>
          <el-table-column prop="file_name" label="文件名"></el-table-column>
          <el-table-column prop="tablespace_name" label="所属表空间" ></el-table-column>
          <el-table-column prop="status" label="是否可用" ></el-table-column>
          <el-table-column prop="online_status" label="是否在线"></el-table-column>
          <el-table-column prop="autoextensible" label="是否自动扩展"></el-table-column>
          <el-table-column prop="size" label="当前大小"></el-table-column>
          <el-table-column prop="max_size" label="最大大小"></el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button type="danger" size="small" :disabled="btnOpt" @click="resizeDatafile(scope.row.file_id,scope.row.size,)">
                扩展
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  export default {
    props: ['instId','dbRole'],
    data() {
      return{
        btnOpt: false,
        dataFileTableData: [],
        flag: true,
        listLoading: false,
      }
    },
    methods: {
      getDataFile(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.dataFileTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'tablespace',
                item: 'dataFileSql,dataFileNameList,dataFileData',
              }
            }).then((res) => {
                this.dataFileTableData = res.result.datafiledata
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
        this.getDataFile()
      },
      resizeDatafile(fileId,curSize){
        if(curSize >=30){
          this.$message({type: 'error',message: '此数据文件已经30G,不支持扩展！'})
        }else{
          var execSql = 'alter database datafile '+ fileId + ' resize 30G;'
          this.$emit('showExecSql', execSql)
        }
      },
      // 获取当前实例角色
      getDbRole(){
        console.log('db_role:'+this.dbRole)
        if(this.dbRole != 'PRIMARY'){
          this.btnOpt = true;
        }
      },
    },
    mounted() {
      this.getDbRole()
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
