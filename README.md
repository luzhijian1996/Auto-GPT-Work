# Auto-GPT-Work

基于 LangChain 和 ReAct 模式实现的智能数据分析助手。通过自然语言对话，自动拆解任务、调用工具、多步推理，完成数据分析与文档处理等复杂任务。

## 项目架构

```
├── Agent/              # 智能体核心
│   ├── ReAct.py        # ReAct Agent 实现（思考→行动→观察循环）
│   └── Action.py       # 动作定义（Pydantic 模型）
├── Models/
│   └── Factory.py      # 模型工厂（支持 OpenAI / Azure / DashScope / SiliconFlow）
├── Tools/              # 工具集（LangChain StructuredTool 封装）
│   ├── FileQATool.py   # 文档问答（基于 Chroma 向量数据库）
│   ├── ExcelTool.py    # Excel 表格探查
│   ├── PythonTool.py   # Excel 数据分析器（LLM 驱动）
│   ├── WriterTool.py   # 文档生成
│   ├── EmailTool.py    # 邮件发送
│   ├── FileTool.py     # 目录浏览
│   └── FinishTool.py   # 任务结束占位符
├── Utils/              # 工具类（回调处理、彩色打印）
├── prompts/            # 提示词模板
│   ├── main/main.txt   # 主系统提示词
│   └── tools/          # 工具专用提示词
├── data/               # 数据文件目录
├── main.py             # 程序入口
└── requirements.txt    # 依赖清单
```

## 技术栈

- **Python 3.11**
- **LangChain 0.1.19** — LLM 应用框架
- **ChromaDB** — 向量数据库（文档问答）
- **DashScope / OpenAI** — 大语言模型服务
- **Pydantic** — 结构化输出解析

## 环境配置

### 1. 创建 `.env` 文件

在项目根目录创建 `.env`，根据使用的模型配置对应的 API Key：

```env
# DashScope（通义千问系列，默认使用）
DASHSCOPE_API_KEY=sk-xxxx

# OpenAI（可选）
OPENAI_API_KEY=sk-xxxx

# SiliconFlow（可选，开源模型平台）
SILICONFLOW_API_KEY=sk-xxxx

# Azure OpenAI（可选）
AZURE_OPENAI_API_KEY=xxxx
AZURE_OPENAI_ENDPOINT=https://xxxx.openai.azure.com/
```

### 2. 设置环境变量（Windows 可跳过）

Linux/macOS 下需要设置：

```bash
export HNSWLIB_NO_NATIVE=1
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

启动后进入交互式对话：

```
🤖：有什么可以帮您？
👨：9月份的销售额是多少
```

输入 `quit` 退出。

## 内置工具

| 工具 | 说明 |
|---|---|
| **AskDocument** | 基于文档内容回答问题（支持 PDF/Word） |
| **GenerateDocument** | 根据需求生成正式文档 |
| **SendEmail** | 向指定邮箱发送邮件 |
| **InspectExcel** | 探查 Excel 文件的结构和内容 |
| **ListDirectory** | 浏览目录结构和文件列表 |
| **ExcelAnalyser** | LLM 驱动的 Excel 数据分析器 |
| **FINISH** | 结束任务并返回最终结果 |

## 示例问题

- 9月份的销售额是多少？
- 销售总额最大的产品是什么？
- 帮我找出销售额不达标的供应商
- 给这两家供应商发一封邮件通知此事
- 对比8月和9月销售情况，写一份报告

## 支持的模型

通过修改 `main.py` 中的模型名称切换：

```python
# DashScope 通义千问（默认）
llm = ChatModelFactory.get_model("qwen3.8-flash")

# OpenAI GPT 系列
# llm = ChatModelFactory.get_model("gpt-4o")

# Azure OpenAI
# llm = ChatModelFactory.get_model("gpt-4o", use_azure=True)

# SiliconFlow 开源模型
# llm = ChatModelFactory.get_model("qwen2")
```
