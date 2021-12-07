from django.urls import path, re_path
# from django.conf.urls import url

from .views import *
from .ws import *

urlpatterns = [
    path('getindexinfo/',GetIndexInfo.as_view()),
    path('getcreatetspinfo/',getCreateTspInfo.as_view()),
    path('addinstance/',AddInst.as_view()),
    path('getinstances/',GetInst.as_view()),
    path('deleteinstance/',DelInst.as_view()),
    path('editinstance/',EditInst.as_view()),
    path('getinfo/',GetInfo.as_view()),
    path('getmlinfo/',GetMLInfo.as_view()),
    path('addcluster/',AddCluster.as_view()),
    path('getcluster/',GetCluster.as_view()),
    path('getoracluster/',GetOraCluster.as_view()),
    path('getcommoninfo/',GetCommonInfo.as_view()),
    path('execsql/',ExecSql.as_view()),
    path('getclusterinstances/',GetClusterList.as_view()),
    path('switchadg/',SwitchADG.as_view()),
    path('getmysqlinfo/',GetMysqlInfo.as_view()),
    path('binloganaly/',BinlogAnaly.as_view()),
    path('slowloganaly/',SlowlogAnaly.as_view()),
    path('testws/',TestWS.as_view()),
    # path(r'taskstailperform/', Tailperform.as_view()),
]

websocket_url = [
    re_path(r'ws/execsql/(?P<user_name>[^/]+)/$',execSqlService),
    re_path(r'^ws/switchadg/(?P<user_name>[^/]+)/$', switchADG),
    # re_path(r'^ws/switchadg/(?P<user_name>[^/]+)/$', AsyncSqlService),
    re_path(r'^ws/looklog/(?P<user_name>[^/]+)/$', lookLogConsumer),
]