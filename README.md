## 仓库使用步骤
### 克隆仓库
```shell
git clone https://github.com/nusduck/qf5214_StockAgent
```
### 创建虚拟环境安装包
```shell
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```
### Coding
- tools编写（注意命名规范 `xxx_tools.py`
- ddl编写 `ods_xxx.sql`
- 表的字典编写

### 上传代码
通过git上传代码