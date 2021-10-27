let menu = {
  menus: [
    {
      key: '/home', desc: 'Dashboard', icon: 'el-icon-s-platform', permission: 'view_home_board',
    },
    {
      key: '/inst/instance', desc: '实例列表', icon: 'el-icon-coin', permission: 'view_inst_list',
    },
    {
      key: '1', desc: '数据库运维', icon: 'el-icon-s-tools', permission: 'devops_view', subs: [
        {key: '/devops/databases', permission: 'devops_db_view', desc: '数据同步'},
        {key: '/devops/viewsql', permission: 'devops_sql_view', desc: 'SQL上线申请'},
        {key: '/devops/binlog2sql', permission: 'devops_binlog_view', desc: '解析Binlog'},
        {key: '/devops/slowsql', permission: 'devops_slow_view', desc: 'Mysql主节点切换'},
        {key: '/devops/analyseawr', permission: 'devops_awr_view', desc: 'AWR报告分析'},
        {key: '/devops/checkdb', permission: 'devops_checkdb_view', desc: '数据库巡检'},
        {key: '/devops/switchora', permission: 'checkdb_switchora_view', desc: 'ADG主备切换'},
        {key: '/devops/install', permission: 'switchora_install_view', desc: '数据库安装'},
      ]
    },
    {
      key: '2', desc: '定时任务', icon: 'el-icon-date', permission: 'cron_view', subs: [
        {key: '/cron/checkdb', permission: 'cron_checkdb_view', desc: '巡检'},
        {key: '/cron/backup', permission: 'cron_backup_view', desc: '备份'},
        {key: '/cron/getawr', permission: 'cron_getawr_view', desc: '获取awr'},
        {key: '/cron/getslowsql', permission: 'cron_getslowsql_view', desc: '获取慢查'},
      ]
    },
  ]
}

export default menu
