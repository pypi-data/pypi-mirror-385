# MCP服务开发、测试、发布全流程
## 1、在某个conda环境中(比如llm-mcp)，安装好uv：
pip install uv

## 2、PyCharm项目初始化为uv项目：
uv init .

## 3、创建、激活虚拟环境
uv venv
source .venv/bin/activate

## 4、安装 MCP SDK
uv add openai dotenv mcp

## 5、创建项目源代码
### 创建src/weather 文件夹
#### 添加 server.py 文件

## 6、本地测试（使用Inspector进行）
### 安装nodejs
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
### 运行Inspector
npx -y @modelcontextprotocol/inspector uv run ./src/weather/server.py --api_key apikey123abc

## 7、打包
### 添加__init__.py、__main__.py
### 修改pyproject.toml文件
#### 填写内容，注意[project.scripts]中的rents-mcp-weather2名称：
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project.scripts]
rents-mcp-weather2 = "weather:main"
[tool.setuptools]
package-dir = {"" = "src"}
[tool.setuptools.packages.find]
where = ["src"]
### 安装打包/发布(上传)工具包
uv pip install build twine

### 打包（回到项⽬主⽬录）
cd /Users/rents/PycharmProjects/rents-mcp-weather
python -m build

## 8、发布
python -m twine upload dist/*