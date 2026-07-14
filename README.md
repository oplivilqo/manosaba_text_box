# 🎭魔法少女的魔女裁判 文本框生成器

一个基于Python的自动化表情包生成工具，能够快速生成带有自定义文本的魔法少女的魔女裁判文本框图片。[灵感来源与代码参考](https://github.com/MarkCup-Official/Anan-s-Sketchbook-Chat-Box)

## 预览
<img width="500" alt="预览 1" src="https://github.com/user-attachments/assets/6fb46a8d-4fc4-4d10-80a0-ed21fbb428bf" />&nbsp;<img width="500" alt="预览 2" src="https://github.com/user-attachments/assets/847c331e-9274-4b60-9b42-af0a80265391" />
<img width="500" alt="高级预览 1" src="https://github.com/user-attachments/assets/86af2653-99d9-4ed3-99a6-f21380102b93" />&nbsp;<img width="500" alt="高级预览 2" src="https://github.com/user-attachments/assets/0643f205-6fa6-456f-96c6-2fdafda6152e" />

## 分支指引
由于本项目正在蒸蒸日上（喜，有很多老师都为本项目提交了自己的贡献，但全都挤进主分支有点百家争鸣了（悲

因此本项目当前使用分支管理各位老师独具匠心的思路，下面提供各分支的预览与指北，可以根据自己的喜好选择合适的分支：

1. **GUI 用户界面**: 当前的主分支 👈您在这里
   <details>
      <summary>GUI界面预览</summary>
   <img src="https://github.com/user-attachments/assets/6cd00359-3ace-4c2c-b19e-12bdd70381fe" alt="GUI界面截图" />
   </details>
   
   - 简单易用的用户界面，同时带有预览。适合大多数用户。
   
2. **[textual TUI](https://github.com/oplivilqo/manosaba_text_box/tree/refresh)**: `refresh`分支
   <details>
      <summary>TUI界面预览</summary>
      <img src="https://github.com/user-attachments/assets/5d1219c4-582f-4573-a605-065d6abc5337" alt="TUI界面截图">
   </details>
   
   - 直接在运行终端展示的用户界面，适合少数喜欢终端UI的用户。但暂时无法实现图片预览。

3. **[JavaScript WebUI](https://github.com/oplivilqo/manosaba_text_box/tree/lite)**: `lite`分支
   <details>
      <summary>JS版界面预览</summary>
      <img src="https://github.com/user-attachments/assets/38d0e142-8707-4f43-b1a8-1bb0bcdbe848" alt="JS版界面截图">
   </details>
   
   - 无需`Python`环境，使用浏览器实现的版本。适合偶尔生成图片的用户。
  
4. **[Rust 内核🦀](https://github.com/oplivilqo/manosaba_text_box/tree/rust)**: `rust`分支
   - 使用`Rust`重写了内核逻辑来提升性能。
   
5. **[LEGACY 古早版本](https://github.com/oplivilqo/manosaba_text_box/tree/legacy)**: `legacy`分支
   - 纯命令行界面，监听全局快捷键的古早版本，「但是没bug」。

6. **其他 tkinter GUI** (现在还没合并但未来可期)
   - 其他使用tkinter实现的GUI用户界面
   - 目前还有两位老师正在爆肝：
      1. @morpheus315 _[PR #32](https://github.com/oplivilqo/manosaba_text_box/pull/32)_: [仓库地址](https://github.com/morpheus315/Text_box-of-mahoushoujo_no_majosaiban-NEO) (已发布Release)
      2. @thgg678 _[PR #23](https://github.com/oplivilqo/manosaba_text_box/pull/23)_: [仓库地址](https://github.com/thgg678/Text_box-of-mahoushoujo_no_majosaiban)


## 使用方法与配置教程
参阅[项目Wiki页面](https://github.com/oplivilqo/manosaba_text_box/wiki/GUI-%E5%88%86%E6%94%AF-(%E7%94%A8%E6%88%B7%E7%95%8C%E9%9D%A2))

## GUI 介绍
### 功能特色
- 🎨 内置角色 - 内置14个角色，每个角色多个表情差分
- ⚡ 图形界面 - 使用Tkinter实现简单易用的用户界面
- 🖼️ 智能合成 - 自动合成背景与角色图片
- 📝 文本嵌入 - 自动在表情图片上添加文本
- 🀄 智能匹配 - 通过AI分析文本内容匹配情感，选择符合情感的表情
- 🔄 实时预览 - 即使随机也能预览合成效果
- 🔍 实时生成 - 图片缓存在内存中，不占硬盘空间
- 🔧 高度定制 - 支持自定义角色导入，可配置角色差分和背景是否随机等

### 界面预览
<details>
   <summary>GUI 用户界面</summary>
<img width="600" alt="GUI主界面" src="https://github.com/user-attachments/assets/6cd00359-3ace-4c2c-b19e-12bdd70381fe" />
</details>

<details>
   <summary>GUI 设置界面</summary>
<img width="600" alt="GUI设置界面" src="https://github.com/user-attachments/assets/26643f73-de43-4609-9792-44c0711e949c" />
</details>

<details>
   <summary>GUI 样式编辑界面</summary>
<img width="600" alt="GUI样式编辑界面" src="https://github.com/user-attachments/assets/c42bd862-e533-41f2-ab4d-7800e1c4cb70" />
</details>

## 使用方法与配置教程
参阅[项目Wiki页面](https://github.com/oplivilqo/manosaba_text_box/wiki/GUI-%E5%88%86%E6%94%AF-(%E7%94%A8%E6%88%B7%E7%95%8C%E9%9D%A2))

## 许可证
本项目基于MIT协议传播，仅供个人学习交流使用，不拥有相关素材的版权。进行分发时应注意不违反素材版权与官方二次创造协定。

背景、立绘等图片素材 © Re,AER LLC./Acacia

表情符号图形（PNG格式）来源于 [Noto Emoji](https://github.com/googlefonts/noto-emoji) 项目，遵循 [SIL Open Font License 1.1](licenses/OFL.txt) 许可

SDL，SDL_image，SDL_ttf，cJSON 等库遵循的协议见 [NOTICE.txt](licenses/NOTICE.txt) 中的说明

## 结语
受B站上MarkCup做的夏目安安传话筒启发，以夏目安安传话筒为源代码编写了这样一个文本框脚本。
由于本人是初学者，第一次尝试写这种代码，有许多地方尚有改进的余地，望多多包含。


<div align="right">
  
### _以上. 柊回文_



