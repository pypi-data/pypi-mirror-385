# Weather-X 天气查询工具

Weather-X 是一个基于 FastMCP 框架开发的天气查询工具，可以获取中国各城市的天气信息和警报。

## 功能特性

- 获取指定城市的天气信息
- 查询天气警报
- 基于高德地图天气API实现
- 支持异步请求处理

## 安装

```bash
pip install weather-x
```

或从源码安装：

```bash
git clone <repository-url>
cd weather-x
pip install -e .
```

## 使用方法

```python
from weather import mcp

# 运行MCP服务器
mcp.run(transport='stdio')
```

或直接运行：

```bash
python main.py
```

## API接口

### get_alerts(city: str) -> str

获取指定城市的天气警报信息。

参数:
- city: 城市名称（例如：北京、上海）

返回:
- 包含天气信息的字符串

## 依赖

- Python >= 3.12
- fastmcp >= 2.12.4
- httpx >= 0.28.1
- mcp[cli] >= 1.18.0

## 配置

项目使用高德地图天气API，需要在代码中配置API密钥。

## 开发

安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 许可证

MIT