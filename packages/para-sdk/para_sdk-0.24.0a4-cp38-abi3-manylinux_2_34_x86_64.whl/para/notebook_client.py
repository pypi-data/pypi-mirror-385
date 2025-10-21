import os
import json
import base64
import builtins
from dataclasses import dataclass
from para import para;
from typing import Any, Optional
from typing import List
import boto3

if hasattr(builtins, "__IPYTHON__"):
  from .conversation_panel import ConversationPanel

if hasattr(builtins, "__IPYTHON__"):
  import panel as pn
  pn.extension()

class NotebookClient:
    _client: any

    def __init__(self, client: any):
        self._client = client

    def new_request(self, subject: str, action: str, target_actor_id=None, **kwargs):
        return self._client.pncp.skill_request(subject, action, target=target_actor_id, **kwargs)


async def from_env():
    paranet_endpoint = os.environ.get('PARANET_ENDPOINT')

    if not paranet_endpoint:
        raise ValueError("PARANET_ENDPOINT is not set")

    actor = os.environ.get('PARANET_ACTOR_ID')
    version = os.environ.get('PARANET_ACTOR_VERSION') or '1.0.0'

    if not actor:
        raise ValueError("PARANET_ACTOR is required")

    actor_entity_id = f'{actor}@{version}'

    paranet_access_token = os.environ.get('PARANET_ACTOR_ACCESS_TOKEN')
    paranet_refresh_token = os.environ.get('PARANET_ACTOR_REFRESH_TOKEN')

    paranet_jwt = os.environ.get('PARANET_ACTOR_JWT')
    paranet_password = os.environ.get('PARANET_ACTOR_PASSWORD')
    paranet_cognito_password = os.environ.get('PARANET_ACTOR_COGNITO_PASSWORD')


    print(f"Paranet endpoint: {paranet_endpoint}")
    endpoint = para.web_endpoint(paranet_endpoint)
    
    if paranet_access_token and paranet_refresh_token:
        client = await endpoint.paranode(actor, access_token=paranet_access_token, refresh_token=paranet_refresh_token)
    elif paranet_password:
        client = await endpoint.paranode(actor, password=paranet_password)
    elif paranet_cognito_password:
        client = await endpoint.paranode(actor, cognito_password=paranet_cognito_password)
    elif paranet_jwt:
        client = await endpoint.paranode(actor, jwt=paranet_jwt)
    else:
        raise ValueError("No login method provided")

    print(f"Logged into {paranet_endpoint} as {actor_entity_id}")

    return client


def existing_users(paranode):
    actors = paranode.list_base_actors()
    existing = set()
    for actor in actors:
        if (actor['kind'] == "user"):
            existing.add(actor['id'])
    return existing

def cognito_add(paranode, cognito_pool_id='us-west-2_N7wvmRxN6', group_name='Playgrounds'):
    region = "us-west-2"

    existing = existing_users(paranode)
    print("Existing users", existing)
    
    client = boto3.client('cognito-idp', region_name=region)
    paginator = client.get_paginator("list_users_in_group")

    for page in paginator.paginate(UserPoolId=cognito_pool_id, GroupName=group_name):
        for user in page['Users']:
            username = user['Username']
            if username not in existing:
                print(f"Cognito user {username} added")
                paranode.paranode_new_user(username, cognito_id=username)
            else:
                print(f"Cognito user {username} skipped")


async def connect_to(parent, name: Optional[str] = None, password: Optional[str] = "fun", **kwargs: Any):
    namespace = parent
    node_name = parent
    endpoint = f"https://{namespace}.paranet.otonoma.com"
    parent_namespace = None
    if name:
        node_name = name
        namespace = f"{namespace}--{name}"
        endpoint = f"https://{name}.{parent}.paranet.otonoma.com"
        parent_namespace = parent

    env = para.env_version()
    print("Environment versions", env)
    
    kwargs.setdefault("platform_channel", env.platform_channel)
    kwargs.setdefault("platform_version", env.platform_version)
    kwargs.setdefault("paranet_version", env.paranet_version)
    kwargs.setdefault("paraflow_version", env.paraflow_version)
    kwargs.setdefault("paralogue_version", env.paralogue_version)
    kwargs.setdefault("python_sdk_version", env.python_sdk_version)
    kwargs.setdefault("paracord_version", env.paracord_version)

        
    # Defines a new node to create
    node = await para.create_kube(
        node_name,
        namespace=namespace,
        parent_namespace=parent_namespace,
        endpoint=endpoint,
        
        cognito_client_id="4b52p19cfsaeobagem34vfe2u9",
        cognito_pool_id="us-west-2_N7wvmRxN6",
        cognito_redirect=f"https://{parent}.paranet.otonoma.com/auth/cognito/",

        root_password=password,
        await_for=None,

        **kwargs,
    )

    deployer = await node.deployer("root", password=password, await_for=None)
    
    return deployer