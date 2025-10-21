from typing import Any, Dict, Optional, Union

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from mcp_server_aliyun_observability.config import Config
from mcp_server_aliyun_observability.core.utils import call_data_query
from mcp_server_aliyun_observability.utils import handle_tea_exception


class AgentToolkit:
    """Agent Toolkit - AI驱动的智能可观测性洞察

    提供单一智能洞察工具：
    - agent_insight: 基于自然语言的全能可观测性分析

    AI会根据问题内容自动选择最合适的数据源（日志、指标、链路、事件、拓扑等）
    进行综合分析，用户无需预判数据类型。
    """

    def __init__(self, server: FastMCP):
        self.server = server
        self._register_tools()

    def _register_tools(self):
        """Register the unified Agent insight tool"""

        @self.server.tool()
        @retry(
            stop=stop_after_attempt(Config.get_retry_attempts()),
            wait=wait_fixed(Config.RETRY_WAIT_SECONDS),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        @handle_tea_exception
        def agent_insight(
            ctx: Context,
            query: str = Field(
                ...,
                description="自然语言问题，AI会自动分析并选择最合适的数据源进行回答",
            ),
            workspace: str = Field(..., description="CMS工作空间ID"),
            region_id: str = Field(..., description="阿里云地域ID，如cn-hangzhou"),
            entity_domain: str = Field(..., description="实体域，如apm、arms、k8s等"),
            entity_set_name: str = Field(
                ..., description="域内类型，如apm.service、arms.application等"
            ),
            entity_id: Optional[str] = Field(
                None, description="可选的特定实体ID，不指定则分析该类型下所有实体"
            ),
            from_time: Union[str, int] = Field(
                "now-15m", description="查询开始时间，支持相对时间(now-15m)或时间戳"
            ),
            to_time: Union[str, int] = Field(
                "now", description="查询结束时间，支持相对时间(now)或时间戳"
            ),
        ) -> Dict[str, Any]:
            """🤖 Agent智能洞察：基于自然语言的全能可观测性分析

            ## 核心能力

            AI会根据您的问题自动选择最合适的可观测性数据源进行综合分析：
            - 📊 **时序指标**：性能指标、资源使用率、业务指标等
            - 📝 **日志数据**：应用日志、错误日志、访问日志等
            - 🔗 **链路追踪**：分布式调用链、span分析、性能瓶颈等
            - 🚨 **告警事件**：告警记录、事件关联、影响分析等
            - 🏗️ **拓扑关系**：服务依赖、架构分析、影响范围等
            - 📈 **性能剖析**：CPU热点、内存分析、性能优化等
            - 🎯 **实体信息**：服务发现、状态查询、配置信息等

            ## 使用场景

            ### 🐛 故障排查
            - "payment-service最近有什么错误？错误原因是什么？"
            - "为什么订单接口失败率这么高？"
            - "刚才的告警是什么问题？影响范围多大？"

            ### ⚡ 性能分析
            - "为什么用户登录这么慢？瓶颈在哪里？"
            - "哪个服务的CPU使用率最高？"
            - "调用链中哪个环节最耗时？"

            ### 🔍 健康监控
            - "这个服务现在运行状况怎么样？"
            - "系统整体健康度如何？有什么异常？"
            - "最近的性能趋势是什么？"

            ### 🌐 架构洞察
            - "这个服务依赖哪些其他服务？"
            - "如果这个服务故障，会影响哪些业务？"
            - "系统调用关系复杂度如何？"

            ## 智能特性

            1. **自动数据源选择**：AI根据问题语义自动选择最相关的数据源
            2. **跨模态综合分析**：同时分析多种数据源，提供全面洞察
            3. **上下文感知**：理解实体范围和时间约束，避免结果发散
            4. **自然语言交互**：用人类语言提问，无需学习技术术语

            ## 使用限制

            - **实体范围限定**：查询范围限定在指定的entity_domain和entity_set_name内
            - **时间范围建议**：根据问题类型，建议不同的时间窗口
              - 实体状态查询：24小时内
              - 性能指标分析：7天内
              - 日志错误分析：1小时内
              - 链路追踪分析：1小时内
              - 告警事件分析：24小时内
            - **数据量控制**：AI会自动控制查询数据量，避免系统过载

            ## 参数说明

            - **query**: 用自然语言描述问题，AI会理解并分析
            - **workspace**: CMS工作空间ID，指定数据范围
            - **region_id**: 阿里云区域，如cn-hangzhou、cn-shanghai等
            - **entity_domain**: 限定实体域范围，如apm、arms、k8s等
            - **entity_set_name**: 限定实体类型，如apm.service、host.instance等
            - **entity_id**: 可选，指定特定实体，不填则分析该类型所有实体
            - **from_time/to_time**: 分析时间范围，支持相对时间表达式

            Args:
                ctx: MCP上下文
                query: 自然语言问题（必填）
                workspace: CMS工作空间ID（必填）
                region_id: 阿里云地域ID（必填）
                entity_domain: 实体域（必填）
                entity_set_name: 域内类型（必填）
                entity_id: 可选的特定实体ID
                from_time: 查询开始时间
                to_time: 查询结束时间

            Returns:
                包含AI智能分析结果的字典，包括：
                - insight: 主要洞察结果
                - data_sources_used: AI使用的数据源列表
                - analysis_summary: 分析摘要
                - recommendations: 建议和后续行动
            """
            try:
                # 构建完整的AI查询上下文
                ai_query = self._build_ai_query(
                    query=query,
                    entity_domain=entity_domain,
                    entity_set_name=entity_set_name,
                    entity_id=entity_id,
                    from_time=from_time,
                    to_time=to_time,
                )

                # 调用AI分析接口
                result = call_data_query(
                    ctx=ctx,
                    query=ai_query,
                    region_id=region_id,
                    workspace=workspace,
                    domain=entity_domain,
                    entity_type=entity_set_name,
                    entity_id=entity_id,
                    start_time=from_time,
                    end_time=to_time,
                    error_message_prefix="Agent智能洞察分析失败",
                )

                # 包装返回结果
                return {
                    "success": True,
                    "insight_type": "comprehensive",
                    "query": query,
                    "result": result,
                    "entity_context": {
                        "domain": entity_domain,
                        "type": entity_set_name,
                        "id": entity_id,
                    },
                    "time_range": {"from": from_time, "to": to_time},
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "query": query,
                    "entity_context": {
                        "domain": entity_domain,
                        "type": entity_set_name,
                        "id": entity_id,
                    },
                }

    def _build_ai_query(
        self,
        query: str,
        entity_domain: str,
        entity_set_name: str,
        entity_id: Optional[str],
        from_time: Union[str, int],
        to_time: Union[str, int],
    ) -> str:
        """构建传递给AI的完整查询上下文

        Args:
            query: 用户原始问题
            entity_domain: 实体域
            entity_set_name: 域内类型
            entity_id: 可选的特定实体ID
            from_time: 开始时间
            to_time: 结束时间

        Returns:
            完整的AI查询字符串
        """
        query_parts = [
            f"用户问题：{query}",
            "",
            "分析上下文：",
            f"- 实体域：{entity_domain}",
            f"- 实体类型：{entity_set_name}",
            f"- 目标实体：{entity_id if entity_id else '该类型下所有实体'}",
            f"- 时间范围：{from_time} 到 {to_time}",
            "",
        ]

        return "\n".join(query_parts)


def register_agent_tools(server: FastMCP):
    """Register Agent toolkit tools with the FastMCP server

    Args:
        server: FastMCP server instance
    """
    AgentToolkit(server)
