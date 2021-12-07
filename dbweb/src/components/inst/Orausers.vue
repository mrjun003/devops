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
            <el-table-column prop="username" label="用户名" ></el-table-column>
            <el-table-column prop="account_status" label="用户状态" >
              <template slot-scope="scope">
                <el-tag :type="scope.row.account_status == 'OPEN' ? 'success' : 'danger'" size="small">
                  {{ scope.row.account_status }}{{ scope.row.account_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lock_date" label="上锁时间" ></el-table-column>
            <el-table-column prop="expiry_date" label="过期时间" ></el-table-column>
            <el-table-column prop="default_tablespace" label="默认表空间"></el-table-column>
            <el-table-column prop="created" label="创建时间"></el-table-column>
            <el-table-column label="操作" width="150">
              <template slot-scope="scope">
                <el-popover placement="right" width="800" trigger="click" >
                  <el-row>
                    <el-divider style="margin-bottom: 10px;"><span class="span">用户详情</span></el-divider>
                  </el-row>

                  <el-button slot="reference" type="primary" size="small" @click="">详情</el-button>
                </el-popover>
                <el-button type="danger" size="small" :disabled="btnOpt" @click="delUser(scope.row.username)">删除</el-button>
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
            <el-col :span="8">
              <el-form-item prop="user" label="用户：" required>
                <el-input placeholder="请输入" v-model="addUserForm.user" auto-complete="off"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item prop="password" label="密码：" required>
                <el-input v-model="addUserForm.password" show-password></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item prop="password2" label="再次输入密码：" required>
                <el-input v-model="addUserForm.password2" show-password></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="12">
              <el-form-item prop="defaulttsp" label="默认表空间：" required>
                <el-select v-model="addUserForm.defaulttsp" placeholder="请选择" style="width:140px">
                  <el-option v-for="item in tsp_options" :key="item.value" :label="item.label" :value="item.value">
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="defaulttmptsp" label="默认临时表空间：" required>
                <el-select v-model="addUserForm.defaulttmptsp" placeholder="请选择" style="width:140px">
                  <el-option v-for="item in tmp_tsp_options" :key="item.value" :label="item.label" :value="item.value">
                  </el-option>
                </el-select>
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
              <el-form-item prop="roles" label="角色：">
                <el-transfer v-model="addUserForm.roles" :data="role_options"></el-transfer>
              </el-form-item>
            </el-col>
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
        return{
          btnOpt: false,
          userTableData: [],
          flag: true,
          listLoading: false,
          addUserForm:{
            user: '',
            password: '',
            grant: '只读权限',
            // users: [],
            roles: [],
          },
          tsp_options: [],
          tmp_tsp_options: [],
          // user_options: [],
          role_options: [],
          addUserLoading:false,
          dialogUserShow:false,

          rules: {
            user: [
              {required: true, message: '请输入用户名', trigger: 'blur'},
            ],
            password: [
              {required: true, message: '请输入密码', trigger: 'blur'},
            ],
            password2: [
              {required: true, message: '请再次输入密码', trigger: 'blur'},
              {validator: validatePass2, trigger: 'blur'},
            ],
            defaulttsp: [
              {required: true, message: '请选择默认表空间', trigger: 'blur'}
            ],
            defaulttmptsp: [
              {required: true, message: '请选择默认临时表空间', trigger: 'blur'}
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
            this.$http.get('/api/inst/getinfo/', {
              params: {
                id: instId,
                tab: 'user',
                item: 'userSql,userNameList,userData',
              }
            }).then((res) => {
              this.userTableData = res.result.userdata
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
        delUser(userName){
          var execSql = 'drop user '+ userName + ' cascade;';
          this.$emit('showExecSql', execSql)
        },
        //添加数据库用户
        userAdd(){
          this.dialogUserShow=true;
          this.$http.get('/api/inst/getcreatetspinfo/', {
            params: {
              instId: this.instId,
            }
          }).then((res) => {
            var data = res.data.data;
            console.log('i am here')
            console.log(data)
            this.role_options = data.roleList;
            // this.user_options = data.userList;
            this.tmp_tsp_options = data.tempTspList;
            this.tsp_options = data.normalTspList;
            }, (response) => {
              this.$message({type: 'error',message: '获取信息失败，原因：' + response.result})
            }
          );
        },
        //生成创建用户SQL
        showSql(){
          this.$refs.addUserForm.validate((valid) =>{
            if(valid){
              var execSql = 'create user ' + this.addUserForm.user + ' identified by "' + this.addUserForm.password
                + '" default tablespace ' + this.addUserForm.defaulttsp + ' temporary tablespace '
                + this.addUserForm.defaulttmptsp + ';<br/> grant connect,unlimited tablespace to '
                + this.addUserForm.user + ';<br/>'
              if (this.addUserForm.roles.length>0){
                var role = ''
                for(var i = 0; i < this.addUserForm.roles.length; i++) {
                  role = role + this.addUserForm.roles[i] + ',';
                }
                execSql = execSql + 'grant ' + role.substr(0, role.length - 1) + ' to '
                  + this.addUserForm.user + ';<br/>';
              };
              if(this.addUserForm.grant == '超级权限'){
                execSql = execSql + 'grant dba to ' + this.addUserForm.user + ';<br/>';
              }else if(this.addUserForm.grant == '应用权限'){
                execSql = execSql + 'grant resource to ' + this.addUserForm.user + ';<br/>';
              };
              this.$emit('showExecSql', execSql);
            }
          });
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
        // this.getUsers()
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
