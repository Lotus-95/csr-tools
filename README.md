# SSH tools for csr

## 安装
安装：

> $ python setup.py install

初始化，注意 cluster 选项可以留空，留空默认为 2080ti 和 v100 集群，如果需要输入多个集群用 `,` 隔开。

> $ csr init
> 
> username: qinwenkang
> 
> password: 
> 
> cluster[2080ti,v100]:

## 连接到集群
输入 `csr` 后会列出所有集群上的所有 job，输入 id 来快速链接，需要避免 job name 重复的情况，否则可能会导致 private key 有问题。输入任意一个不存在的 id 会退出程序。

> $ csr

## 查看集群资源

> $ csr quota v100
> 
> $ csr quota 2080ti

## 删除 job

> $ csr delete cluster:job_name
> 
> $ csr delete v100:test_job
> 
>  deleted job test_job successfully

## 下载文件

输入 `csr download cluster:filename` 来快速下载文件，例如：`csr download v100:test.zip`。


## 将可用的集群加入 ssh_config

输入 `csr update-config` 将所有可用的集群更新到 ssh_config 当中，方便使用 vscode 等工具连接集群。

## TODO

 - [x] 删除 job
 - [x] 查看集群资源
 - [ ] 快速创建新 job
 - [ ] 远程执行指令
 - [ ] 列出文件列表
 - [ ] 上传文件
 - [ ] 快速启动多个实验
 - [x] 生成 ssh config 用于 vscode 和 pycharm 连接
 - [ ] 修改 private key 的保存方式