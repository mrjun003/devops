<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">各用户占用空间大小</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="usersegmentTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="user" label="用户" ></el-table-column>
          <el-table-column prop="size" label="使用大小（GB）" width="140px"></el-table-column>
          <el-table-column label="操作" width="110">
            <template slot-scope="scope">
              <el-popover placement="right" width="800" trigger="click" >
                <el-row>
                  <el-divider style="margin-bottom: 10px;"><span class="span">用户{{scope.row.user}}下占用空间前10的对象</span></el-divider>
                </el-row>
                <el-row>
                  <el-col :span="24">
                    <el-table :data="userObjData" stripe border v-loading="listLoadingUserObj" style="width: 100%" max-height="500">
                      <el-table-column type="index" width="60"></el-table-column>
                      <el-table-column prop="owner" label="用户" ></el-table-column>
                      <el-table-column prop="tablespace_name" label="表空间" ></el-table-column>
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
                <el-button slot="reference" type="primary" size="small" @click="getUserObj(instId,scope.row.user)">占用详情</el-button>
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
        usersegmentTableData: [],
        userObjData: [],
        flag: true,
        listLoading: false,
        listLoadingUserObj: false,

      }
    },
    methods: {
      getUserObj(instId,userName){
        this.listLoadingUserObj = true;
        this.tspObjData = [];
        this.$http.get('/api/inst/getinfo/', {
          params: {
            id: instId,
            tab: 'tablespace',
            filter: "owner='" + userName + "'",
            item: 'tspObjSizeSql,tspObjSizeNameList,tspObjSizeData',
          }
        }).then((res) => {
            this.userObjData = res.result.tspobjsizedata;
            this.listLoadingUserObj = false;
          }, (response) => {
            this.listLoadingUserObj = false;
            this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
          }
        )
      },
      getUserSize(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.usersegmentTableData = [],
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'object',
                item: 'usersegmentSql,usersegmentNameList,usersegmentData',
              }
            }).then((res) => {
                this.usersegmentTableData = res.result.usersegmentdata;
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
        this.getUserSize()
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
