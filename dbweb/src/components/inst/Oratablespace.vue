<template>
  <div>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px" type="primary"
                   @click="showDialog()" :disabled="btnOpt">新建表空间
        </el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">表空间使用情况</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="float: right;margin-bottom: 10px;" type="success" plain @click="reflashClick">刷新</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-table :data="tablespaceTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="tablespace_name" label="表空间名" ></el-table-column>
          <el-table-column prop="total_gb" label="总大小（GB）" ></el-table-column>
          <el-table-column prop="used_gb" label="使用大小（GB）"></el-table-column>
          <el-table-column prop="free_gb" label="剩余大小（GB）">
            <template slot-scope="scope">
              <el-tag :type="scope.row.used_pct > 90 && scope.row.free_gb < 10 ?  'danger' : 'success'" size="small">
                {{ scope.row.free_gb }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="used_pct" label="使用率（%）">
            <template slot-scope="scope">
              <el-tag :type="scope.row.used_pct > 90 && scope.row.free_gb < 10 ?  'danger' : 'success'" size="small">
                {{ scope.row.used_pct }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template slot-scope="scope">
              <el-popover placement="right" width="800" trigger="click" >
                <el-row>
                  <el-divider style="margin-bottom: 10px;"><span class="span">表空间{{scope.row.tablespace_name}}占用前10的对象</span></el-divider>
                </el-row>
                <el-row>
                  <el-col :span="24">
                    <el-table :data="tspObjData" stripe border v-loading="listLoadingTspObj" style="width: 100%" max-height="500">
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
                <el-row>
                  <el-divider style="margin-bottom: 10px;"><span class="span">表空间{{scope.row.tablespace_name}}数据文件</span></el-divider>
                </el-row>
                <el-row>
                  <el-col :span="24">
                    <el-table :data="tspFileData" stripe border v-loading="listLoadingTspFile" style="width: 100%" max-height="500">
                      <el-table-column type="index" width="60"></el-table-column>
                      <el-table-column prop="tablespace_name" label="表空间" ></el-table-column>
                      <el-table-column prop="file_id" label="文件号" ></el-table-column>
                      <el-table-column prop="file_name" label="文件名" ></el-table-column>
                      <el-table-column prop="online_status" label="文件状态"></el-table-column>
                      <el-table-column prop="autoextensible" label="是否自动扩展"></el-table-column>
                      <el-table-column prop="size" label="文件大小（GB）" width="140px"></el-table-column>
                      <el-table-column label="操作">
                        <template slot-scope="scope">
                          <el-button type="warning" size="small" :disabled="btnOpt"
                                     @click="resizeDatafile(scope.row.file_id,scope.row.size)">扩展
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </el-col>
                </el-row>
                <el-button slot="reference" type="primary" size="small" @click="getTspObj(instId,scope.row.tablespace_name),getTspFile(instId,scope.row.tablespace_name)">使用详情</el-button>
              </el-popover>
              <el-button type="warning" size="small" :disabled="btnOpt" @click="addDatafile(scope.row.tablespace_name)" >加数据文件</el-button>
              <el-button type="danger" size="small" :disabled="btnOpt" @click="delTablespace(scope.row.tablespace_name)" >删除</el-button>
<!--              :disabled="db_role=='PRIMARY' ? false:true"-->
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>

    <!--新建表空间界面-->
    <el-dialog title="新建表空间" visible v-if="dialogTablespaceShow" @close="dialogTablespaceShow = false"
               :close-on-click-modal="false" width="70%" append-to-body>
      <el-form ref="addTablespaceForm" :model="addTablespaceForm" :rules="rules" label-width="135px">
        <el-row>
          <el-col :span="12">
            <el-form-item prop="tablespace_type" label="表空间类型：" required>
              <el-select v-model="addTablespaceForm.tablespace_type" placeholder="请选择">
                <el-option label="Normal" value="Normal"></el-option>
                <el-option label="Temp" value="Temp"></el-option>
                <el-option label="Undo" value="Undo"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="18">
            <el-form-item prop="tablespace_name" label="表空间名：" required>
              <el-input v-model="addTablespaceForm.tablespace_name" auto-complete="off">
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="18">
            <el-form-item prop="file_name" label="文件名：" :required="datafiledir == '+DATA' ? false:true">
              <el-input v-model="addTablespaceForm.file_name" auto-complete="off"
                        :disabled="datafiledir == '+DATA' ? true:false">
                <template slot="prepend">{{ datafiledir }} </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item prop="size" label="文件初始大小：" required>
              <el-input placeholder="最大32" v-model.number="addTablespaceForm.size">
                <template slot="append">GB</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item prop="autoextend" label="是否自动扩展：">
              <el-radio-group v-model="addTablespaceForm.autoextend">
                <el-radio label="off"></el-radio>
                <el-radio label="on"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" style="text-align: center">
        <el-button type="text" @click.native="dialogTablespaceShow = false">取消</el-button>
        <el-button type="primary" @click.native="tablespaceAdd()">生成SQL</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  // import Oratspobj from "./Oratspobj";
  export default {
    // components:{Oratspobj},
    props: ['instId', 'dbRole'],
    data() {
      return{
        tablespaceTableData: [],
        tspObjData: [],
        tspFileData: [],
        flag: true,
        listLoading: false,
        listLoadingTspObj: true,
        listLoadingTspFile: true,
        btnOpt: false,
        // btnFileExtend: false,
        addTablespaceForm: {
          tablespace_type: 'Normal',
          tablespace_name: '',
          file_name: '',
          autoextend: 'off',
        },
        rules: {
          tablespace_name: [
            {required: true, message: '请输入表空间名', trigger: 'blur'}
          ],
          size: [
            {required: true, message: '请输入数据文件大小', trigger: 'blur'},
            {type:"number" ,min: 1, max: 31, message: '大小要在1到32之间', trigger: 'blur'}
          ],
          file_name: [
            {required: true, message: '请输入文件名', trigger: 'blur'}
          ],
        },
        dialogTablespaceShow: false,
        datafiledir: '',
        filename:'',
      }
    },
    methods: {
      //获取数据库表空间使用情况
      getTablespaceUsed(instId=this.instId){
        if (this.flag){
          this.flag = false;
          this.listLoading = true;
          this.tablespaceTableData = [];
          this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'tablespace',
                item: 'usedSql,usedNameList,usedData',
              }
            }).then((res) => {
              this.listLoading = false;
              this.tablespaceTableData = res.result.useddata;
              }, (response) => {
              this.listLoading = false;
              this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
              }
            );
        }
      },
      //获取占用指定表空间前十对象
      getTspObj(instId,tspName){
        this.listLoadingTspObj = true;
        this.tspObjData = [];
          this.$http.get('/api/inst/getinfo/', {
          params: {
            id: instId,
            tab: 'tablespace',
            filter: "tablespace_name='" + tspName + "'",
            item: 'tspObjSizeSql,tspObjSizeNameList,tspObjSizeData',
          }
        }).then((res) => {
            this.tspObjData = res.result.tspobjsizedata;
            this.listLoadingTspObj = false;
          }, (response) => {
            this.listLoadingTspObj = false;
            this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
          }
        )
      },
      //获取表空间数据文件情况
      getTspFile(instId,tspName){
        this.listLoadingTspFile = true;
        this.tspFileData = [];
        this.$http.get('/api/inst/getinfo/', {
          params: {
            id: instId,
            tab: 'tablespace',
            filter: "tablespace_name='" + tspName + "'",
            item: 'tspFileSql,tspFileNameList,tspFileData',
          }
        }).then((res) => {
            this.tspFileData = res.result.tspfiledata;
            this.listLoadingTspFile = false;
          }, (response) => {
            this.listLoadingTspFile = false;
            this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
          }
        )
      },
      //刷新
      reflashClick () {
        this.flag = true;
        this.getTablespaceUsed()
      },
      //添加表空间
      tablespaceAdd(){
        this.$refs.addTablespaceForm.validate((valid) =>{
          if (valid) {
            if (this.datafiledir == '+DATA') {
              this.file_name = '+DATA'
            } else {
              this.file_name = this.datafiledir + '/' + this.addTablespaceForm.file_name + '.dbf'
            }
            ;
            if (this.addTablespaceForm.tablespace_type == 'Normal') {
              var execSql = 'create tablespace ' + this.addTablespaceForm.tablespace_name + ' datafile \'' +
                this.file_name + '\' size ' + this.addTablespaceForm.size +
                'G autoextend ' + this.addTablespaceForm.autoextend + ';'
            } else if (this.addTablespaceForm.tablespace_type == 'Undo') {
              var execSql = 'create undo tablespace ' + this.addTablespaceForm.tablespace_name + ' datafile \'' +
                this.file_name + '\' size ' + this.addTablespaceForm.size +
                'G autoextend ' + this.addTablespaceForm.autoextend + ';'
            } else if (this.addTablespaceForm.tablespace_type == 'Temp') {
              var execSql = 'create temporary  tablespace ' + this.addTablespaceForm.tablespace_name + ' tempfile \'' +
                this.file_name + '\' size ' + this.addTablespaceForm.size +
                'G autoextend ' + this.addTablespaceForm.autoextend + ';'
            }
            this.$emit('showExecSql', execSql)
          };
        },
        );
      },
      //展示添加表空间
      showDialog(){
        this.dialogTablespaceShow = true;
        this.$http.get('/api/inst/getcommoninfo/', {
          params: {
            id: this.instId,
            item: 'datafiledir',
          }
        }).then((res) => {
          this.datafiledir = res.result.datafiledirdata[0].datafiledir;
          // this.datafiledir = '+DATA'
          // this.datafiledir = '/u01/app/data/oradata/smtbdbdg'
          }, (response) => {
            this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
          }
        );
      },
      //删除表空间
      delTablespace(tspName){
        var execSql = 'drop tablespace '+ tspName + ' including contents and datafiles cascade constraints;';
        this.$emit('showExecSql', execSql)
      },
      //表空间添加数据文件
      addDatafile(tspName){
        var tsptype = ''
        this.$http.get('/api/inst/getcommoninfo/', {
          params: {
            id: this.instId,
            item: 'tsptype',
            filter: "tablespace_name='" + tspName + "'",
          }
        }).then((res) => {
          var tsptype = res.result.tsptypedata[0].tsptype;
          var tspdir = res.result.tsptypedata[0].datafiledir;
          console.log(tspdir)
          if (tspdir == '+DATA'){
            var file_name = '+DATA'
          }else{
            var myDate = new Date();
            var file_name = tspdir + '/' + tspName + '_' + myDate.getMinutes()+ myDate.getSeconds() +'.dbf'
          }
          if (tsptype == 'TEMPORARY'){
            var execSql = 'alter tablespace '+ tspName + ' add tempfile \''+ file_name + '\' size 30G autoextend off;';
          }else {
            var execSql = 'alter tablespace '+ tspName + ' add datafile \''+ file_name + '\' size 30G autoextend off;';
          }
          this.$emit('showExecSql', execSql)
          }, (response) => {
            this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
          }
        );
      },
      //数据文件扩展
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
      this.getDbRole();
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
