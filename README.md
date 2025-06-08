# 企业微信转发到QQ群插件（astrbot_plugin_teheixy）

## 功能简介

本插件适用于 [AstrBot](https://github.com/AstrBotDevs/AstrBot)，可实现企业微信（gewechat）群消息自动转发到指定QQ群，支持多群对多群映射，支持文本、图片、表情等富媒体消息。

## 安装方法

1. 将本插件目录放入 AstrBot 的 `data/plugins/` 目录下。
2. 在 AstrBot 后台插件管理界面加载本插件。
3. 或通过 git 克隆：
   ```bash
   git clone https://github.com/teheiw192/astrbot_plugin_teheixy.git
   ```

## 配置方法

在 AstrBot 后台插件管理界面，配置 `group_mapping` 字段：
- 格式为 `{ "企业微信群ID": "QQ群ID", ... }`
- 例如：
  ```json
  {
    "group_mapping": {
      "wxid_group1": "123456789",
      "wxid_group2": "987654321"
    },
    "prefix": "[企业微信转发]"
  }
  ```
- `prefix` 字段可选，用于自定义转发消息前缀，默认为 `[企业微信转发]`。

## 使用说明

- 插件会自动监听所有企业微信群的消息，并转发到配置的QQ群。
- 支持文本、图片、表情等消息类型。
- 支持多群对多群独立映射，互不影响。
- 如需修改映射，直接在后台修改配置并重载插件即可生效。
- 插件日志会详细记录转发行为和异常，便于调试和排查。

## 常见问题

- **如何获取企业微信群ID？**
  - 可通过日志、调试或联系Bot管理员获取。
- **如何支持更多消息类型？**
  - 可参考 AstrBot 消息链相关API进行扩展。
- **如何反馈Bug或建议？**
  - 欢迎在本仓库提交 issue。

## 开源协议

MIT
