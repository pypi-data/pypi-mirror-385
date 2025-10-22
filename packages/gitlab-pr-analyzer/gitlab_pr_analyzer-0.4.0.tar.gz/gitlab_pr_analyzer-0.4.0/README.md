# GitLab PR Analyzer 使用指南

## 简介
GitLab PR Analyzer 是一个基于命令行的辅助工具，帮助你快速收集、搜索并分析 GitLab Merge Request 与提交记录。无论是审核日常工作量、定位相关改动，还是借助 AI 生成总结报告，都可以通过这一工具完成。

## 功能概览
- 收集指定项目在时间窗口内的打开与已合并 Merge Request
- 搜索 Merge Request 与提交记录，支持按关键字匹配和得分排序
- 查看单个 Merge Request 或提交的详细信息
- 遍历近期 Merge Request 并批量生成 AI 分析报告
- 交互式浏览模式，方便探索数据
- 可选的 AI 总结功能（依赖 cursor-agent）

## 安装

### 从 PyPI 安装
```bash
pip install gitlab-pr-analyzer
```

### 从源码安装
```bash
git clone https://github.com/your-org/gitlab-pr-analyzer.git
cd gitlab-pr-analyzer
pip install .
```

如果需要在离线环境部署，可以使用仓库中的 wheel 包：
```bash
pip install dist/gitlab_pr_analyzer-0.3.0-py3-none-any.whl
```

## 环境要求
- Python 3.8 及以上版本
- 已安装 `git` 并可在命令行执行
- 已安装 `glab`（GitLab CLI），并完成 `glab auth login`
- 可访问目标 GitLab 实例的网络权限
- GitLab Personal Access Token，需至少具备 `api` 或 `read_api` scope

> `glab` 被用于获取 Merge Request diff 内容（例如 `traverse` 命令中的 AI 分析），请提前在本地或 CI 环境安装并完成认证。

## 连接私有化部署的 GitLab
GitLab PR Analyzer 通过环境变量读取访问配置，以下设置适用于官方与私有化部署：

```bash
export GITLAB_HOST="https://gitlab.example.com"
export GITLAB_TOKEN="<your-token>"
export GITLAB_INSTANCE_NAME="Example GitLab"
```

- `GITLAB_HOST`：你的私有 GitLab 基础地址，必须包含协议（例如 `https://`）。
- `GITLAB_TOKEN`：来自目标 GitLab 的 Personal Access Token，建议包含 `read_api` 或 `api` 权限，以便读取 Merge Request 与提交数据。
- `GITLAB_INSTANCE_NAME`：可选，用于在命令行 Banner 中显示实例名称。
- `CURSOR_AGENT_PATH`：可选，如需启用 AI 分析，请设置为 cursor-agent 可执行文件路径。

> 提示：若私有化实例使用自签证书，可通过设置 `REQUESTS_CA_BUNDLE` 或在系统信任证书后再运行工具。

在 CI 环境中，可通过注入环境变量或配置管理工具（如 Ansible、Vault）安全地分发 Token。

## 快速开始
1. 在本地仓库中进入你希望分析的 Git 项目目录。
2. 设置上文描述的环境变量。
3. 执行示例命令：

```bash
gl-pr-analyzer collect --project group/subgroup/project --months 3
```

命令执行后会输出最新的打开与已合并 Merge Request 概览，并统计本地仓库对应时间窗口内的提交数量。

## CLI 命令说明

### collect
收集 Merge Request 与提交。

```bash
gl-pr-analyzer collect --project group/project --months 6
```

- `--project/-p`：GitLab 项目路径，留空时工具会尝试根据当前仓库远程地址自动识别。
- `--months/-m`：向前回溯的月数，默认 3。
- `--days/-d`：以天为单位的回溯窗口，设置后将覆盖 `--months`。

### search
按照关键字在 Merge Request 与提交之间匹配。

```bash
gl-pr-analyzer search "payment bugfix" --project group/project --days 120 --min-score 40 --max-results 15
```

- `--min-score`：最低匹配得分（0-100），默认 30。
- `--max-results`：返回结果数量上限，默认 20。
- `--analyze/-a`：若开启并且配置了 `CURSOR_AGENT_PATH`，会对得分最高的结果执行 AI 分析。

### view_mr
查看单个 Merge Request 详情并可选触发 AI 总结。

```bash
gl-pr-analyzer view_mr 1024 --project group/project --analyze
```

- 指定 Merge Request IID（非 ID）。

### view_commit
查看单个提交详情。

```bash
gl-pr-analyzer view_commit 3f5e9a1 --analyze
```

### interactive
启动交互式浏览体验。

```bash
gl-pr-analyzer interactive
```

根据提示可选择搜索、查看 Merge Request 或提交详情，并在可用时触发 AI 分析。

### traverse
遍历最近的 Merge Request，逐条执行 AI 分析并可生成统一报告。

```bash
gl-pr-analyzer traverse --project group/project --days 45
```

- `--days/-d`：向前回溯的天数，默认 60。
- `--project/-p`：项目路径，留空时自动识别。
- 需要提前配置 `CURSOR_AGENT_PATH`，否则命令将直接退出。
- 运行过程中会提示是否把分析结果写入 Markdown 报告。

## AI 分析功能
- 需要安装 cursor-agent，并将其可执行路径写入 `CURSOR_AGENT_PATH`。
- AI 分析会调用 cursor-agent 的 `agent` 模式生成总结报告，可单独保存。
- 若未配置 `CURSOR_AGENT_PATH`，命令会给出提示但不会中断主要流程。

## 日常实用建议
- 在执行 `collect` 或 `search` 前，确保本地仓库已 `git fetch`，以便 commit 数据与远端同步。
- 如果需要长期运行，可将环境变量写入 shell 配置文件或专用 `.env` 再通过 `source` 加载。
- 遇到 401/403 错误时，优先检查 Token 权限与项目可见性。
- 使用自建 GitLab 时，建议为 API 访问创建专用服务账号并限制权限。

## 获取更多帮助
```bash
gl-pr-analyzer --help
gl-pr-analyzer collect --help
gl-pr-analyzer search --help
```

欢迎根据团队需求扩展命令或结合现有 CI/CD 流程使用。若有新需求，可在 Issue 中描述使用场景与期望行为。

