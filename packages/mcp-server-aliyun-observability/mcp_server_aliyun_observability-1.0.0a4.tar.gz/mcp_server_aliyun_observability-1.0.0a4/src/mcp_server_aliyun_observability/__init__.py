import os
import sys

import click
import dotenv

from mcp_server_aliyun_observability.server import server
from mcp_server_aliyun_observability.utils import CredentialWrapper

dotenv.load_dotenv()


@click.command()
@click.option(
    "--access-key-id",
    type=str,
    help="aliyun access key id",
    required=False,
)
@click.option(
    "--access-key-secret",
    type=str,
    help="aliyun access key secret",
    required=False,
)
@click.option(
    "--knowledge-config",
    type=str,
    help="knowledge config file path",
    required=False,
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    help="transport type: stdio or sse (streamableHttp coming soon)",
    default="streamable-http",
)
@click.option("--host", type=str, help="host", default="127.0.0.1")
@click.option("--log-level", type=str, help="log level", default="INFO")
@click.option("--transport-port", type=int, help="transport port", default=8080)
@click.option(
    "--scope",
    type=click.Choice(["paas", "iaas", "agent", "all"]),
    help="工具范围: paas(平台API), iaas(基础设施), agent(AI增强), all(全部)",
    default="all",
)
def main(access_key_id, access_key_secret, knowledge_config, transport, log_level, transport_port, host, scope):
    if access_key_id and access_key_secret:
        credential = CredentialWrapper(
            access_key_id, access_key_secret, knowledge_config
        )
    else:
        credential = None
    # 设置环境变量，传递给服务器
    if scope and scope != "all":
        os.environ['MCP_TOOLKIT_SCOPE'] = scope
    
    server(credential, transport, log_level, transport_port, host)
