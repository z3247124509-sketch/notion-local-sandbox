# 来源、27 文件清单与许可证结论

核查日期：2026-10-14。权利人已批准向公开仓库 `z3247124509-sketch/notion-local-sandbox` 发布通用自有代码、文档、Skill、测试和合成样例；采用 MIT，署名 `z3247124509-sketch`。

## 当前分发结论

本包只包含下列27个文本文件：通用源码、Skill、文档、合成样例、锁文件和审查元数据。
**不分发 wheel、Rust crate、Python/Debian/ngrok 镜像、二进制、真实项目、凭据或日志。**
本轮另行授权的构建在本地 Docker 内安装了依赖用于测试；宿主 Python 未安装这些包。

67 个 Python 依赖的顶层及已附多许可已逐项查明；当前源码包没有因依赖“许可证类型未知”而悬置的条目。
自有部分的 MIT 授权见根目录 LICENSE；第三方元数据保留原归属，依赖和外部程序仍适用各自许可证，不被本项目重新授权。

## 逐文件来源

| 文件 | 来源及处理 |
|---|---|
| `.dockerignore` | 新写；只允许公开源码、样例、lock 和审批后的 wheel 构建输入。 |
| `.env.example` | 新写；只有不可用占位值，程序不读取此文件。 |
| `.gitignore` | 新写；排除真实环境配置、构建产物、日志及运行状态。 |
| `Dockerfile` | 新写；引用固定官方 Python 基线，依赖来自已核验 lock。 |
| `Dockerfile.gateway` | 新写；多阶段只复制官方 ngrok 程序，不复制 vendor 镜像文件系统。 |
| `LICENSE` | 标准 MIT 许可文本；按权利人批准，以已核验 GitHub 账号署名。 |
| `LICENSE-STATUS.md` | 新写；记录已批准的 MIT 许可、署名和第三方分发边界。 |
| `PUBLICATION-MANIFEST.json` | 由 package_review.py 生成；列出其余26文件的长度和哈希。 |
| `README.md` | 新写；通用配置、授权、成本、停用及交付边界。 |
| `VERIFICATION.md` | 新写；本版本实际测试结果及未执行项目。 |
| `docs/PROVENANCE.md` | 新写；本逐文件清单、公开源及许可证结论。 |
| `docs/RELEASE-CHECKLIST.md` | 新写；发布与部署分开审批。 |
| `docs/SECURITY.md` | 新写；真实容器边界及威胁模型。 |
| `docs/dependency-license-inventory.json` | 从公开包/镜像资料与合成测试结果逐字段组装；不含依赖代码。 |
| `fixtures/notes/welcome.md` | 新写的合成样例，没有业务文本。 |
| `fixtures/samples/example.json` | 新写的合成样例，没有真实数据。 |
| `launch.py` | 新写通用生命周期控制器；沿用本次会话已审查的隔离设计，不复制业务代码。 |
| `package_review.py` | 新写；按固定白名单打包、校验 SHA-256。 |
| `requirements.lock` | 逐文件复制此前公开 PyPI 包锁；67 个 wheel 哈希均匹配。 |
| `skills/notion-local-sandbox/SKILL.md` | 新写；通用技能流程及逐动作授权边界。 |
| `src/auth.py` | 改写本次会话创建的通用 ASGI Bearer 包装层；去除机器和会话设置。 |
| `src/gateway.py` | 新写；采用本次会话通用临时配置设计，不复制任何认证值。 |
| `src/origin_proxy.py` | 逐文件复制本次会话创建的通用代理；修改名称并加入完整请求截止时间。 |
| `src/safe_files.py` | 新写；描述符相对读写及小文本限制。 |
| `src/selftest.py` | 新写；只运行只读镜像内固定测试。 |
| `src/server.py` | 新写精简 MCP；网络检查依据已观察 Docker 内核行为及本次会话隔离逻辑修正。 |
| `tests/test_safety.py` | 新写；24 项标准库安全/功能回归测试，公开夹具。 |

