"""
企业微信转发到QQ群插件（支持多群对多群映射，支持图片/表情等富媒体消息转发）

【event: AstrMessageEvent 常用用法】
- event.message_str         # 获取消息的纯文本内容
- event.get_group_id()      # 获取群ID（如企业微信群/QQ群号）
- event.get_platform_name() # 获取消息来源平台（如 'gewechat'、'aiocqhttp'）
- event.get_sender_id()     # 获取发送者ID
- event.get_sender_name()   # 获取发送者昵称
- event.is_admin()          # 判断是否为管理员
- event.is_private_chat()   # 判断是否为私聊
- event.stop_event()        # 终止事件传播
- event.plain_result(text)  # 生成文本消息结果（用于 yield）
- event.chain_result(chain) # 生成消息链结果（用于 yield）
- await event.send(chain)   # 主动发送消息（推荐用于异步函数）
- 更多详见 AstrBot 官方文档

【context: Context 常用用法】
- context.get_platform(PlatformAdapterType.AIOCQHTTP)  # 获取 QQ 平台适配器
- context.get_platform(PlatformAdapterType.GEWECHAT)   # 获取企业微信平台适配器
- context.send_message(session, message_chain)         # 主动发送消息到指定会话
- context.get_config()                                 # 获取全局配置
- context.get_all_stars()                              # 获取所有已注册插件
- 更多详见 AstrBot 官方文档

【操作指南】
1. 在 AstrBot 后台插件管理界面，配置 group_mapping 字段：
   - 格式为 {"企业微信群ID": "QQ群ID", ...}
   - 例如：{"wxid_group1": "123456789", "wxid_group2": "987654321"}
   - 企业微信群ID可通过日志或调试获取，QQ群ID为纯数字。
2. 可选配置 prefix 字段，设置转发消息前缀，默认为"[企业微信转发]"。
3. 插件会自动监听所有企业微信群的消息，并转发到配置的QQ群。
4. 如需修改映射，直接在后台修改配置并重载插件即可生效。
5. 未配置映射的企业微信群消息不会被转发。
6. 插件日志会详细记录转发行为和异常，便于调试和排查。
7. 支持多群对多群独立映射，互不影响。
8. 支持图片、表情等富媒体消息转发。

【行为说明】
- 仅转发企业微信群（gewechat平台）的群消息到对应QQ群。
- 支持多个群的独立映射，互不影响。
- 转发内容为消息链（文本、图片、表情等）。
- 日志会详细记录转发行为和异常。

"""
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, EventMessageType
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.platform import PlatformAdapterType
from astrbot.api import AstrBotConfig

@register("wework2qq", "YourName", "企业微信转发到QQ群（多群对多群可配置）", "1.2.0", "https://github.com/YourName/wework2qq")
class Wework2QQPlugin(Star):
    """
    企业微信转发到QQ群插件主类。
    支持在后台配置多个企业微信群与QQ群的映射，实现多群对多群自动转发。
    支持图片、表情等富媒体消息转发。
    """
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config or {}
        # group_mapping: {企业微信群ID: QQ群ID}
        self.group_mapping = self.config.get("group_mapping", {})
        # prefix: 转发消息前缀
        self.prefix = self.config.get("prefix", "[企业微信转发]")

    async def initialize(self):
        """
        插件初始化时自动调用。
        重新加载配置中的群映射关系和前缀。
        """
        self.group_mapping = self.config.get("group_mapping", {})
        self.prefix = self.config.get("prefix", "[企业微信转发]")
        logger.info(f"[Wework2QQ] 当前群映射配置: {self.group_mapping}, 前缀: {self.prefix}")

    @filter.event_message_type(EventMessageType.GROUP_MESSAGE)
    async def on_wework_message(self, event: AstrMessageEvent):
        """
        监听所有群消息。
        event: AstrMessageEvent，包含消息内容、来源、发送者等所有上下文信息。
        如果消息来自企业微信（gewechat），且配置了映射，则自动转发到对应QQ群。
        常用属性和方法见文件头注释。
        支持文本、图片、表情等消息类型。
        """
        if event.get_platform_name() == "gewechat":
            wework_group_id = event.get_group_id()  # 企业微信群ID
            qq_group_id = self.group_mapping.get(wework_group_id)
            if not qq_group_id:
                logger.info(f"[Wework2QQ] 未配置企业微信群 {wework_group_id} 的映射，消息不转发。")
                return
            qq_platform = self.context.get_platform(PlatformAdapterType.AIOCQHTTP)
            if not qq_platform:
                logger.warning("[Wework2QQ] 未找到QQ平台适配器，无法转发消息。")
                return
            try:
                # 获取原始消息链，支持富媒体
                chain = event.get_messages()
                if not chain:
                    logger.info(f"[Wework2QQ] 企业微信群({wework_group_id})收到空消息，不转发。")
                    return
                # 在消息链前加上前缀
                from astrbot.api.message_components import Plain
                chain = [Plain(self.prefix)] + chain
                await qq_platform.send_message(qq_group_id, chain)
                logger.info(f"[Wework2QQ] 已将企业微信({wework_group_id})消息转发到QQ群({qq_group_id})。消息链: {chain}")
            except Exception as e:
                logger.error(f"[Wework2QQ] 转发消息时发生异常: {e}")

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """
        示例指令：/helloworld
        用于测试插件是否正常加载。
        """
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")

    async def terminate(self):
        """
        插件卸载/停用时自动调用。
        可用于资源清理。
        """
