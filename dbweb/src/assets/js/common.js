//判断权限是否存在
export default {
  has_permission:function (permission) {
    let permissions = localStorage.getItem('permissions')
    // console.log(permissions)
    if (permissions.includes(permission)){
      return false
    }else{
      return true
    }
  },
  uuid:function (len, radix) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
    var uuid = [], i;
    radix = radix || chars.length;

    if (len) {
      // Compact form
      for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random()*radix];
    } else {
      // rfc4122, version 4 form
      var r;
      // rfc4122 requires these characters
      uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
      uuid[14] = '4';
      // Fill in random data.  At i==19 set the high bits of clock sequence as
      // per rfc4122, sec. 4.1.5
      for (i = 0; i < 36; i++) {
        if (!uuid[i]) {
          r = 0 | Math.random()*16;
          uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
        }
      }
    }
    return uuid.join('');
  },
  getWsServer:function () {
    var env = process.env.NODE_ENV
    var wsServer = ''
    if (env == 'development'){
      wsServer = 'ws://192.168.8.156:8000'
    }else if (env == 'production'){
      wsServer = 'ws://192.168.8.156:8000'
    };
    return wsServer
  },
  //时间戳转日期格式
  int2Date (oldTime,fmt) {
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
}
