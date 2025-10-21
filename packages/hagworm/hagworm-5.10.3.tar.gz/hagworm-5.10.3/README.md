# Hagworm

![](https://img.shields.io/pypi/v/hagworm.svg)
![](https://img.shields.io/pypi/format/hagworm.svg)
![](https://img.shields.io/pypi/implementation/hagworm.svg)
![](https://img.shields.io/pypi/pyversions/hagworm.svg)



## 快速开始



### 1. 下载

```bash
git clone git@gitee.com:wsb310/hagworm.git
```



### 2. 安装

```bash
pip install hagworm
```



### 3. 设计定位

* Hagworm是原生框架、原生库的中间层，对它们进行了更高层次的抽象，用来屏蔽直接的调用，达到不改变使用习惯的情况下可以随意更换框架或库。
* Hagworm整合了它支持的各种框架和库，使它们成为一个整体，屏蔽了底层细节，简化了使用方式。
* Hagworm提供了一个打包的环境，建立了工程质量的底线，开发者只需要关注业务逻辑本身，不需要再关注底层的性能和安全等问题。

```mermaid
graph LR
原生框架-->Hagworm
原生库-->Hagworm
Hagworm-->业务代码
```



### 5. 代码树结构

```text
├── extend
│    ├── base.py                                基础工具
│    ├── cache.py                               缓存相关
│    ├── compile.py                             pyc编译
│    ├── config.py                              配置相关
│    ├── crypto.py                              加解密相关
│    ├── error.py                               错误定义
│    ├── event.py                               事件总线
│    ├── igraph.py                              内存图引擎
│    ├── interface.py                           接口定义
│    ├── logging.py                             日志相关
│    ├── media.py                               媒体相关
│    ├── metaclass.py                           元类相关
│    ├── process.py                             多进程工具
│    ├── qrcode.py                              二维码工具
│    ├── struct.py                              数据结构
│    ├── text.py                                文本相关
│    ├── trace.py                               调试及跟踪
│    ├── transaction.py                         事务抽象
│    ├── validator.py                           通用验证器
│    └── asyncio
│         ├── base.py                           异步工具库
│         ├── buffer.py                         缓冲相关
│         ├── command.py                        命令行相关
│         ├── event.py                          分布式事件总线
│         ├── file.py                           文件读写相关
│         ├── future.py                         协程相关
│         ├── mail.py                           邮件工具
│         ├── mongo.py                          MongoDB工具
│         ├── mysql.py                          MySQL工具
│         ├── net.py                            网络工具
│         ├── ntp.py                            时间同步
│         ├── pool.py                           对象池抽象
│         ├── redis.py                          Redis工具
│         ├── socket.py                         Socket封装
│         ├── task.py                           任务相关
│         └── transaction.py                    事务抽象
│
├── frame
│    └── fastapi
│    │    ├── base.py                           基础工具
│    │    ├── field.py                          表单验证器
│    │    ├── model.py                          表单相关
│    │    └── response.py                       响应数据结构
│    └── gunicorn.py                            gunicorn相关
│    └── stress_tests.py                        压力测试工具
│
└── third
     ├── grpc
     │    ├── client.py                         客户端封装
     │    └── server.py                         服务端封装
     ├── nacos
     │    ├── client.py                         服务发现
     │    └── config.py                         配置中心
     └── rabbitmq
          ├── consume.py                        消费者封装
          ├── publish.py                        生产者封装
          └── rpc.py                            远程调用封装
```



### 6. 重要提示

* 不要在非异步魔术方法中调用异步函数，例如在__del__中调用异步函数，在该函数结束前，对象一直处于析构中的状态，此时弱引用是有效的，但如果此时另外一个线程或者协程通过弱引用去使用它，然后意外就可能发生了
* 使用contextvars库时，要注意使用asyncio的call_soon、call_soon_threadsafe、call_later和call_at函数时（建议使用hagworm.extend.asyncio.base.Utils提供的函数），其中的context参数，必须给出独立的contextvars.Context对象，使其上下文环境独立，否则会出现伪内存泄漏现象



### 7. 关于本项目

* 请遵守开源协议，并保留作者信息
* 本项目任何版本不保证没有BUG，商业使用请自行承担风险
* 如果有任何问题，欢迎与我联系，邮箱wsb310@gmail.com，微信号wsb310



### 8. 特别鸣谢

* 洪仁
