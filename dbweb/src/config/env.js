// 后端API接口地址
// const envs = {
//   apiServer: 'http://192.168.8.152:8000',
//   request_timeout: 120000,
// }
var envs = {}

if (process.env.NODE_ENV == 'development'){
  envs = {
    apiServer: 'http://192.168.8.152:8000',
    request_timeout: 120000,
  }
}else if (process.env.NODE_ENV == 'production'){
  envs = {
    apiServer: 'http://192.168.8.156:8000',
    request_timeout: 120000,
  }
}

module.exports = envs