## 参考仓库与权属边界

参考 [catoncat/notion-local-ops-mcp](https://github.com/catoncat/notion-local-ops-mcp/tree/26982c862c76ec3ecaf6194bb38713403136dd05)
该固定提交的 [LICENSE](https://github.com/catoncat/notion-local-ops-mcp/blob/26982c862c76ec3ecaf6194bb38713403136dd05/LICENSE)
为 MIT，版权行为 Copyright (c) 2026，没有具名权利人。本包没有复制其原始 Python 模块、shell/executor、安装器或 launchd 脚本。
用户已批准将本次会话新增的通用实现作为自有部分按 MIT 发布，并指定以已核验 GitHub 账号署名；不声称任何公司拥有或背书本项目。
未来引入上游实质代码时须保留适用 MIT 版权和许可文本。

## 基础镜像与仅运行时组件

| 组件 | 已核实证据与许可 | 当前分发 |
|---|---|---|
| Python 3.12.15 slim-bookworm arm64 | 固定镜像实际含 Python LICENSE.txt，PSF 与历史许可；105 个已安装 Debian 包均有对应 copyright 文件；Python/pip 加上系统共107份记录 | 不分发镜像；仅本机测试/用户自行构建 |
| Debian 用户态 | 包含 GPL、LGPL、BSD、MIT、Apache、MPL 等。105项版本、版权文件哈希和原始 License 字段在 JSON；不能把整个镜像标为 MIT | 不分发镜像或系统文件 |
| glibc 2.36 | 实际版权文件说明库主体 LGPL-2.1-or-later、相关工具 GPL-2.0-or-later，另含 BSD 部分 | 不分发 |
| bash 5.2 / coreutils 9.1 | 主体 GPL-3.0-or-later，版权文件另记录文档/辅助文件许可 | 不分发 |
| OpenSSL/libssl 3.0.22 | 主体 Apache-2.0；Debian copyright 同时覆盖源码包里的其他文件，不等于所有字段都在运行时库内 | 不分发 |
| libffi / SQLite / zlib | libffi 主体 MIT/Expat；SQLite 核心公有领域；zlib 为 Zlib；Debian 源码包版权文件含额外构建/测试文件许可 | 不分发 |
| 系统 ca-certificates | Debian 脚本 GPL-2.0-or-later；Mozilla 根证书数据 MPL-2.0 | 不分发 |
| pip 25.0.1 | 镜像内 MIT LICENSE；vendor.txt 列出18个依赖，分别为 Apache/BSD/ISC/MIT/MPL/PSF。对应版本类型从官方来源补核，镜像内未找到这些 vendor 的单独许可附件 | 不分发；作为本地构建工具使用 |
| ngrok 3.39.8 | 官方 agent，受厂商服务条款约束；不是本项目可以重新授予 MIT/Apache 的开源程序。已离线执行 version | 不分发 agent 或镜像；用户从官方来源自行取得 |

Python 基线：`sha256:739ba32ae445e8d58f3d90feb85f83bebc8346f8dd280fa1eb5848f4ff1ed163`。
ngrok vendor 基线：`sha256:5efd9ff49cb25d320ad25dcc1f94e982e85265e266db220418d883e6300b8be5`。
ngrok vendor 镜像有86份可读系统版权文本；Dockerfile.gateway 只复制 agent 二进制，vendor 的 Debian 层不会进入成品 gateway。
gateway 自己的 Python/Debian 层仍适用上述 Python 基线的许可。

[Python 官方许可](https://docs.python.org/3.12/license.html)、[官方 Python 镜像](https://hub.docker.com/_/python)、
[pip 25.0.1 配置](https://github.com/pypa/pip/blob/25.0.1/pyproject.toml)、
[ngrok 条款](https://ngrok.com/tos)、[Docker Desktop 订阅条款](https://www.docker.com/legal/docker-subscription-service-agreement/)。

ngrok 条款对 agent 再分发设有限制，向自行持有 ngrok 账号的客户分发需事先书面同意；不要直接发布含 agent 的镜像。
若以后分发 Python/Debian 成品镜像，须保留各包版权/许可，并按 GPL/LGPL/MPL 等适用条款提供对应源码、修改和链接所需材料。
镜像来源为官方并不替代再分发义务。

## 具体未闭合事项（只针对将来二进制发行）

1. CFFI/PyYAML 原生轮子的 libffi/libyaml 精确静态版本和组件附件，不能仅靠顶层许可证证明。
2. Rust 180个锁定版本已核验官方元数据及校验和，但尚未审阅每份原文或建立实际 ELF 的裁剪后 SBOM。
3. cryptography 静态 OpenSSL 的版本和 Apache-2.0 已查明，成品仍需完整第三方 notices。
4. pip 基线未携带18个 vendor 独立许可附件；将来重发镜像需补齐或去掉不需要的构建工具。
5. ngrok 二进制再分发须符合具体厂商授权；本轮的源码包没有包含它。

以上事项针对将来的二进制发行；本轮仅批准通用文本源码发布，仓库名、公开范围与自有部分 MIT 许可证均已明确批准。

# 依赖许可证逐项核对

本报告只覆盖公开源码审查包的依赖部分。许可证审计通过静态读取67个 wheel完成；另行授权的离线容器测试安装并运行了它们，宿主未安装。67 个 SHA-256 均在项目 requirements.lock 中匹配。审查包只分发锁文件和元数据；wheel、Rust crate 和镜像均不装入审查包。

## 结论

对当前不含依赖代码的源码包，67 个 Python 依赖的顶层/已附多许可归属已查清，没有需要因未知顶层许可证而暂停源码审查的条目。不能据此宣称 wheel/容器镜像的完整二进制再分发已清关，亦不替作者选择新代码许可证。

66 个 wheel 自带许可文本；dnspython 2.9.0 的缺失附件已从官方版本 LICENSE 补证 ISC。6 个 wheel 含原生 ELF。没有在这些 wheel 中发现独立名为 NOTICE 的文件；已记录 LICENSE/AUTHORS 和 vendor/LICENSES.txt 等归属材料。

## 逐项结果

| 依赖 | 版本 | 文本确认的许可 | 归属/额外材料与范围 |
|---|---|---|---|
| aiofile | 3.12.3 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| annotated-types | 0.8.0 | MIT | Copyright (c) 2022 the contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| anyio | 4.15.1 | MIT | Copyright (c) 2018 Alex Grönholm。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| attrs | 26.1.0 | MIT | Copyright (c) 2015 Hynek Schlawack and the attrs contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| Authlib | 1.8.0 | BSD-3-Clause | Copyright (c) 2017, Hsiaoming Yang。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| beartype | 0.23.1 | MIT | Copyright (c) 2014-2026 Beartype authors.。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| cachetools | 7.2.1 | MIT | Copyright (c) 2014-2026 Thomas Kemmer。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| caio | 0.12.9 | Apache-2.0 | Copyright 2025 Dmitry Orlov <me@mosquito.su>。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| certifi | 2026.7.22 | MPL-2.0 | 详见包内许可文件（未猜测权利人）。包内 LICENSE 是 Mozilla CA 根证书来源与 MPL-2.0 告知，不是完整 MPL；官方 MPL 全文可访问。无需因此把独立桥接器源文件改为 MPL。 |
| cffi | 2.1.1 | MIT-0 | 详见包内许可文件（未猜测权利人）。wheel 含 _cffi_backend ELF；DT_NEEDED 只有 libpthread/libc，没有独立 libffi 动态库。顶层 MIT-0 已确认；CFFI 使用的 libffi 是单独 MIT 项目，不能据顶层许可将其改标为 MIT-0。本 wheel 没有独立 libffi 许可/版本证据，精确静态组件版本与其文件级 notices 未由 wheel 证明。 |
| click | 8.5.0 | BSD-3-Clause | Copyright 2014 Pallets。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | Copyright (c) Individual contributors.。wheel 含 Rust ELF，静态字串 OpenSSL 4.0.3 29 Sep 2026；DT_NEEDED 无 libssl/libcrypto，配合官方静态 wheel 文档支持内含 OpenSSL 的结论。OpenSSL 4.0.3 官方 LICENSE.txt 为 Apache-2.0；wheel 只附 cryptography 双许可，未附完整 Rust/OpenSSL 组件告知清单。 |
| cyclopts | 5.2.0 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| dnspython | 2.9.0 | ISC | Dnspython Contributors；Nominum, Inc. (2001–2017)；Google Inc.。唯一无包内 LICENSE 的 wheel。已用官方 v2.9.0/LICENSE 原文补证 ISC，含 Dnspython Contributors、Nominum、Google 归属。当前不再分发 wheel；若以后再分发，应随包补足该文本。 |
| docstring_parser | 0.18.0 | MIT | Copyright (c) 2018 Marcin Kurczewski。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| email-validator | 2.3.0 | Unlicense | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| exceptiongroup | 1.3.1 | MIT AND PSF-2.0 | Copyright (c) 2022 Alex Grönholm。LICENSE 明确声明包含复制的 Python 标准库代码，并附 PSF-2.0；不能只记 MIT。 |
| fastmcp | 3.2.4 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| griffelib | 2.3.2 | ISC | Copyright (c) 2021, Timothée Mazzucotelli and contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| h11 | 0.16.0 | MIT | Copyright (c) 2016 Nathaniel J. Smith <njs@pobox.com> and other contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| httpcore | 1.0.9 | BSD-3-Clause | Copyright © 2020, [Encode OSS Ltd](https://www.encode.io/).。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| httpx | 0.28.1 | BSD-3-Clause | Copyright © 2019, [Encode OSS Ltd](https://www.encode.io/).。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| httpx-sse | 0.4.3 | MIT | Copyright (c) 2022 Florimond Manca。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| idna | 3.20 | BSD-3-Clause | Copyright (c) 2013-2026, Kim Davies and contributors.。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| jaraco.classes | 3.4.0 | MIT | 详见包内许可文件（未猜测权利人）。包内 MIT 文本没有具体版权持有人行；如再分发应保留原文件，不擅自补猜权利人。 |
| jaraco.context | 6.1.2 | MIT | Copyright (c) 2026 <copyright holders>。MIT 原文版权行为 <copyright holders> 占位；按原样保留，不能凭元数据推定已核实权利链。 |
| jaraco.functools | 4.6.0 | MIT | Copyright (c) 2026 <copyright holders>。MIT 原文版权行为 <copyright holders> 占位；按原样保留，不能凭元数据推定已核实权利链。 |
| jeepney | 0.9.0 | MIT | Copyright (c) 2017 Thomas Kluyver。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| joserfc | 1.7.5 | BSD-3-Clause | Copyright (c) 2023, Hsiaoming Yang。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| jsonref | 1.1.0 | MIT | Copyright (C) 2013 Chase Sterling。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| jsonschema | 4.26.0 | MIT | Copyright (c) 2013 Julian Berman。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| jsonschema-path | 0.5.0 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| jsonschema-specifications | 2025.9.1 | MIT | Copyright (c) 2022 Julian Berman。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| keyring | 25.7.0 | MIT | Copyright (c) 2025 <copyright holders>。MIT 原文版权行为 <copyright holders> 占位；按原样保留，不能凭元数据推定已核实权利链。 |
| markdown-it-py | 4.2.0 | MIT | Copyright (c) 2020 ExecutableBookProject；Copyright (c) 2014 Vitaly Puzrin, Alex Kocharin.。附带 LICENSE.markdown-it（Vitaly Puzrin、Alex Kocharin），同为 MIT，需要同时保留。 |
| mcp | 1.30.0 | MIT | Copyright (c) 2024 Anthropic, PBC。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| mdurl | 0.1.2 | MIT | Copyright (c) 2015 Vitaly Puzrin, Alex Kocharin.；Copyright (c) 2021 Taneli Hukkinen。同一 LICENSE 包含 mdurl、Node/Joyent 的 MIT 归属，需完整保留。 |
| more-itertools | 11.1.0 | MIT | Copyright (c) 2012 Erik Rose。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| openapi-pydantic | 0.6.0 | MIT | Copyright (c) 2023 mike-oakley；Copyright (c) 2020 Kuimono。许可证有 mike-oakley 与 Kuimono 两组 MIT 归属。包中 license.py 是模型源码，不是许可文件。 |
| opentelemetry-api | 1.45.1 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | Copyright (c) Donald Stufft and individual contributors.。顶层 Apache-2.0 OR BSD-2-Clause；packaging/licenses/*.py 是程序源码而非许可附件，本报告不误将其当许可证。 |
| pathable | 0.6.0 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| platformdirs | 4.13.0 | MIT | Copyright (c) 2010-202x The platformdirs developers。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| py-key-value-aio | 0.4.6 | Apache-2.0 | Copyright 2025 strawgate。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| pycparser | 3.11 | BSD-3-Clause | Copyright (c) 2008-2027, Eli Bendersky。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| pydantic | 2.14.1 | MIT | Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| pydantic_core | 2.50.1 | MIT | Copyright (c) 2022 Samuel Colvin。wheel 含 Rust ELF；官方 pydantic v2.14.1/pydantic-core/Cargo.toml 确认 core 2.50.1。Cargo.lock 包括 PyO3、regex、serde、url/idna、ICU/Unicode 数据等；顶层 MIT 不覆盖成单一许可。 |
| pydantic-settings | 2.15.0 | MIT | Copyright (c) 2022 Samuel Colvin and other contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| Pygments | 2.21.0 | BSD-2-Clause | Copyright (c) 2006-2022 by the respective authors (see AUTHORS file).。BSD-2-Clause 归属指向 AUTHORS 文件，二者一并保留。 |
| PyJWT | 2.15.1 | MIT | Copyright (c) 2015-2022 José Padilla。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| pyperclip | 1.11.0 | BSD-3-Clause | Copyright (c) 2014, Al Sweigart。METADATA 仅写 BSD；LICENSE.txt 三个条件含禁止以作者背书，故确认为 BSD-3-Clause。 |
| python-dotenv | 1.2.4 | BSD-3-Clause | Copyright (c) 2014, Saurabh Kumar (python-dotenv), 2013, Ted Tieken (django-dotenv-rw), 2013, Jacob Kaplan-Moss (django-dotenv)。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| python-multipart | 0.0.32 | Apache-2.0 | 详见包内许可文件（未猜测权利人）。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| PyYAML | 6.0.3 | MIT | Copyright (c) 2017-2021 Ingy döt Net；Copyright (c) 2006-2016 Kirill Simonov。wheel 含 yaml/_yaml ELF；DT_NEEDED 只有 libpthread/libc，没有独立 libyaml 动态库。PyYAML 和官方 libyaml 都有 MIT 文本，但本 wheel 没有独立 libyaml 版本/NOTICE。不能仅据依赖名证明精确嵌入版本。 |
| referencing | 0.37.0 | MIT | Copyright (c) 2022 Julian Berman。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| rich | 15.0.0 | MIT | Copyright (c) 2020 Will McGugan。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| rich-rst | 2.2.0 | MIT AND BSD-2-Clause AND BSD-3-Clause AND LicenseRef-Public-Domain | Copyright © 2011, 2017 Günter Milde.；Copyright © 2010–2023 Günter Milde,；original SmartyPants © 2003 John Gruber,。随包 vendor/LICENSES.txt 逐项记录 41 个 Docutils 模块：39 公有领域、2 BSD-2-Clause，其中 smartquotes 又含 SmartyPants BSD-3-Clause 派生告知。归档未含 rst.el；不因上游整个 Docutils 的 GPL 标签误判本子集。 |
| rpds-py | 2026.9.1 | MIT | Copyright (c) 2023 Julian Berman。wheel 含 Rust ELF；官方 v2026.9.1 Cargo.toml 含 rpds 1.2.1、archery 1.2.2、PyO3。rpds/archery 官方许可均为 MIT（Diogo Sousa）；更多版本和许可见 Rust 元数据清单。 |
| SecretStorage | 3.5.0 | BSD-3-Clause | Copyright 2012-2025 Dmitry Shachnev <mitya57@gmail.com>。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| sse-starlette | 3.5.0 | BSD-3-Clause | Copyright © 2020, [sysid](https://sysid.github.io/).。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| starlette | 1.7.0 | BSD-3-Clause | Copyright © 2018, [Encode OSS Ltd](https://www.encode.io/).。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| typing_extensions | 4.16.0 | PSF-2.0 | Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam,。PSF-2.0 许可文件同时附 Python 的 BeOpen/CNRI/CWI 历史文本及文档示例 0BSD，保留整份文件，不能删成短 PSF 标签。 |
| typing-inspection | 0.4.4 | MIT | Copyright (c) Pydantic Services Inc. 2025 to present。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| uncalled-for | 0.4.1 | MIT | Copyright (c) 2025 Chris Guidry.。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| uvicorn | 0.54.0 | BSD-3-Clause | Copyright © 2017-present, [Encode OSS Ltd](https://www.encode.io/).。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |
| watchfiles | 1.3.0 | MIT | Copyright (c) 2017 to present Samuel Colvin。wheel 含 Rust ELF；官方 v1.3.0 Cargo.toml 包含 crossbeam-channel、notify、PyO3。notify 8.0.0 注册表声明 CC0-1.0，不能将所有内含代码简化为 MIT。 |
| websockets | 17.2 | BSD-3-Clause | Copyright (c) Aymeric Augustin and contributors。本轮未在许可附件发现额外不同许可组件；不等同穷举包内每个源文件。 |

完整证据位置、文件哈希、官方项目来源、逐项义务和 180 个 Rust 版本元数据见 dependency-license-inventory.json 中的 detailed_license_audit。表中归属仅为摘录，再分发时应保留对应完整文本。

## 重点区别

- **certifi：MPL-2.0。** 保留受覆盖根证书来源/许可告知；如果分发其可执行形式，需要让接收者取得受覆盖源码。独立桥接器文件不因此自动改为 MPL。[Mozilla 原文](https://www.mozilla.org/en-US/MPL/2.0/)。
- **dnspython：ISC。** wheel 缺附件，但 [v2.9.0 官方 LICENSE](https://raw.githubusercontent.com/rthalley/dnspython/v2.9.0/LICENSE) 有完整文本和 Dnspython/Nominum/Google 归属，问题已定点查清。
- **cryptography：顶层 Apache-2.0 OR BSD-3-Clause。** ELF 中的版本字串指向 OpenSSL 4.0.3，官方 [OpenSSL 4.0.3 LICENSE](https://raw.githubusercontent.com/openssl/openssl/openssl-4.0.3/LICENSE.txt) 为 Apache-2.0。官方文档说明 Linux wheel 静态链接；这与 ELF 不依赖动态 libssl 的观察一致。顶层双许可不能代替 OpenSSL 及 Rust 组件 notices。
- **cffi：2.1.1 顶层 MIT-0。** libffi 为独立 MIT 项目。当前 wheel 没有 libffi 精确版本或单独许可附件，不能断言整个 ELF 只有 MIT-0。
- **pyperclip：BSD-3-Clause。** 已从三个条件的原文确认，不沿用含糊的 BSD 元数据。
- **exceptiongroup：MIT＋PSF-2.0；rich-rst：MIT＋公有领域＋BSD 2/3-Clause。** 两者的已附完整文本必须保留。rich-rst 的特定 vendored 子集不包含 Docutils 的 GPL Emacs 文件。
- **Rust 原生扩展：** 官方版本锁文件中 180 个不同 crate 版本的注册表校验和全部匹配；许可证类型来自 crates.io 版本元数据，不能称为 180 份原文都审阅完毕，也不能将跨平台/开发依赖全称为最终 ELF 内含组件。

## 许可义务摘要

- **MIT：** 再分发代码或实质部分时保留版权和许可/免责文本。
- **MIT-0：** 该顶层许可无署名条件；不要把它扩展到另附许可的组件。
- **BSD-2-Clause：** 源码保留版权、条件和免责；二进制在随附文档/材料中重现这些文本。
- **BSD-3-Clause：** 源码/二进制保留版权、条件和免责；不得借原作者/项目名称背书。
- **Apache-2.0：** 再分发附 Apache 2.0；保留适用的版权/专利/归属及 NOTICE；修改文件标记改动，遵守专利和商标条款。
- **ISC：** 副本保留版权和许可/免责文本。
- **Unlicense：** 包含公有领域奉献及免责文本；保留原文方便接收者识别来源。
- **MPL-2.0：** 保留 MPL 告知；分发受覆盖源码/修改仍适用 MPL；若分发可执行形式，要让接收者合理取得受覆盖源码。独立文件组成的较大作品可采用其他许可。
- **PSF-2.0：** 保留 PSF 及所附历史许可、版权/免责；分发修改版时简述修改，不借 PSF 背书。
- **Apache-2.0 OR BSD-3-Clause：** 顶层代码可按 Apache 2.0 或 BSD 3-Clause 其中一支遵守；其原生附带组件另行计入。
- **Apache-2.0 OR BSD-2-Clause：** 顶层代码可按 Apache 2.0 或 BSD 2-Clause 其中一支遵守；保留选定许可及归属。
- **MIT AND PSF-2.0：** 保留 MIT 及复制的 Python 标准库代码所附 PSF 文本；修改 Python 派生部分时简述修改。
- **MIT AND BSD-2-Clause AND BSD-3-Clause AND LicenseRef-Public-Domain：** 保留顶层 MIT 与 vendor/LICENSES.txt 全文；包括 BSD 2/3-Clause 和 Docutils 公有领域声明。

## 原生组件的具体边界

- CFFI/PyYAML wheel 内 libffi/libyaml 精确嵌入版本和文件级 notices 未由包内文件证明。
- 4 个 Rust 扩展的版本锁包含 180 个 crate 版本；已核验官方元数据/校验和，但未完成 180 份许可原文审阅或确定最终 ELF 中每个编译组件。
- cryptography wheel 未附 OpenSSL/Rust 完整组件 notices；已确定静态 OpenSSL 4.0.3 及其 Apache-2.0 官方许可。
- 若未来分发镜像或 wheel，要按实际成品补足源码/NOTICE/许可附件，并与基础系统组件许可证一并审查；本轮不分发这些成品。

OR 是可选择的许可分支，不应因为 self_cell 有 GPL 或 r-efi 有 LGPL 的可选分支就称二进制必然强制 GPL；Unicode 的 AND 条款则不能丢弃。最终构建是否包含这些 crate 未由锁文件单独证明。

Rust 特殊条目包括：self_cell 1.3.0（Apache-2.0 OR GPL-2.0-only）、r-efi 5.2.0（MIT OR Apache-2.0 OR LGPL-2.1-or-later）、notify 8.0.0（CC0-1.0）、ICU 系列（Unicode-3.0）、unicode-ident（宽松许可 AND Unicode）、target-lexicon（Apache-2.0 WITH LLVM-exception）、foldhash（Zlib）。这些不应被压成笼统 MIT。

运行时下载/安装供本地使用，与将库或成品镜像发给第三方不同。未来若改变分发边界，应处理上列具体缺口；当前源代码包不因这些未分发二进制的附件缺口被误写为“全部许可证未知”。

本报告是证据和义务摘要，不作法律、权属或商业使用保证。新写桥接器代码的许可证仍由发布者决定。
