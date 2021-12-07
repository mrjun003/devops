<template>
  <div>
    <el-row>
      <el-col>
        <el-button style="float: right;" :disabled="btnOpt" type="primary" @click="dbAdd()">创建数据库
        </el-button>
      </el-col>
    </el-row>
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
        <el-table :data="databaseTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="schema_name" label="数据库名" ></el-table-column>
          <el-table-column prop="default_character_set_name" label="字符编码" ></el-table-column>
          <el-table-column prop="default_collation_name" label="排序" ></el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button type="danger" size="small" :disabled="btnOpt" @click="delDatabase(scope.row.schema_name)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>

    <!--新增用户界面-->
    <el-dialog title="创建数据库" visible v-if="dialogDbShow" @close="dialogDbShow = false"
               :close-on-click-modal="false" width="60%" append-to-body>
      <el-form ref="addDbForm" :model="addDbForm" :rules="rules"  label-width="135px">
        <el-row>
          <el-col :span="24">
            <el-form-item prop="dbName" label="数据库名：" required>
              <el-input placeholder="请输入" v-model="addDbForm.dbName" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-form-item prop="charset" label="字符编码：">
            <el-select v-model="addDbForm.charset" placeholder="请选择" >
              <el-option v-for="item in charsetList" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
        </el-row>
        <el-row>
          <el-col :span="18">
            <el-form-item prop="grant" label="权限：">
              <el-radio-group v-model="addDbForm.grant">
                <el-radio label="只读权限"></el-radio>
                <el-radio label="应用权限"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item prop="users" label="授权用户：">
              <el-transfer v-model="addDbForm.grantUsers" :data="userList"></el-transfer>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer">
        <el-button type="text" @click.native="dialogDbShow = false">取消</el-button>
        <el-button type="primary" :loading="addDbLoading" @click.native="showSql()">生成SQL</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  export default {
    props: ['instId','dbRole'],
    data() {
      let validateDatabaseName = (rule, value, callback) => {
        if (value.indexOf("-") != -1) {
          callback(new Error("数据库名不能包含中划线！！！"));
        } else {
          callback();
        }
      };
      return{
        btnOpt: false,
        databaseTableData: [],
        flag: true,
        listLoading: false,
        addDbForm:{
          dbName: '',
          charset: '',
          grantUsers: [],
          grant: '只读权限',
        },
        userList:[],
        charsetList: [
          {label:'utf8',value:'utf8'},
          {label:'gbk',value:'gbk'},
          {label:'latin1',value:'latin1'},
          {label:'utf8mb4',value:'utf8mb4'},
        ],
        addDbLoading:false,
        dialogDbShow:false,
        rules: {
          dbName: [
            {required: true, message: '请输入数据库名', trigger: 'blur'},
            {validator: validateDatabaseName, trigger: 'blur'},
          ],
        },
      }
    },
    methods: {
      //获取用户信息
      getDatabases(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.databaseTableData = [],
            this.$http.get('/api/inst/getmlinfo/', {
              params: {
                id: instId,
                item: 'databases',
              }
            }).then((res) => {
                this.databaseTableData = res.result.databases
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
        this.getDatabases()
      },
      //删除数据库
      delDatabase(databaseName){
        var execSql = 'drop database '+ databaseName + ';';
        this.$emit('showExecSql', execSql)
      },
      //添加数据库用户
      dbAdd(){
        this.dialogDbShow=true;
        this.getUsers();
      },
      //生成创建用户SQL
      showSql(){
        this.$refs.addDbForm.validate((valid) =>{
          if(valid){
            var execSql = 'create database `' + this.addDbForm.dbName + '`'
            if(this.addDbForm.charset != ''){
              execSql = execSql + '  DEFAULT CHARACTER SET ' + this.addDbForm.charset + ';'
            }else{
              execSql = execSql + ';'
            }
            console.log(this.addDbForm.grantUsers)
            if(this.addDbForm.grantUsers.length>0){
              if(this.addDbForm.grant=='只读权限'){
                var grantSql = 'grant select on ' + this.addDbForm.dbName + '.* to '
              }else{
                var grantSql = 'grant all privileges on ' + this.addDbForm.dbName + '.* to '
              }
              for(var i=0;i<this.addDbForm.grantUsers.length;i++){
                console.log('i am here')
                execSql = execSql + '<br/>' + grantSql + this.addDbForm.grantUsers[i] + ';'
                console.log(execSql)
              }
            }
            this.$emit('showExecSql', execSql);
          }
        });
      },
      //获取实例数据库列表
      getUsers(){
        this.$http.get('/api/inst/getmysqlinfo/',
          {
            params:
              {
                id:this.instId,
                item:'getuserhost',
              }
          }).then(res => {
          var users = res.result
          for(var i=0;i<users.length;i++){
            this.userList.push({'label':users[i].value,'key':users[i].value,'disabled':false})
          }
        }, response => {
          alert(response.result)
        })
      },
    },
    mounted() {
      //判断此实例是否有创建数据库权限
      if(this.dbRole != 'Master'){
        this.btnOpt = true;
      }
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
