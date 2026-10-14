# Notion Local Sandbox

让 Notion 通过 MCP 读写一个隔离的合成样例工作区，并执行固定检查。
这是独立社区工具，无 Notion、Docker、ngrok 或 OpenAI 官方背书。

**本版本本地验证通过；真实 Notion 联调未复验。** 已通过24项标准库测试、两个镜像的离线构建、真实MCP读写/固定检查、断网代理链路及SIGTERM清理验收。测试只用公开夹具；本版本的公网ngrok会话与Notion端到端调用未执行，不能将这些结果视为云端联调成功。通用自有源码、文档、Skill、测试和合成样例采用 [MIT 许可证](LICENSE)，署名 `z3247124509-sketch`；第三方运行依赖保留各自许可，见[许可证范围](LICENSE-STATUS.md)。

## 实际架构与范围

```text
Notion Agent（云端）
    │ HTTPS + Bearer，仅 /mcp
    ▼
ngrok 服务 → gateway 容器（允许联网，无工作区、无宿主端口映射）
                  │ 只读挂载 IPC volume，转发至 Unix socket
                  ▼
             control 容器（network=none，非 root，只读根文件系统）
                  │
                  ├─ 专用 synthetic data volume：samples/、notes/
                  └─ 两个固定检查：sample_json、self_test
```

宿主上的 `launch.py` 是受信任的生命周期控制器，只调用指定的本机 Docker CLI。
Docker socket 仅由宿主 CLI 使用，不挂载进任何容器。没有 home、钥匙串、SSH、公司目录或真实项目绑定挂载。
`workspace_root` 或路径检查并非操作系统沙箱：这里依赖 Docker 的网络命名空间、挂载边界、非 root 用户、只读根、资源限制和默认 seccomp。
Docker Desktop 在 macOS 上提供 Linux 虚拟机；仍须维护 Docker/宿主安全更新。拥有 Docker 管理权限的本地用户不在隔离威胁模型内。

公开版本特意缩小范围：不执行工作区代码，不提供任意 shell、命令参数、包安装、Git、Codex/Claude 委派、浏览器、截图或模型调用。原工作台的异步任务队列、独立 runner、静态预览及附件打包需要另外审查后才能作为扩展加入。

## Notion 前置条件

