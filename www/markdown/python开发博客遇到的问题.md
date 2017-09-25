___name=Blog开发细节反思
___summary=Python开发博客系统遇到的问题

##ORM 测试
user = User()

##问题
Q1 :编写完测试模板以后，如果app中没有add_static会遇到什么问题？
会遇到首页显示不正常的问题。

Q2: 即使添加完add_static也还是显示不出来，猜想这种文件的处理还是有问题。
直接访问遇到127.0.0.1:9000/static/css/1.html 返回 <FileResponse OK not prepared>