import axios from 'axios'
import envs from '../config/env'

let tools = {
  install: null
}

// Promise 添加finally方法
// eslint-disable-next-line no-extend-native
Promise.prototype.finally = function (callback) {
  return this.then(
    () => Promise.resolve(callback()),
    () => Promise.reject(callback())
  )
}

// Date 添加format方法
// eslint-disable-next-line no-extend-native
Date.prototype.format = function () {
  return `${this.getFullYear()}-${this.getMonth() + 1}-${this.getDate()} ${this.getHours()}:${this.getMinutes()}:${this.getSeconds()}`
}

// 数组包含判断
function isSubArray (parent, child) {
  for (let item of child) {
    if (!parent.includes(item.trim())) {
      return false
    }
  }
  return true
}

// js对象和数组深拷贝
function deepCopy (obj) {
  if (Array.isArray(obj)) {
    let result = []
    for (let item of obj) {
      result.push(deepCopy(item))
    }
    return result
  } else if (typeof obj === 'object' && obj !== null) {
    let result = {}
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        result[key] = deepCopy(obj[key])
      }
    }
    return result
  } else {
    return obj
  }
}

// response处理
function handleResponse(response, router) {
  if (response.status === 401) {
    localStorage.removeItem('token');
    router.push({name: 'login',params:{error:response.data.message}});
    response['result'] = '请登录';
    return Promise.reject(response)
  } else if (response.data.hasOwnProperty('data') && response.data.hasOwnProperty('message')) {
    console.log(response.data)
    if (response.data.message) {
      response['result'] = response.data.message
    } else {
      response['result'] = response.data.data;
      return Promise.resolve(response)
    }
  } else {
    console.log(response)
    response['result'] = '无效的数据格式'
  }
  return Promise.reject(response)
}

tools.install = function (Vue, router) {
  // 请求拦截器
  axios.interceptors.request.use(request => {
    if (request.url.startsWith('/api/')) {
      request.headers['X-TOKEN'] = localStorage.getItem('token');
      request.headers['Content-Type'] = "application/json;charset=utf-8"
      request.url = envs.apiServer + request.url.replace('/api', '');
      // request.url = envs.apiServer + request.url
      console.log(request.url)
    }
    request.timeout = envs.request_timeout;
    return request;
  });
  // 返回拦截器
  axios.interceptors.response.use(response => {
    return handleResponse(response, router)
  }, error => {
    if (error.response) {
      return handleResponse(error.response, router)
    }
    return Promise.reject({result: '请求异常： ' + error.message})
  });
  Vue.prototype.$http = axios;
  Vue.prototype.$layer_message = function (message, type) {
    this.$message({
      showClose: true,
      duration: 5000,
      message: message,
      type: type || 'error'
    })
  };
  // js对象和数组深拷贝
  Vue.prototype.$deepCopy = deepCopy;
  // 权限判断
  Vue.prototype.has_permission = function (str_code) {
    if (localStorage.getItem('is_supper') === 'true') {
      return true
    }
    let permissions = localStorage.getItem('permissions');
    if (!str_code || !permissions) return false;
    permissions = permissions.split(',');
    for (let or_item of str_code.split('|')) {
      if (isSubArray(permissions, or_item.split('&'))) {
        return true
      }
    }
    return false
  };
  // 路由导航钩子
  router.beforeEach((to, from, next) => {
    next()
    // if (['/', '/login', '/deny','/home','/welcome','/layout','/inst/instance','/devops/databases'].includes(to.path)) {
    //   next()
    // } else if (to.meta.hasOwnProperty('permission') && Vue.prototype.has_permission(to.meta.permission)) {
    //   next()
    // } else {
    //   next({path: '/deny'})
    // }
  })
};


export default tools;
