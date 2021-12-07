<template>
  <div>
    <el-row :gutter="20" style="text-align: center">
      <el-col :span="8">
        <div class="grid-content bg-purple" v-loading="listLoading">
          <el-divider><span class="title">主机信息</span></el-divider>
          <span class="span">主机名：{{ instInfo.host_name }}<br/></span>
          <span class="span">操作系统：{{ databaseInfo.platform_name }}<br/></span>
          <span class="span" v-for="info in hostInfoData">{{ info.stat_name }}：{{ info.value }}<br/></span>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="grid-content bg-purple" v-loading="listLoading">
          <el-divider><span class="title">实例信息</span></el-divider>
          <span class="span">实例号：{{ instInfo.instance_number }}<br/></span>
          <span class="span">实例名：{{ instInfo.instance_name }}<br/></span>
          <span class="span">服务名：{{ instInfo.service_name }}<br/></span>
          <span class="span">端口：{{ instInfo.inst_port }}<br/></span>
          <span class="span">数据库版本：{{ instInfo.version }}<br/></span>
          <span class="span">启动时间：{{ instInfo.startup_time }}<br/></span>
          <span class="span">数据库状态：{{ instInfo.status }}<br/></span>
          <span class="span">归档模式：{{ instInfo.archiver }}<br/></span>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="grid-content bg-purple" v-loading="listLoading">
          <el-divider><span class="title">数据库信息</span></el-divider>
          <span class="span">dbid：{{ databaseInfo.dbid }}<br/></span>
          <span class="span">数据库名：{{ databaseInfo.name }}<br/></span>
          <span class="span">创建时间：{{ databaseInfo.created }}<br/></span>
          <span class="span">日志模式：{{ databaseInfo.log_mode }}<br/></span>
          <span class="span">数据库角色：{{ databaseInfo.database_role }}<br/></span>
          <span class="span">数据状态：{{ databaseInfo.open_mode }}<br/></span>
          <span class="span">是否有备库：{{ databaseInfo.guard_status }}<br/></span>
          <span class="span">是否开启闪回功能：{{ databaseInfo.flashback_on }}<br/></span>
          <span class="span">是否RAC集群：{{ databaseInfo.is_cluster=='FALSE' ? '否':'是' }}<br/></span>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" v-if="isCluster ? true:false">
      <div class="center_text">
        <el-divider><span class="title">群组信息</span></el-divider>
        <el-table :data="clusterInfo" stripe border v-loading="listLoading" v-if="isCluster" :span-method="objectSpanMethod"
                    style="width: 100%" max-height="500">
            <el-table-column type="index" width="60"></el-table-column>
            <el-table-column prop="cluster_name" label="群组名" ></el-table-column>
            <el-table-column prop="ip" label="ip" ></el-table-column>
            <el-table-column prop="db_role" label="角色" >
              <template slot-scope="scope">
                <el-tag :type="scope.row.db_role == 'PRIMARY' || scope.row.db_role == 'Master' ? 'success' : 'danger'" size="small">
                  {{ scope.row.db_role }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template slot-scope="scope">
                <el-button type="warning" size="small" :disabled="bntSwitch" @click="switchOraADG(scope.row.cluster_id)">主备切换
                </el-button>
              </template>
            </el-table-column>
          </el-table>
      </div>
    </el-row>
  </div>
</template>

<script>
  export default {
    props: ['instId'],
    data(){
      return{
        bntSwitch: false,
        listLoading:false,
        instInfo:{},
        databaseInfo:{},
        hostInfoData:[],
        clusterInfo:[],
        flag:true,
        listLoading: true,
        isCluster: false,

      }
    },
    methods:{
      getDatabaseInfo(instId=this.instId){
        if (this.flag){
          this.flag = false
          this.listLoading = true
          this.$http.get('/api/inst/getinfo/', {
            params: {
              id: instId,
              tab: 'info',
            }
          }).then((res) => {
              this.instInfo = res.result.instanceinfodata[0];
              this.databaseInfo = res.result.databaseinfodata[0];
              this.hostInfoData = res.result.hostinfodata;
              this.clusterInfo = res.result.clusterinfo
              this.listLoading = false;
              if (this.clusterInfo.length > 0){
                this.isCluster = true;
              };
            }, (response) => {
              this.listLoading = false;
              this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
            }
          )
        }
      },

      // arraySpanMethod({ row, column, rowIndex, columnIndex }) {
      //   if (rowIndex % 2 === 0) {
      //     if (columnIndex === 0) {
      //       return [1, 2];
      //     } else if (columnIndex === 1) {
      //       return [0, 0];
      //     }
      //   }
      // },
      //合并单元格
      objectSpanMethod({ row, column, rowIndex, columnIndex }) {
        if (columnIndex == 4) {
          if (rowIndex == 0){
            return {
              rowspan: this.clusterInfo.length,
              colspan: 1
            };
          }else{
            return {
              rowspan: 0,
              colspan: 0
            };
          };
        };
        if (columnIndex == 1) {
          if (rowIndex == 0){
            return {
              rowspan: this.clusterInfo.length,
              colspan: 1
            };
          }else{
            return {
              rowspan: 0,
              colspan: 0
            };
          };
        };
      },

      //跳转到切换页面
      switchOraADG(clusterId){
        var switchUrl = this.$router.resolve({
          path:"/devops/switch/oraadg", query:{clusterId: clusterId}
        })
        window.open(switchUrl.href)
      },
    },
    mounted(){
      // this.getDatabaseInfo(this.instId)
      this.bntSwitch = this.common.has_permission('devops_switch_role')
    },
  }
</script>

<style scoped>
  .center_text{
    display: block;
    width: 80%;
    margin: 0 auto;
  }
  .span{
    margin-bottom: 10px;
    margin-left: 20px;
  }
  .grid-content {
    padding-top:20px;
    border-radius: 4px;
    min-height: 100px;
    line-height: 35px;
  }
  .bg-purple {
    background: #ffffff;
  }
  .title{
    font-weight: bold;
    font-size:16px
  }
</style>
