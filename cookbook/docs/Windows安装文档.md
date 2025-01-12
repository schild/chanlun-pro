### Windows 安装文档

---

> Python 版本支持 3.8、3.9、3.10 （建议 3.10），不然运行会报 RuntimeError 错误  
> 前置条件  
> 已经安装 GitHub Desktop、 Anaconda、MySQL、Redis  

### 1. 通过 GitHub Desktop 克隆项目到本地

      # GitHub 地址
      https://github.com/yijixiuxin/chanlun-pro.git
      # Gitee 地址
      https://gitee.com/wang-student/chanlun-pro

### 2. 在 `chanlun-pro` 目录，双击 `install_windows.bat` 文件进行安装

### 3. 设置 PYTHONPATH 环境变量

         # 我的电脑 -> 右键菜单选“属性” -> 高级系统设置 -> 高级 -> 环境变量 -> 系统变量 -> 新建
         # 系统变量信息，project_path 需要替换成项目所在目录
         变量名：PYTHONPATH
         变量值：project_path\chanlun-pro\src
         
         设置完成后，重启终端 ，输入命令 $env:PYTHONPATH  查看是否设置成功

### 4. 在 `src/chanlun` 目录， 复制拷贝 `config.py.demo` 文件为 `config.py` 并修改其中的 [配置项](配置文件说明.md)

### 5. 运行项目根目录中的 `check_env.py` 文件，检查环境是否OK，如果输出 “环境OK”，则可以继续进行，如果有错误，则安装提示进行修复

         conda activate chanlun
         python check_env.py

### 6. 加作者微信，获取授权许可文件，并放置在项目中的 `src/pyarmor_runtime_005445` 目录下

### 7. 在 `web/chanlun_chart` 目录，双击  `run.bat` 启动
