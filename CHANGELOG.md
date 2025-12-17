# Changelog

遵循 Keep a Changelog 与语义化版本（SemVer）。本日志记录“仅后端图片生成核心”阶段的改动。

## [0.1.0] - 2025-12-16

### 新增
- 核心图片合成模块：
  - `src/core/image_generator.rs`：主合成入口 `generate_image`（`src/core/image_generator.rs:28`），支持加载背景、居中缩放叠加角色、绘制文本并保存 PNG。
  - `src/core/text_processor.rs`：文本处理工具，`wrap_text_to_width` 自动按像素宽度换行（`src/core/text_processor.rs:26`），`draw_multiline_text` 绘制多行文本并支持阴影（`src/core/text_processor.rs:74`）。
- 命令行接口：
  - `src/main.rs`：提供参数 `--background`、`--character`、`--font`、`--text`、`--font_size`、`--out`（入口定义于 `src/main.rs:10-26`），默认从 `assets` 自动选择可用资源。
- 自动资源选择：
  - 背景：默认取 `assets/background` 目录中的首个 PNG（`find_first_png` 在 `src/core/image_generator.rs:83`）。
  - 角色：默认深度遍历 `assets/chara/*` 子目录，选取首个 PNG（逻辑位于 `src/main.rs:37-50`）。
  - 字体：默认取 `assets/fonts` 目录中的首个 TTF（`find_first_ttf` 在 `src/core/image_generator.rs:92`）。
- 文本样式与绘制：
  - 支持 TrueType 字体、字体大小（默认 48）、文本颜色（默认白色）、左对齐与阴影（黑色半透明，偏移 2 像素）。
- 依赖新增：
  - `image`、`imageproc`、`rusttype`：图像处理与文本渲染
  - `clap`：命令行解析
  - `thiserror`：错误类型管理

### 变更
- 更新 `Cargo.toml` 添加上述依赖（`image = "0.24"`、`imageproc = "0.23"`、`rusttype = "0.9"`、`clap = "4.5"`、`thiserror = "1.0"`）。
- 新增 `src/core/mod.rs` 并引入 `image_generator`、`text_processor` 模块。
- `src/main.rs` 由占位输出替换为完整 CLI 流程：解析参数、选择资源、调用合成、输出路径（`src/main.rs:28-77`）。

### 已验证
- 本地构建：`cargo build` 通过。
- 运行示例：`cargo run` 生成 `output.png`，默认示例文本为“魔女裁判・文本生成器（Rust）”。

### 已知问题
- 若干编译警告（`unused_imports` / `unused_mut`），不影响功能，后续将清理。
- 当前阶段仅实现后端合成核心：
  - 未包含 GUI、AI 情感匹配、剪贴板集成、快捷键、配置管理等功能（参见 `todo.md` 的后续阶段）。

### 用法示例
- 默认生成（自动选择首个背景、角色与字体）：  
  `cargo run`
- 指定文本与大小：  
  `cargo run -- --text "你好，魔女裁判风格！" --font_size 48 --out output.png`
- 指定资源路径（Windows 路径分隔符示例）：  
  `cargo run -- --background assets\\background\\c10.png --character assets\\chara\\yuki\\yuki (1).png --font assets\\fonts\\font3.ttf --text "..." --out output.png`

### 文件与路径
- 资源目录：`assets/background`、`assets/chara/*`、`assets/fonts`
- 输出文件：`output.png`（可由 `--out` 指定）

---

[0.1.0]: https://example.com/releases/0.1.0

## [0.1.1] - 2025-12-16

### 新增
- 百分比参数支持（以背景尺寸为基准）：
  - 角色叠加大小与位置：
    - `--char_width_pct` / `--char-width-pct`：角色目标宽度占背景宽度的百分比（0-100）
    - `--char_pos_pct` / `--char-pos-pct`：角色左上角位置（`x%,y%`）
  - 文本区与字体：
    - `--text_pos_pct` / `--text-pos-pct`：文本起始位置（`x%,y%`）
    - `--text_width_pct` / `--text-width-pct`：文本区域宽度占背景宽度的百分比（0-100）
    - `--font_size_pct` / `--font-size-pct`：字体大小占背景高度的百分比（0-100）

### 变更
- `src/core/image_generator.rs`：
  - `GenerationParams` 增加百分比字段（`overlay_width_pct`、`overlay_pos_pct`、`text_pos_pct`、`text_width_pct`、`font_size_pct`）
  - 合成逻辑根据百分比计算像素位置与尺寸（叠加时保持纵横比）
- `src/main.rs`：
  - CLI 解析支持下划线与短横线两种参数命名（Clap alias）
  - 增加 `parse_xy_pct` 将 `x,y` 字符串解析为 `f32` 元组

### 使用示例
- 指定角色与文本的百分比布局：
  - `cargo run -- --text "测试百分比参数" --char_width_pct 30 --char_pos_pct 60,20 --text_pos_pct 5,80 --text_width_pct 60 --font_size_pct 6 --out output_pct.png`

### 兼容性
- 未提供百分比参数时，保持原有默认行为（角色居中、宽度按背景最小维度 75% 缩放；文本默认在下部 1/4 处，字体大小按 `--font_size`）。

## [0.1.2] - 2025-12-16

### 新增
- 角色高度百分比：
  - `--char_height_pct` / `--char-height-pct`：角色目标高度占背景高度的百分比（0-100），保持纵横比缩放。

### 变更
- 缩放优先级：
  - 若同时提供宽度百分比与高度百分比，优先使用宽度百分比计算缩放；仅提供高度百分比时按高度缩放；均未提供时维持默认逻辑。

### 使用示例
- 高度百分比叠加：
  - `cargo run -- --text "高度百分比测试" --char_height_pct 40 --char_pos_pct 10,10 --out output_hpct.png`

## [0.1.3] - 2025-12-16

### 新增
- 压缩与格式：
  - `--compress`：启用 PNG 最佳压缩（CompressionType::Best + FilterType::Adaptive）。
  - `--format`：输出格式选择（`png` 或 `jpeg`）。默认根据 `--out` 扩展名推断，无法推断时使用 `png`。
  - `--quality`：JPEG 质量（1–100，默认 85）。

### 变更
- 保存逻辑：
  - 对 PNG 使用自定义编码器；对 JPEG 自动丢弃 alpha 并保存为 RGB。

### 使用示例
- 压缩 PNG：
  - `cargo run -- --text "压缩PNG测试" --compress --out output_png_best.png`
- 压缩 JPEG：
  - `cargo run -- --text "压缩JPEG测试" --format jpeg --quality 65 --out output_jpeg_65.jpg`
