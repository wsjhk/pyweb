# pyweb
基于Python的小型web服务器和小型web框架结合实现

功能：

  1.实现小型的web服务器，可以接受http请求并响应，可解析http头,函数返回可以是对象也可以是其他类型数据。
  
  2.小型web服务器实现master+worker模式,master负责监听socket,worker负责处理socket数据,实现了两种多线程的方式，一种是每个线程都accept()操作,该操作会导致阻塞,并发不高;另一种是使用select模式主进程执行accept(),然后使用队列分配连接的socket到每个worker去接收数据和处理返回,这样简单处理了惊群效应(linux2.6内核之后已经修复该问题),并且worker是轮询的负载均衡,性能提升不少。
  
  3.实现小型web框架,简单封装request和response,封装成app处理web服务器http请求。
  
  4.小型web框架实现router系统,快速开发api应用,同时支持FBV和CBV两种模式。
  
  5.实现简单的测试中间件和token中间件，该web框架支持使用@token_auth实现api的token验证。
  
  
扩展方向：

  1.web服务器使用epoll模型,实现IO多路复用。
  
  2.实现访问模板等静态文件。
  
  3.实现gzip文件压缩和缓存。
  
  4.web框架用协程实现异步。
  
  5.路由系统同时支持CBV和FBV，urls路由表没有去重，使用时注意urls不要重复即可，改进的话添加url时进行判断再添加。
  


运行：

  直接运行myapp.py文件即可实现访问：http://127.0.0.1:8001/hello/wsjhk/ ,token访问需要用时postman工具或者curl等工具。
  

