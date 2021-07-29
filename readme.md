# nonebot_plugin_bugku

## 简介

基于[nonebot2](https://github.com/nonebot/nonebot2)的bot插件，用于检测Bugku的AWD公开房间，练手项目，~~其实并没有什么卵用~~

功能：

- [x] 定时检测并通知
- [x] 即时检测
- [x] Bot所有者自动签到
- [ ] 多用户自动签到

## 使用方法

### 初始配置

在`.env`文件中添加如下配置

```
bugku_username=bugku的账号
bugku_password=bugku的密码
bugku_own=机器人拥有者的扣扣号
```

在`bot.py`目录的父目录(上一级)建立`res`文件夹(不存在会自动创建)，用于存放`captcha.png`、`cookies`、`userinfo`，可按需求自行更改

### 命令

- `/init `

  用于bot重启后，将保存到本地的配置文件加载到config

- `/start`

  将当前QQ号/群号加入定时检测通知列表

- `/bugku`

  用于即时检测

### 使用

开始`/init`一下，然后`/start`一下，想看看有没有房间就`/bugku`一下，如果cookie失效了会尝试重新登录并发送登录所需的验证码图片，发送`四个字符`的验证码(不用带`/`)即可。

## 鸣谢

感谢如此美妙的bot框架[nonebot2](https://github.com/nonebot/nonebot2)

感谢耐心解答问题的开发者群群友

感谢商店里插件提供精妙的案例让我有的~~抄~~借鉴

