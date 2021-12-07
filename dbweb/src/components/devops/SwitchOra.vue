<template>
  <div>
    <el-row>
      <el-col :span="20">
        <el-form :inline="true" :model="filters">
          <el-form-item label="实例名:">
            <el-input v-model="filters.inst_name" placeholder="实例名" style="width:140px"></el-input>
          </el-form-item>
          <el-form-item label="IP:">
            <el-input v-model="filters.inst_ip" placeholder="ip" style="width:140px"></el-input>
          </el-form-item>
          <el-form-item label="所属应用:">
            <el-input v-model="filters.inst_apps" placeholder="所属应用" style="width:140px"></el-input>
          </el-form-item>
          <el-form-item label="群组:">
            <el-select v-model="filters.cluster_id" placeholder="请选择" style="width:140px">
              <el-option lable="ALL" value="ALL"></el-option>
              <el-option v-for="item in inst_cluster_options" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" @click="getClusterInstances(1)">查询</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <el-table :data="tableData" stripe border v-loading="listLoading" :span-method="objectSpanMethod"
              style="width: 100%">
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
      <el-table-column prop="db_version" label="版本"></el-table-column>
      <el-table-column prop="apps" label="操作" width="105">
        <template slot-scope="scope">
          <el-button type="warning" size="small" :disabled="bntSwitch" @click="switchOraADG(scope.row.cluster_id)">主备切换
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--分页-->
    <div class="pagination-bar" v-if="total > 10">
      <el-pagination :page-size="10"
                     @current-change="handleCurrentChange"
                     :current-page="currentPage"  layout="total, prev, pager, next"
                     :total="total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
  export default {
    data () {
      return {
        bntSwitch: false,
        filters:{
          ip:'',
          inst_name:'',
          app:'',
          cluster_id:'',
          page:1,
        },
        inst_cluster_options:[],
        listLoading:false,
        tableData:[],
        total:0,
        currentPage:1,
      }
    },
    methods:{
      //获取群组
      getCluster(){
        this.$http.get('/api/inst/getoracluster/',this.filters).then(res => {
          this.inst_cluster_options = res.result;
          console.log(this.inst_cluster_options)
        }, response => {
          this.error = response.result
        })
      },
      //获取集群实例列表
      getClusterInstances(page) {
        this.listLoading = true;
        this.filters.page = page;
        this.$http.post('/api/inst/getclusterinstances/',this.filters).then(res => {
          this.tableData = res.result.data;
          this.total = res.result.total;
          let data2 = this.mergeTableRow(this.tableData,['apps']);
          this.tableData = data2;
        }, response => {
          this.error = response.result
        }).finally(() => this.listLoading = false)
      },

      //换页
      handleCurrentChange(val) {
        this.currentPage = val;
        this.getInstances(this.currentPage);
      },

      //合并相同的单元格
      objectSpanMethod({row, column, rowIndex, columnIndex}) {
        const span = column['property'] + '-span';
        if(row[span]){
          return row[span]
        }
      },

      /**
       *
       * @param data  表格数据
       * @param merge 需要合并的列字段名称数组
       * @returns {*}
       */
      mergeTableRow (data, merge) {
        if (!merge || merge.length === 0) {
          return data
        }
        merge.forEach((m) => {
          const mList = {}
          data = data.map((v, index) => {
            const rowVal = v[m]
            if (mList[rowVal] && mList[rowVal].newIndex === index) {
              mList[rowVal]['num']++
              mList[rowVal]['newIndex']++
              data[mList[rowVal]['index']][m + '-span'].rowspan++
              v[m + '-span'] = {
                rowspan: 0,
                colspan: 0
              }
            } else {
              mList[rowVal] = { num: 1, index: index, newIndex: index + 1 }
              v[m + '-span'] = {
                rowspan: 1,
                colspan: 1
              }
            }
            return v
          })
        });
        console.log(data)
        return data
      },

      //跳转到切换页面
      switchOraADG(clusterId){
        var switchUrl = this.$router.resolve({
          path:"/devops/switch/oraadg", query:{clusterId: clusterId}
        })
        window.open(switchUrl.href)
      },

    },
    mounted() {
      this.bntSwitch = this.common.has_permission('devops_switch_role')
      this.getCluster();
      this.getClusterInstances(1);
    }
  }
</script>

<style scoped>

</style>
