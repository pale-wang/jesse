import os, re
from datetime import datetime
from fabric.api import cd, run, put, local, lcd
from fabric.state import env

env.user = 'iknow'
env.password = 'wonki^(*%'
env.hosts = ['wshy.me']

_TAR_FILE = 'dist-jesse.tar.gz'

def build():
	includes = ['static', 'templates', '*.py']
	excludes = ['test', '.*', '*.pyc', '*.pyo']
	local('rm -f dist/{}'.format(_TAR_FILE))
	with lcd( os.path.join(os.path.abspath('.'), 'www') ):
		# on linux use --deference or -h
		# on mac use -h
		# 需要验证
		cmd = ['tar', '-h', '-czvf', '../dist/{}'.format(_TAR_FILE)]
		cmd.extend(["--exclude='{}'".format(ex)  for ex in excludes])
		cmd.extend(includes)
		print(' '.join(cmd))
		local(' '.join(cmd))



_REMOTE_TMP_TAR = '/tmp/{}'.format(_TAR_FILE)
_REMOTE_BASE_DIR = '/home/iknow'

def deploy():
	newdir = 'jesse-{}'.format(datetime.now().strftime('%y-%m-%d_%H.%M.%S'))
	# 移除原有的 /tmp/dist-jesse.tar.gz
	run('rm -f {}'.format(_REMOTE_TMP_TAR))
	# 将本地的dist/dist-jesse.tar.gz 推送到远端的 /tmp/dist-jesse.tar.gz
	put('dist/{}'.format(_TAR_FILE), _REMOTE_TMP_TAR)
	# 切换到远端的/home/iknow
	with cd(_REMOTE_BASE_DIR):
		run('mkdir {}'.format(newdir))
	# 切换到远端的/home/iknow/jesse-%y-%m-%d_%H.%M.%S/
	with cd( '{}/{}'.format(_REMOTE_BASE_DIR, newdir) ):
		# 解压缩/tmp/dist-jesse.tar.gz 到当前路径
		run('tar -xzvf %s' % _REMOTE_TMP_TAR)

	# 切换到远端的/home/iknow
	with cd(_REMOTE_BASE_DIR):
		# 删除当前的www目录
		run('rm -f www')
		# 将新上传的jesse-%y-%m-%d_%H.%M.%S目录软连接到www
		run('ln -s {} www'.format(newdir))
'''		
	with settings(warn_only=True):
		sudo('supervisorctl stop awesome')
		sudo('supervisorctl start awesome')
		sudo('/etc/init.d/nginx reload')
'''
