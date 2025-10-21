from typing import Any, Dict, Optional
from alibabacloud_cms20240330.client import Client as CmsClient
from alibabacloud_cms20240330.models import (ListWorkspacesRequest,
                                             ListWorkspacesResponse,
                                             ListWorkspacesResponseBody)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from mcp_server_aliyun_observability.utils import handle_tea_exception, execute_cms_query_with_context


class SharedToolkit:
    """Shared Toolkit
    
    Provides common functionality used by both PaaS and DoAI layers, including:
    - Workspace management (list_workspace)
    - Entity discovery (list_domains)
    """

    def __init__(self, server: FastMCP):
        """Initialize the shared toolkit
        
        Args:
            server: FastMCP server instance
        """
        self.server = server
        self.register_tools()

    def register_tools(self):
        """Register all shared tools"""
        self._register_workspace_tools()
        self._register_discovery_tools()

    def _register_workspace_tools(self):
        """Register workspace management tools"""

        @self.server.tool()
        @retry(
            wait=wait_fixed(1),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        @handle_tea_exception
        def list_workspace(
            ctx: Context,
            regionId: str = Field(..., description="阿里云区域ID"),
        ) -> Dict[str, Any]:
            """列出可用的CMS工作空间
            
            ## 功能概述
            获取指定区域内可用的Cloud Monitor Service (CMS)工作空间列表。
            工作空间是CMS中用于组织和管理监控数据的逻辑容器。
            
            ## 参数说明
            - regionId: 阿里云区域标识符，如 "cn-hangzhou", "cn-beijing" 等
            
            ## 返回结果
            返回包含工作空间信息的字典，包括：
            - workspaces: 工作空间列表，每个工作空间包含名称、ID、描述等信息
            - total_count: 工作空间总数
            - region: 查询的区域ID
            
            ## 使用场景
            - 在使用PaaS层API之前，需要先获取可用的工作空间
            - 为DoAI层查询提供工作空间选择
            - 管理和监控多个工作空间的资源使用情况
            
            ## 注意事项
            - 不同区域的工作空间是独立的
            - 工作空间的可见性取决于当前用户的权限
            - 这是一个基础工具，为其他PaaS和DoAI工具提供工作空间选择
            """
            try:
                # 获取CMS客户端
                cms_client: CmsClient = ctx.request_context.lifespan_context.get("cms_client")
                if not cms_client:
                    return {
                        "error": True,
                        "workspaces": [],
                        "total_count": 0,
                        "region": regionId,
                        "message": "CMS客户端未初始化",
                    }
                
                cms_client = cms_client.with_region(regionId)
                
                # 构建请求 - 获取所有工作空间
                request = ListWorkspacesRequest(
                    max_results=100,
                    next_token=None,
                    region=regionId,
                    workspace_name=None  # 获取所有工作空间
                )
                
                # 调用CMS API
                response: ListWorkspacesResponse = cms_client.list_workspaces(request)
                body: ListWorkspacesResponseBody = response.body
                
                # 处理响应
                workspaces = []
                if body.workspaces:
                    workspaces = [w.to_map() for w in body.workspaces]
                
                return {
                    "error": False,
                    "workspaces": workspaces,
                    "total_count": body.total if body.total else len(workspaces),
                    "region": regionId,
                    "message": f"Successfully retrieved {len(workspaces)} workspaces from region {regionId}"
                }
                
            except Exception as e:
                return {
                    "error": True,
                    "workspaces": [],
                    "total_count": 0,
                    "region": regionId,
                    "message": f"Failed to retrieve workspaces: {str(e)}"
                }

    def _register_discovery_tools(self):
        """Register discovery tools"""

        @self.server.tool()
        @retry(
            wait=wait_fixed(1),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        @handle_tea_exception
        def list_domains(
            ctx: Context,
            workspace: str = Field(..., description="CMS工作空间名称，可通过list_workspace获取"),
            regionId: str = Field(..., description="阿里云区域ID"),
        ) -> Dict[str, Any]:
            """列出所有可用的实体域
            
            ## 功能概述
            获取系统中所有可用的实体域（domain）列表。实体域是实体的最高级分类，
            如 APM、容器、云产品等。这是发现系统支持实体类型的第一步。
            
            ## 使用场景
            - 了解系统支持的所有实体域
            - 为后续查询选择正确的domain参数
            - 构建动态的域选择界面
            
            ## 返回数据
            每个域包含：
            - __domain__: 域名称（如 apm, k8s, cloud）  
            - cnt: 该域下的实体总数量
            
            Args:
                ctx: MCP上下文
                workspace: CMS工作空间名称
                regionId: 阿里云区域ID
                
            Returns:
                包含实体域列表的响应对象
            """
            # 使用.entity查询来获取所有域的统计信息
            query = ".entity with(domain='*', type='*', topk=1000) | stats cnt=count(1) by __domain__ | project __domain__, cnt | sort cnt desc"
            return execute_cms_query_with_context(ctx, query, workspace, regionId, "now-24h", "now", 1000)


def register_shared_tools(server: FastMCP):
    """Register shared toolkit tools with the FastMCP server
    
    Args:
        server: FastMCP server instance
    """
    SharedToolkit(server)