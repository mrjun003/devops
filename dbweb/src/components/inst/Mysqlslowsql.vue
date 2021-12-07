<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">慢日志解析</span></el-divider>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-form ref="slowlogAnalyForm" :rules="rules" :inline="true" :model="filters" >
          <el-form-item label="开始结束时间：">
            <el-date-picker
              v-model="filters.beginEndTime"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="用户：">
            <el-select v-model="filters.user" placeholder="请选择">
              <el-option v-for="item in userList" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-button type="primary" :disabled="bntSlowlog" @click="slowlogAnaly" v-loading="analyseLoading">开始解析</el-button>
        </el-form>
      </el-col>
    </el-row>
    <el-row>
      <el-input id="show_slow" type="textarea" :rows="20" v-model="showSlow" readonly=""></el-input>
    </el-row>
  </div>
</template>

<script>
    export default {
      props: ['instId'],
      data() {
        return{
          showSlow:'',
          bntSlowlog:false,
          analyseLoading:false,
          filters:{
            beginEndTime: [
              Date.now(),
              Date.now()
            ],
            user:'',
            isOnlySel:'0',
            instId: this.instId,
          },
          userList:[],
          analyseLoading:false,
          rules: {

          },
        }
      },
      methods: {
        slowlogAnaly(){
          this.$refs.slowlogAnalyForm.validate((valid) =>{
            if (valid) {
              if(this.filters.beginEndTime){
                this.filters.beginEndTime[0] = this.common.int2Date(this.filters.beginEndTime[0],'yyyy-MM-dd hh:mm:ss')
                this.filters.beginEndTime[1] = this.common.int2Date(this.filters.beginEndTime[1],'yyyy-MM-dd hh:mm:ss')
              }
              this.analyseLoading = true;
              this.$http.post('/api/inst/slowloganaly/',this.filters).then(res => {
                this.showSlow = res.data.data
                if (this.showSlow=='None') {
                  this.$layer_message('没有解析到相应的SQL！');
                }
              }, response => {
                // this.addLoading = false;
                this.$layer_message(response.result);
              }).finally(() => {
                this.analyseLoading = false;
              }).catch((e) => {})
            }
          })
        },
        //获取binglog列表
        getUsers(){
          this.$http.get('/api/inst/getmysqlinfo/', {params:{id:this.instId,item:'getusers'}}).then(res => {
            this.userList = res.result;
          }, response => {
            alert(response.result)
          })
        },
      },
    }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
</style>
