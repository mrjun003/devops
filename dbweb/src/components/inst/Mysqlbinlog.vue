<template>
  <div>
    <el-row>
      <el-divider style="margin-bottom: 10px;"><span class="span">Binlog解析</span></el-divider>
    </el-row>
    <el-row>
      <el-col>
        <el-form ref="binLogAnalyForm" :rules="rules" :inline="true" :model="filters" >
          <el-form-item prop="startBinlog" label="开始binlog：" required>
            <el-select v-model="filters.startBinlog" placeholder="请选择" @change="getEndBinlogList">
<!--              <el-option v-for="item in binlogList" :key="item.value" :label="item.label" :value="item.value">-->
<!--              </el-option>-->
              <el-option
                v-for="item in startBinlogList"
                :key="item.value"
                :label="item.label"
                :value="item.value">
                <span style="float: left">{{ item.label }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ item.time }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="结束binlog：">
            <el-select v-model="filters.endBinlog" placeholder="请选择" :disabled="endBinlogSel" @change="changeEndTime">
<!--              <el-option v-for="item in endBinlogList" :key="item.value" :label="item.label" :value="item.value">-->
<!--              </el-option>-->
              <el-option
                v-for="item in endBinlogList"
                :key="item.value"
                :label="item.label"
                :value="item.value">
                <span style="float: left">{{ item.label }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ item.time }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="开始结束时间：">
            <el-date-picker
              v-model="filters.beginEndTime"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="数据库：">
            <el-select v-model="filters.dbs" multiple placeholder="请选择" @change="getTables">
              <el-option v-for="item in dbList" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="表：">
            <el-select v-model="filters.tables" multiple placeholder="请选择" :disabled="tabSel">
              <el-option v-for="item in tableList" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="sql类型：">
            <el-select v-model="filters.sqlType" multiple placeholder="请选择">
              <el-option lable="INSERT" value="INSERT"></el-option>
              <el-option lable="DELETE" value="DELETE"></el-option>
              <el-option lable="UPDATE" value="UPDATE"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="只解析DML：">
            <el-radio v-model="filters.isOnlyDml" label="0">否</el-radio>
            <el-radio v-model="filters.isOnlyDml" label="1">是</el-radio>
          </el-form-item>
          <el-form-item label="生成sql类型：">
            <el-radio v-model="filters.isFlashBack" label="0">原始sql</el-radio>
            <el-radio v-model="filters.isFlashBack" label="1">回滚sql</el-radio>
          </el-form-item>
          <el-button type="primary" :disabled="bntBinlog" @click="binlogAnaly" v-loading="analyseLoading">开始解析</el-button>
        </el-form>
      </el-col>
    </el-row>
    <el-row>
      <el-input id="show_sql" type="textarea" :rows="20" v-model="showSql" readonly=""></el-input>
    </el-row>
    <el-row style="text-align: center;margin-top: 20px">
      <el-button type="primary" v-if="copyBnt" v-clipboard:copy="showSql.replaceAll('<br/>','\n')"
                 v-clipboard:success="onCopy"
                 v-clipboard:error="onError">复制</el-button>
    </el-row>
  </div>
</template>

