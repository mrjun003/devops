<template>
    <div>
      <el-row>
        <el-divider style="margin-bottom: 10px;"><span class="span">用户详情</span></el-divider>
      </el-row>
      <el-row>
        <el-col>
          <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="24">
          <el-table :data="userTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
            <el-table-column type="index" width="60"></el-table-column>
            <el-table-column prop="username" label="用户名" ></el-table-column>
            <el-table-column prop="account_status" label="用户状态" >
              <template slot-scope="scope">
                <el-tag :type="scope.row.account_status == 'OPEN' ? 'success' : 'danger'" size="small">
                  {{ scope.row.account_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lock_date" label="上锁时间" ></el-table-column>
            <el-table-column prop="expiry_date" label="过期时间" ></el-table-column>
            <el-table-column prop="default_tablespace" label="默认表空间"></el-table-column>
            <el-table-column prop="created" label="创建时间"></el-table-column>
            <el-table-column label="操作" width="150">
              <template slot-scope="scope">
                <el-button type="primary" size="small" @click="instDetail(scope.row.id,scope.row.inst_type)">详情</el-button>
                <el-button type="danger" size="small" @click="instDelete(scope.row.id ,scope.row.inst_ip)">删除</el-button>
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
          userTableData: [],
          flag: true,
          listLoading: false,
        }
      },
      methods: {
        getUsers(instId=this.instId){
          if (this.flag){
            this.flag = false,
            this.listLoading = true,
            this.userTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'user',
              }
            }).then((res) => {
              this.userTableData = res.result.userdata
              this.listLoading = false;
              }, (response) => {
                this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            )
          }
        },
        reflashClick () {
          this.flag = true;
          this.getUsers()
        },
      },
      mounted() {
        this.getUsers()
      }
    }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
