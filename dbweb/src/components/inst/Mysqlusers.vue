<template>
  <div>
    <el-row>
      <el-col>
        <el-button style="float: right;" :disabled="btnOpt" type="primary" @click="userAdd()">创建用户
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
        <el-table :data="userTableData" stripe border v-loading="listLoading" style="width: 100%" max-height="500">
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="user" label="用户名" ></el-table-column>
          <el-table-column prop="host" label="可访问主机" ></el-table-column>
          <el-table-column prop="plugin" label="密码插件" ></el-table-column>
          <el-table-column prop="password_expired" label="密码过期时间" >
            <template slot-scope="scope">
              {{ scope.row.password_expired== 'N' ? '': scope.row.password_expired}}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button type="danger" size="small" :disabled="btnOpt" @click="delUser(scope.row.user,scope.row.host)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>

    <!--新增用户界面-->
    <el-dialog title="创建用户" visible v-if="dialogUserShow" @close="dialogUserShow = false"
               :close-on-click-modal="false" width="60%" append-to-body>
      <el-form ref="addUserForm" :model="addUserForm" :rules="rules"  label-width="135px">
        <el-row>
          <el-col :span="24">
            <el-form-item prop="user" label="用户：" required>
              <el-input placeholder="请输入" v-model="addUserForm.user" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item prop="ips" label="可访问网段：">
              <el-input placeholder="例如：192.168.8.%,192.168.3.%" v-model="addUserForm.ips" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="18">
            <el-form-item prop="grant" label="权限：">
              <el-radio-group v-model="addUserForm.grant">
                <el-radio label="只读权限"></el-radio>
                <el-radio label="应用权限"></el-radio>
                <el-radio label="超级权限"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item prop="dbs" label="授权数据库：">
              <el-transfer v-model="addUserForm.dbs" :data="dbList"></el-transfer>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-form-item prop="password" label="密码：" required>
            <el-input v-model="addUserForm.password" show-password></el-input>
          </el-form-item>
        </el-row>
        <el-row>
          <el-form-item prop="password2" label="再次输入密码：" required>
            <el-input v-model="addUserForm.password2" show-password></el-input>
          </el-form-item>
        </el-row>
      </el-form>
      <div slot="footer">
        <el-button type="text" @click.native="dialogUserShow = false">取消</el-button>
        <el-button type="primary" :loading="addUserLoading" @click.native="showSql()">生成SQL</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  export default {
    props: ['instId','dbRole'],
    data() {
      let validatePass2 = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请再次输入密码'));
        } else if (value !== this.addUserForm.password) {
          callback(new Error('两次输入密码不一致!'));
        } else {
          callback();
        }
      };
      let validatePass1 = (rule, value, callback) => {
        if (value.indexOf("'") != -1) {
          callback(new Error("密码不能包含单引号！！！"));
        } else {
          callback();
        }
      };
      return{
        btnOpt: false,
        userTableData: [],
        flag: true,
        listLoading: false,
        addUserForm:{
          user: '',
          password: '',
          grant: '只读权限',
          ips:'',
          dbs: [],
        },
        dbList: [],
        addUserLoading:false,
        dialogUserShow:false,

        rules: {
          user: [
            {required: true, message: '请输入用户名', trigger: 'blur'},
          ],
          password: [
            {required: true, message: '请输入密码', trigger: 'blur'},
            { min: 8, max: 16, message: '长度在 8 到 16 个字符', trigger: 'blur' },
            {validator: validatePass1, trigger: 'blur'},
          ],
          password2: [
            {required: true, message: '请再次输入密码', trigger: 'blur'},
            {validator: validatePass2, trigger: 'blur'},
          ],
        },
      }
    },
    methods: {
      //获取用户信息
      getUsers(instId=this.instId){
        if (this.flag){
          this.flag = false,
            this.listLoading = true,
            this.userTableData = [],
            this.$http.get('/api/inst/getmlinfo/', {
              params: {
                id: instId,
                item: 'users',
              }
            }).then((res) => {
                this.userTableData = res.result.users
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
        this.getUsers()
      },
      //删除用户
      delUser(userName,userHost){
        var execSql = 'drop user '+ userName + '@\'' + userHost + '\';';
        this.$emit('showExecSql', execSql)
      },
      //添加数据库用户
      userAdd(){
        this.dialogUserShow=true;
        this.getDbs();
      },
      //授权方法
      getGrantSql(grant,dbs,user){
        console.log('i am here')
        var r_sql = ''
        if(grant=='超级权限'){
          r_sql = r_sql + 'grant all privileges on *.* to ' + user + ';'
        }else{
          for(var i=0;i<dbs.length;i++){
            if(r_sql != ''){
              r_sql = r_sql + '<br/>'
            }
            if(grant=='应用权限'){
              r_sql = r_sql + 'grant all privileges on ' + dbs[i] + '.* to ' + user + ';'
            }else if (grant=='只读权限'){
              r_sql = r_sql + 'grant select on ' + dbs[i] + '.* to ' + user + ';'
            }
          }
        }
        return r_sql
      },
      //生成创建用户SQL
      showSql(){
        this.$refs.addUserForm.validate((valid) =>{
          if(valid){
            if(this.addUserForm.ips==''){
              var execSql = 'create user ' + this.addUserForm.user + '@\'%\' identified by \''
                + this.addUserForm.password + '\';'
              var grant_sql = this.getGrantSql(this.addUserForm.grant,this.addUserForm.dbs,
                this.addUserForm.user + '@\'%\'')
              console.log(grant_sql)
              execSql = execSql + '<br/>' + grant_sql;
            }else{
              var execSql = ''
              var ipList = this.addUserForm.ips.split(",")
              for (var i=0;i<ipList.length ;i++ ){
                if(execSql!=''){
                  execSql = execSql + '<br/>'
                }
                execSql = execSql + 'create user ' + this.addUserForm.user +
                  '@\''+ ipList[i] +'\' identified by \'' + this.addUserForm.password + '\';'
                var grant_sql = this.getGrantSql(this.addUserForm.grant,this.addUserForm.dbs,
                  this.addUserForm.user + '@\''+ ipList[i] +'\'')
                execSql =execSql + '<br/>' + grant_sql
              }
            }
            this.$emit('showExecSql', execSql);
          }
        });
      },
      //获取实例数据库列表
      getDbs(){
        this.$http.get('/api/inst/getmysqlinfo/',
          {
            params:
              {
                id:this.instId,
                item:'getdatabases',
              }
          }).then(res => {
          var dbs = res.result
          // this.dbList = dbs
          for(var i=0;i<dbs.length;i++){
            this.dbList.push({'label':dbs[i].value,'key':dbs[i].value,'disabled':false})
          }
        }, response => {
          alert(response.result)
        })
      },
    },
    mounted() {
      //判断当前实例是否是主实例，非主实例没有添加用户权限
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
