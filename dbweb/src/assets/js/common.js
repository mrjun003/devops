//判断权限是否存在
export default {
  has_permission:function (permission) {
    let permissions = localStorage.getItem('permissions')
    if (!permissions.includes(permission)){
      return false
    }else{
      return true
    }
  }
}
