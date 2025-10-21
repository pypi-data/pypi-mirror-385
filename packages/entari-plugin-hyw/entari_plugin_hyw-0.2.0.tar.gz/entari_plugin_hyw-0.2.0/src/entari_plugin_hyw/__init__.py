from typing import List, Text, Union
from arclet.entari import metadata
from arclet.entari import MessageChain, Session
from arclet.entari.event.base import MessageEvent
from satori.exception import ActionFailed
from arclet.entari import MessageChain, At, Image, Quote, Text
import arclet.letoderea as leto
from arclet.entari import MessageCreatedEvent, Session
from arclet.entari import BasicConfModel, metadata, plugin_config
from loguru import logger
import asyncio

# 导入AI服务模块
from .agent import  AgentService, HywConfig


metadata(
    name="hyw",
    author=[{"name": "kumoSleeping", "email": "zjr2992@outlook.com"}],
    version="0.1.0",
    description="",
    config=HywConfig,
)

conf = plugin_config(HywConfig)

agent_service = AgentService(conf)
    
@leto.on(MessageCreatedEvent)
async def on_message_created(message_chain: MessageChain, session: Session[MessageEvent]):
    command_name_list = [conf.hyw_command_name] if isinstance(conf.hyw_command_name, str) else conf.hyw_command_name
    if not any(message_chain.get(Text).strip().startswith(cmd) for cmd in command_name_list):
        return
    message_chain = message_chain.exclude(At) if message_chain.get(At) else message_chain
    for command_name in command_name_list:
        message_chain = message_chain.strip().removeprefix(command_name).strip()
    
    if str(message_chain) == "" and (str(session.reply.origin.message) == "" if session.reply else True):
        return
    
    async def react(code: str):
        try:
            await session.account.protocol.call_api("internal/set_group_reaction", {
                "group_id": int(session.guild.id),
                "message_id": int(session.event.message.id),
                "code": code,
                "is_add": True
            })
        except ActionFailed:
            # 忽略反应失败的错误
            pass
            
    try:
        if session.reply:
            try:
                # 将引用消息内容添加到当前content中 反正最后会只取出 Text 和 Image
                message_chain.extend(session.reply.origin.message)
            except Exception:
                # 引用消息获取失败时忽略，继续处理原消息
                pass
        # 文本消息(全部)
        msg = message_chain.get(Text).strip()
        
        images = None
        if message_chain.get(Image):
            # 下载图片
            urls = message_chain[Image].map(lambda x: x.src)
            tasks = [agent_service.download_image(url) for url in urls]
            images = await asyncio.gather(*tasks)
        
        # 使用统一入口，传递react函数让AI服务内部处理反应
        res = await agent_service.unified_completion(str(msg), images, react)
        await react("128051")  # 🐳
        logger.info(f"hyw unified response: {res}")
        
        # 安全检查：处理空回复或被审查的情况
        response_content = str(res.content) if hasattr(res, 'content') else ""
        if not response_content.strip():
            # 检查是否有工具调用但没有内容
            if hasattr(res, 'tool_calls') and res.tool_calls:
                response_content = "[KEY] :: 信息处理 | 内容获取\n>> [search enable]\n抱歉，获取到的内容可能包含敏感信息，暂时无法显示完整结果。\n[LLM] :: 安全过滤"
                raise ValueError("内容被安全过滤，无法显示完整结果。")
            else:
                response_content = "[KEY] :: 系统响应 | 处理异常\n>> [search enable]\n抱歉，暂时无法生成回复内容。\n[LLM] :: 系统提示"
                raise ValueError("内容被安全过滤，无法显示完整结果。")
        
        await session.send(response_content)
    except Exception as e:
        await react("10060")  # ❌
        raise e
