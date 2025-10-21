# CodeViewX 技术文档

## 文档结构
- README.md - 本文件，概览和导航
- 01-overview.md - 项目概览
- 02-quickstart.md - 快速开始
- 03-architecture.md - 架构设计
- 04-core-mechanisms.md - 核心机制
- 05-data-models.md - 数据模型
- 06-api-reference.md - API参考
- 07-development-guide.md - 开发指南
- 08-testing.md - 测试策略

## 文档元信息
- 生成时间：2025-06-17 18:15:00
- 分析范围：19个核心文件，约3000行代码
- 主要技术栈：Python 3.8+, Flask, LangChain, DeepAgents, ripgrep

## 项目简介

CodeViewX 是一个基于 Anthropic Claude 和 DeepAgents 框架的智能代码文档生成工具。它能够自动分析代码库并生成专业的技术文档。

### 核心特性
- 🤖 **AI智能分析**：基于 Anthropic Claude、DeepAgents 和 LangChain 框架
- 📝 **完整文档体系**：自动生成 8 个核心章节的技术文档
- 🌐 **多语言支持**：支持 8 种语言（中文、英文、日文、韩文、法文、德文、西班牙文、俄文）
- 🖥️ **内置 Web 服务器**：美观的文档浏览界面，支持 Mermaid 图表
- ⚡ **高性能搜索**：集成 ripgrep 实现快速代码搜索

### 文档导航
1. **[01-overview.md](01-overview.md)** - 了解项目技术栈和目录结构
2. **[02-quickstart.md](02-quickstart.md)** - 快速安装和使用指南
3. **[03-architecture.md](03-architecture.md)** - 系统架构设计详解
4. **[04-core-mechanisms.md](04-core-mechanisms.md)** - 核心工作机制深度解析（推荐重点阅读）
5. **[05-data-models.md](05-data-models.md)** - 数据模型和配置说明
6. **[06-api-reference.md](06-api-reference.md)** - API 接口详细说明
7. **[07-development-guide.md](07-development-guide.md)** - 开发环境搭建和贡献指南
8. **[08-testing.md](08-testing.md)** - 测试策略和质量保证

## 技术栈概览

### 核心依赖
- **Python 3.8+**：主要开发语言
- **Flask 3.0.0**：Web 框架，用于文档浏览服务器
- **LangChain 0.3.27**：LLM 应用框架
- **DeepAgents 0.0.5**：AI Agent 框架
- **ripgrep 2.0.0**：高性能代码搜索工具

### 主要模块
- **CLI模块** (`cli.py`)：命令行接口
- **生成器模块** (`generator.py`)：文档生成核心逻辑
- **服务器模块** (`server.py`)：Web 文档浏览服务
- **工具模块** (`tools/`)：文件系统、搜索、命令执行工具
- **国际化模块** (`i18n.py`)：多语言支持

## 快速开始

```bash
# 安装
pip install codeviewx

# 分析当前目录并生成文档
codeviewx

# 启动文档浏览服务器
codeviewx --serve -o docs
```

详细安装和使用说明请参考：[02-quickstart.md](02-quickstart.md)

## 开发团队
- **项目维护者**：CodeViewX Team
- **许可证**：GPL-3.0-or-later
- **项目主页**：https://github.com/dean2021/codeviewx

---

⭐ 如果这个项目对您有帮助，请给个星标！