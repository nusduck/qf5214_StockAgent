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
- ddl编写 `ods_xxx.sql`，文件放置在`database/ddl` 下
- 表的字典编写

### 上传代码
通过git上传代码

### Reference
- tools 的编写可以参考 `tools/demo_stock_tools.py` 这个脚本
- `reference.md` 是langchain tools和agents的开发规范，可以把这个文件丢给大模型；
- `prj_document/数据库分层设计方案.md` 这是是数据库设计的说明，大家写ddl可以参考一下，还有数据字典的时候。