# pyweb
基于Python的小型web服务器和小型web框架结合实现

功能：

  1.实现小型的web服务器，可以接受http请求并响应，可解析http头,函数返回可以是对象也可以是其他类型数据。
  
  2.小型web服务器实现master+worker模式,master负责监听socket,worker负责处理socket数据。
  
  3.实现小型web框架,简单封装request和response,封装成app处理web服务器http请求。
  
  4.小型web框架实现router系统,快速开发api应用。
  
  5.实现简单的测试中间件和token中间件，该web框架支持使用@token_auth实现api的token验证。
  
  
待改进：

  1.web服务器使用epoll模型,实现IO多路复用（worker进程负载均衡和惊群问题的处理）。
  
  2.实现访问模板等静态文件。
  
  3.实现gzip文件压缩和缓存。
  
  4.web框架用协程实现异步。
  
  5.路由系统实现CBV模式，类方法响应，目前是FBV。
  


运行：

  直接运行myapp.py文件即可实现访问：http://127.0.0.1:8001/hello/wsjhk/,token访问需要用时postman工具或者curl等工具。
  

