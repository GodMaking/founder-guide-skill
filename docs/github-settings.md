# GitHub 仓库设置建议

仓库 slug 保持 `founder-guide-skill` 不变（已与作者确认），以下只优化展示文案与设置。

## About

**Description（建议直接粘贴，约 120 字符）**

```text
把“这个方向该不该做”变成数字和动作的 AI 创业决策 Skill：五问事实、四道闸门、一张决策卡。个人非商业免费，商业使用需授权。
```

**Website**

```text
https://github.com/GodMaking/founder-guide-skill#readme
```

如果没有独立主页，先留空或填 README 锚点，不要填不存在的购买链接。

## Topics

```text
agent-skill
ai-agent
claude-code
codex
cursor
startup
founder
entrepreneurship
decision-making
business-analysis
chinese
polyform-noncommercial
```

## Social preview

建议做一张 1280×640 的图，包含：

- 主标题：Founder Guide（创业者指南）
- 副标题：把“该不该做”变成数字和动作
- 三个关键词：五问事实 / 四道闸门 / 决策卡
- 角标：个人非商业免费 · 商业使用需授权
- 仓库地址：github.com/GodMaking/founder-guide-skill

不要使用“付费解锁”“独家源码”“稳赚”等误导性文案。

## Pinned Issue / Discussion

建议置顶一条 Issue，标题：

```text
商业授权申请与正版核验说明（先看这里）
```

正文包含：

- 免费非商业使用范围
- 个人商业使用授权范围
- 团队/企业商业使用另签
- 禁止倒卖
- 申请入口
- 核验入口
- 不要在公开 Issue 填写敏感信息

## Releases

每个重要版本建议：

1. 打 tag：`v1.2.0`
2. 创建 Release，粘贴 `CHANGELOG.md` 对应段落
3. 附上源码 zip 的 SHA-256
4. 在 Release 说明中写明许可与商业授权入口

## 仓库检查清单

- [ ] About 描述已更新
- [ ] Topics 已添加
- [ ] Social preview 已上传
- [ ] LICENSE 在 GitHub 右侧显示为 PolyForm Noncommercial 1.0.0
- [ ] README 顶部有“授权速览”
- [ ] Issue 模板可用：商业授权申请、授权核验、侵权举报
- [ ] 置顶 Issue 已发布
- [ ] 首个 Release 已创建
- [ ] 没有把 `licenses/`、`license-ledger.csv`、买家信息提交到仓库