- 个人 Notion Agent 与 Custom Agent 的 MCP 功能目前均要求 Business 或 Enterprise，并受工作区管理员批准列表/自定义 MCP 开关约束。个人入口是 `Settings → Connections → Discover → Add Custom MCP`，新增连接适用于网页和桌面端。[个人 Agent 官方说明](https://www.notion.com/help/connect-mcp-servers-to-your-notion-agent)
- Custom Agent 在其设置中的 `Tools and access` 添加 MCP，官方明确支持 OAuth 或请求头认证（API key / Bearer）。本项目仅实现 Bearer，不实现 OAuth。[Custom Agent 官方说明](https://www.notion.com/help/mcp-connections-for-custom-agents)
- 个人 Agent 文档未明确枚举 Bearer 支持；应先核对当前实际界面并验收，不能把 Custom Agent 的认证支持推定到个人 Agent。不要为缺失入口自动升级订阅。
- 初次使用保持 Agent 私有。共享 Custom Agent 的成员可能通过该 Agent 调用已连接工具。写操作保留 `Always ask`；`run_check` 也建议逐次询问。这个审批是 Notion 客户端设置，服务端无法证明每个请求都经过了人工批准。
- Notion 的官方 MCP 服务“让外部 AI 访问 Notion 页面”与本项目“让 Notion 调用本地工具”方向不同，不能互相替代。

## 软件、来源与费用

| 项目 | 本审查稿基线 | 来源 / 作用 |
|---|---|---|
| 本机 Python | 3.12 或更新；离线测试使用 3.14 | [python.org](https://www.python.org/downloads/)，仅运行受信任 CLI/测试 |
| Docker | 已安装且可用的 Docker Desktop（macOS） | [官方安装](https://docs.docker.com/desktop/setup/install/mac-install/)，不附安装器 |
| Python 容器 | `3.12.15-slim-bookworm`，linux/arm64 摘要固定在 Dockerfile | [Docker Official Image](https://hub.docker.com/_/python) |
| MCP 运行依赖 | FastMCP 3.2.4、Uvicorn 0.54.0；共 67 项锁定依赖 | [PyPI](https://pypi.org/)，`requirements.lock` 含版本与 SHA-256 |
| 可选公网网关 | ngrok 3.39.8，官方 linux/arm64 镜像 | [ngrok/ngrok](https://hub.docker.com/r/ngrok/ngrok)，见下面固定摘要 |

当前 Dockerfile **仅面向 linux/arm64**。Intel Mac/Linux amd64 需要重新核验镜像、wheel 与构建；不能直接替换架构宣称支持。
所有 wheel、镜像、Docker/ngrok 程序都不在源码包内。依赖涉及 Apache、BSD、MIT、MPL 等多种许可证，见 [来源与依赖审查](docs/PROVENANCE.md)。

桥接器本身不调用付费模型，也不会绕过 Notion 额度。个人 Agent 的部分用法受使用额度限制，Custom Agents 与高级模型可能消耗 Notion credits；额度耗尽时应停止继续尝试付费调用。[额度](https://www.notion.com/help/manage-your-usage-allowance-for-notion-ai)、[积分](https://www.notion.com/help/what-are-notion-credits)
ngrok 的域名、会话和流量受账号套餐约束；Docker Desktop 也有适用订阅条件。部署前由使用者确认，不自动付费、升级或更换服务。[ngrok 定价](https://ngrok.com/pricing)、[Docker Desktop 许可](https://docs.docker.com/subscription-billing/desktop-license/)

## 分步安装与配置

以下是**供使用者审查后执行的操作说明**，不是预先授予 AI 的执行权限。每次只确认一个具体动作；同一已批准范围内不重复询问。安装/构建、秘密生成或输入、公网访问、Notion 授权和删除数据分别确认。

### 1. 只读审查与离线测试

阅读源码、[威胁边界](docs/SECURITY.md)、[发布检查表](docs/RELEASE-CHECKLIST.md)。在项目目录中使用已经安装的 Python：

```sh
python3 -I -S -B tests/test_safety.py
python3 -I -S -B src/selftest.py
```

这些测试只使用标准库和临时合成文件；不会安装依赖、读取凭据或启动 Docker。
Skill 位于 [skills/notion-local-sandbox/SKILL.md](skills/notion-local-sandbox/SKILL.md)。可以先直接阅读；如要装入助手的技能目录，再单独批准复制，不附自动安装或开机任务。

### 2. 批准下载和构建后，准备镜像

确认 Docker 已安装且运行。选择当前机器实际 Docker CLI 绝对路径与本地 Unix socket；这里只给占位值，不能原样执行。
专用空配置避免读取默认 Docker 登录凭据或 credential helper：

```sh
NS_DOCKER=/ABSOLUTE/PATH/TO/docker
NS_HOST=unix:///ABSOLUTE/PATH/TO/docker.sock
NS_CONFIG="$(pwd)/runtime/build-docker-config"
mkdir -p "$NS_CONFIG" vendor/wheels
NS_PYTHON=python@sha256:739ba32ae445e8d58f3d90feb85f83bebc8346f8dd280fa1eb5848f4ff1ed163
NS_NGROK=ngrok/ngrok@sha256:5efd9ff49cb25d320ad25dcc1f94e982e85265e266db220418d883e6300b8be5
```

公开元数据查询也应包含在审批范围。核验来源、镜像摘要和许可证，再拉取；不要使用 `latest`：

```sh
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" pull --platform linux/arm64 "$NS_PYTHON"
```

下载 wheel 的容器只挂载这份公开 lock 和新建 wheel 目录；这一步需要访问 `pypi.org`、`files.pythonhosted.org`，运行的是已核验 Python 镜像的 pip。`--only-binary` 禁止源码构建：

```sh
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" run --rm --platform linux/arm64 \
  --read-only --network bridge --cap-drop ALL --security-opt no-new-privileges=true \
  --user "$(id -u):$(id -g)" --memory 512m --pids-limit 96 --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  --mount "type=bind,src=$(pwd)/requirements.lock,dst=/requirements.lock,readonly" \
  --mount "type=bind,src=$(pwd)/vendor/wheels,dst=/wheels" \
  "$NS_PYTHON" python -I -m pip download --no-cache-dir --only-binary=:all: --no-deps \
  --require-hashes -r /requirements.lock -d /wheels
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" build --network none --pull=false \
  --platform linux/arm64 -t notion-local-sandbox:reviewed .
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" image inspect \
  --format '{{.Id}}' notion-local-sandbox:reviewed
```

构建可能需要 Docker/BuildKit 元数据通信；`RUN --network=none` 只保证构建步骤不联网，不代表整个构建控制面断网。不要将构建输出当成验收成功。
可选 gateway 另行批准后构建：

```sh
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" pull --platform linux/arm64 "$NS_NGROK"
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" build --network none --pull=false \
  --platform linux/arm64 --build-arg "NGROK_IMAGE=$NS_NGROK" \
  -f Dockerfile.gateway -t notion-local-sandbox-gateway:reviewed .
"$NS_DOCKER" --config "$NS_CONFIG" --host "$NS_HOST" image inspect \
  --format '{{.Id}}' notion-local-sandbox-gateway:reviewed
```

Dockerfile.gateway 中 ngrok 的内部二进制路径只对应上述已核验基线；更新镜像时必须重新检查路径和版本，不能自动追踪新版。

### 3. 用户安全接管认证输入与离线启动

Bearer 必须是用户专门为该会话提供的 64 个 URL-safe 字符，来自安全随机源；本工具不会生成、读取已有密钥或自动配置 OAuth。若尚无专用 token，先批准“生成一枚专用 token”，再由用户在安全环境完成，**不把值发到聊天**。
`.env.example` 只有说明占位；程序不读取 `.env`。不要把值放入命令行、环境变量、Git、截图、工单或剪贴板自动化。
用户自行在本地隐藏输入提示中输入；脚本只经进程 stdin 传输，control 仅接收 SHA-256 摘要。

将下例 image 占位替换为上一阶段实际 `sha256:...` 本地镜像 ID：

```sh
python3 -I -B launch.py offline --docker "$NS_DOCKER" --host "$NS_HOST" \
  --control-image sha256:REPLACE_WITH_LOCAL_CONTROL_IMAGE_ID
```

此时没有公网入口，也没有宿主 TCP 端口。它保持前台运行，Ctrl+C 停止本会话容器，保留专用合成数据 volume。
运行 `docker inspect` 时只查看所需的网络、挂载、用户、只读根、端口和资源限制字段；不要导出全量环境或凭据。
本审查稿已完成断网容器内的真实 Streamable HTTP/MCP 传输验收；部署到新机器仍需重新验证，见检查表。源码单测不能替代此项。

### 4. 单独批准公网会话与 Notion 连接

关闭离线会话并明确清理其合成数据后，再启动一个全新公网样例会话；不会自动把旧数据暴露出去。
用户拥有 ngrok 账号分配的免费域名，并自行输入 Authtoken。只接受 `.ngrok-free.app` / `.ngrok-free.dev`；不自动申请域名或更换套餐。

```sh
python3 -I -B launch.py remote --docker "$NS_DOCKER" --host "$NS_HOST" \
  --control-image sha256:REPLACE_WITH_LOCAL_CONTROL_IMAGE_ID \
  --gateway-image sha256:REPLACE_WITH_LOCAL_GATEWAY_IMAGE_ID \
  --domain YOUR_ASSIGNED_DOMAIN.ngrok-free.app --approved-public-session
```

这个命令意味着明确授权 gateway 出站连接 DNS/ngrok 服务；ngrok 服务提供公网 HTTPS 入口。gateway 不具备强制目的地址白名单，因此其联网运行仍属于扩展访问。宿主无入站端口映射。
ngrok Authtoken 仅进入网关 stdin 与 tmpfs 中的 0600 配置，原始厂商输出丢弃；未承诺物理内存/宿主交换空间绝不会保留字节。
Cloud Notion 和隧道服务会接触请求与返回数据，故只使用合成内容。

控制台打印“配置的 URL”不代表公网已经可用。确认未带 Bearer 的请求得到 401；有效 Bearer 的 MCP 初始化和工具列举成功；再由用户在 Notion 界面手动连接 `https://YOUR_ASSIGNED_DOMAIN.ngrok-free.app/mcp`，填入同一 Bearer。此授权是独立一步，不由助手自动提交。

## 工具权限与验收示例

| 工具 | 范围 |
|---|---|
| `list_files` | 最多列出 100 个可读样例文件 |
| `read_file` | 仅 `samples/` 或 `notes/` 下一层 `.txt/.md/.json`；UTF-8，最多 16 KiB |
| `write_file` | 同样范围，最多 100 文件；创建不覆盖，替换必须提供完整旧文本 `expected` |
| `run_check` | 只接受 `sample_json` 或 `self_test`；后者运行只读镜像内固定脚本，10 秒超时 |

不提供删除、绝对路径、隐藏文件、子目录、符号链接、硬链接或设备文件访问。
写权限对该合成 volume 有效，不是对用户电脑任意文件有效。用户通过 Docker 自行导出时需另行决定目的路径。

建议在 Notion 发送：

> 列出合成样例文件，读取 samples/example.json。在批准写操作后，创建 notes/result.txt，内容为“synthetic test passed”，读回核对，再运行 sample_json 和 self_test。拒绝读取 ../secret.txt 或 /etc/passwd。不要申请扩大目录或执行任意命令。

逐项核对实际工具结果与本地数据，不能以模型说“完成了”代替验收。

## 长任务、文件与附件边界

本精简版仅做短检查，未实现长任务队列。扩展到构建/截图等工作时，应使用独立断网 runner、固定任务枚举、任务 ID/状态查询和超时；Notion 请求超时或额度耗尽不能自动重跑有副作用的任务。
`read_file` 返回文本，不生成 Notion 原生附件。Base64、磁盘路径或 MCP resource 并不保证会显示为可下载文件。
未来 ZIP/截图导出需要分别验收“本地生成成功”和“Notion/交付通道附件可下载”；这里不承诺统一文件大小上限。大包应按实际依赖制作完整最小包，保留启动说明，并验证断网可运行。

## 停止、保留与卸载

前台 Ctrl+C 会停止并移除**本会话** control/gateway 容器；不自动删除样例 volume 或撤销 Notion/厂商凭据。若终端异常退出，使用同一项目目录：

```sh
python3 -I -B launch.py stop --docker "$NS_DOCKER" --host "$NS_HOST"
```

先确认入口已不可达；若宿主进程被强制终止，容器可能仍在运行，不能仅因窗口关闭就断言停用。
需要删除本会话合成数据时，单独批准：

```sh
python3 -I -B launch.py purge --docker "$NS_DOCKER" --host "$NS_HOST" \
  --confirm-delete-synthetic-data
```

清理按会话名字与标签双重核对，不调用全局 `docker prune`。确认文件已导出后，再选择删除本项目目录和两个专用镜像；不要卸载其他任务正在用的 Docker。
Notion MCP 连接移除、ngrok token 撤销、Skill 卸载分别由用户在对应设置中执行。这个项目不建立 launchd、cron、登录项或自动续期。

## 故障排查

| 现象 | 检查 |
|---|---|
| 没有 MCP 入口 | 核对套餐、网页/桌面版本、管理员允许列表；先报告缺失条件，不升级 |
| 401 | 用户确认同一专用 Bearer；不在聊天粘贴值，不接受 URL query token |
| 404 / 502 | 路径应为 `/mcp`；control 是否启动、IPC 是否存在；重新验收固定镜像 |
| 镜像不可用 | 先核对本地 image ID、arm64 与审批范围；启动器不会自动 pull |
| 已有 session 记录 | 先 stop，确认是否保留或导出，再显式 purge；不覆盖旧会话 |
| ngrok 失败 | 用户自行在官方账号页核对域名、Authtoken 和套餐限额；勿上传原始日志或凭据 |
| Notion 积分耗尽 | 停止模型尝试；本地服务是否继续运行与积分是两件事，按需要手动停止 |
| 读写拒绝 | 检查相对路径、扩展名、16 KiB/100 文件限制、`expected` 是否匹配；不放宽宿主权限 |
| Skill 不可见 | 核对技能安装目录及加载方式；本包默认只包含 Skill，不自动安装 |

发布前必须完成 [RELEASE-CHECKLIST](docs/RELEASE-CHECKLIST.md)。反馈问题时只提供合成复现、版本和脱敏错误类别，不附 token、域名、原始对话或真实业务文件。