<script>
  export default {
    props: ['instId'],
    data() {
      return{
        filters:{
          startBinlog: '',
          endBinlog: '',
          beginEndTime: [
            Date.now(),
            Date.now()
          ],
          isFlashBack: '0',
          isOnlyDml: '0',
          dbs: [],
          tables: [],
          sqlType: [],
          instId: this.instId,
        },
        startBinlogList:[],
        endBinlogList:[],
        dbList: [],
        tableList: [],
        bntBinlog: false,
        tabSel: true,
        endBinlogSel:true,
        rules: {
          startBinlog:[
            {required: true, message: '请选择开始binlog文件！', trigger: 'blur'}
          ]
        },
        analyseLoading:false,
        showSql:'',
        copyBnt:false,
      }
    },
    methods:{
      //开始解析binlog
      binlogAnaly(){
        this.$refs.binLogAnalyForm.validate((valid) =>{
          if (valid) {
            if(this.filters.beginEndTime){
              this.filters.beginEndTime[0] = this.frontOneHour(this.filters.beginEndTime[0].getTime(),'yyyy-MM-dd hh:mm:ss')
              this.filters.beginEndTime[1] = this.frontOneHour(this.filters.beginEndTime[1].getTime(),'yyyy-MM-dd hh:mm:ss')
            };
            this.analyseLoading = true;
            this.$http.post('/api/inst/binloganaly/',this.filters).then(res => {
              this.showSql = res.data.data
              if (this.showSql==''){
                this.$layer_message('没有解析到相应的SQL！');
                this.copyBnt=false;
              }else{
                const textarea = document.getElementById('show_sql');
                textarea.scrollTop = textarea.scrollHeight;
                this.copyBnt=true;
              }
            }, response => {
              // this.addLoading = false;
              this.$layer_message(response.result);
            }).finally(() => {
              this.filters.beginEndTime[0] = new Date(this.filters.beginEndTime[0])
              this.filters.beginEndTime[1] = new Date(this.filters.beginEndTime[1])
              this.analyseLoading = false;
            }).catch((e) => {})
          }
        })
      },
      //获取binglog列表
      getBinLogs(){
        this.$http.get('/api/inst/getmysqlinfo/', {params:{id:this.instId,item:'getbinlogs'}}).then(res => {
          this.startBinlogList = res.result;
        }, response => {
          alert(response.result)
        })
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
          this.dbList = res.result;
        }, response => {
          alert(response.result)
        })
      },
      //获取数据库表列表
      getTables(dbs){
        if (dbs.length==1){
          this.tabSel = false;
          this.$http.get('/api/inst/getmysqlinfo/',
            {params:{id:this.instId,item:'gettables',filters:'table_schema = \''+ dbs[0] + '\''}}
          ).then(res => {
            this.tableList = res.result;
          }, response => {
            alert(response.result)
          })
        }else{
          this.tabSel = true;
          this.tableList = [];
          this.filters.tables = []
        }
      },
      //根据binlog开始文件获取可选结束文件
      getEndBinlogList(){
        if (this.filters.startBinlog !=''){
          this.endBinlogSel = false;
          this.filters.endBinlog = this.filters.startBinlog
        };
        var i = this.startBinlogList.length;
        while (i--) {
          if (this.startBinlogList[i].value == this.filters.startBinlog) {
            if(i!=0){
              this.filters.beginEndTime = [new Date(this.startBinlogList[i-1].time),new Date(this.startBinlogList[i].time)]
            }else{
              this.filters.beginEndTime = [new Date(this.frontOneHour(new Date(this.startBinlogList[i].time).getTime()- 1 * 60 * 60 * 1000,'yyyy-MM-dd hh:mm:ss')),
                new Date(this.startBinlogList[i].time)]
            }
            this.endBinlogList = this.startBinlogList.slice(i,this.startBinlogList.length);
          }
        };

      },
      //根据endBinlog的变化变化时间
      changeEndTime(){
        var i = this.endBinlogList.length;
        while (i--) {
          if (this.endBinlogList[i].value == this.filters.endBinlog) {
            this.filters.beginEndTime = [this.filters.beginEndTime[0],new Date(this.endBinlogList[i].time)]
          }
        };
      },
      //获取前一个小时时间
      frontOneHour (oldTime,fmt) {
        // var currentTime = new Date(oldTime.getTime()- 1 * 60 * 60 * 1000)
        var currentTime = new Date(oldTime)
        // console.log(currentTime) // Wed Jun 20 2018 16:12:12 GMT+0800 (中国标准时间)
        var o = {
          'M+': currentTime.getMonth() + 1, // 月份
          'd+': currentTime.getDate(), // 日
          'h+': currentTime.getHours(), // 小时
          'm+': currentTime.getMinutes(), // 分
          's+': currentTime.getSeconds(), // 秒
          'q+': Math.floor((currentTime.getMonth() + 3) / 3), // 季度
          'S': currentTime.getMilliseconds() // 毫秒
        }
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (currentTime.getFullYear() + '').substr(4 - RegExp.$1.length))
        for (var k in o) {
          if (new RegExp('(' + k + ')').test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (('00' + o[k]).substr(('' + o[k]).length)))
        }
        return fmt
      },
      //复制成功
      onCopy(){
        this.$message.success('复制成功')
      },
      //复制失败
      onError(){
        this.$message.console.error('复制失败');
      },
    },
    mounted() {
      // this.getBinLogs();
      // this.getDbs();
    }
  }
</script>

<style scoped>
  .span {
    font-weight: bold;
    font-size:16px
  }
  .center_text{
    display: block;
    margin: 0 auto;
  }
</style>
