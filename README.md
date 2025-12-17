# text-to-picture_backend

Rust 版「文本框生成器」后端核心：合成背景、角色与文本，支持参数化布局与压缩输出。

## 构建与运行
- 构建：`cargo build`
- 基础运行：`cargo run`

## 参数说明
- `--background PATH`：背景图片路径（PNG）。默认取 `assets/background` 下第一个 PNG。
- `--character PATH`：角色图片路径（PNG）。默认深度遍历 `assets/chara/*` 子目录，取第一个 PNG。
- `--font PATH`：字体文件（TTF）。默认取 `assets/fonts` 下第一个 TTF。
- `--text TEXT`：绘制文本内容。默认示例文本。
- `--font_size NUMBER`：字体大小（像素）。默认 `48.0`。若提供 `--font_size_pct` 则被覆盖。
- `--font_size_pct PERCENT` / `--font-size-pct PERCENT`：字体大小占背景高度的百分比（0–100）。
- `--text_pos_pct X,Y` / `--text-pos-pct X,Y`：文本起始位置，单位为背景的百分比坐标。
- `--text_width_pct PERCENT` / `--text-width-pct PERCENT`：文本区域宽度占背景宽度的百分比（0–100）。
- `--char_width_pct PERCENT` / `--char-width-pct PERCENT`：角色宽度占背景宽度的百分比（0–100）。
- `--char_height_pct PERCENT` / `--char-height-pct PERCENT`：角色高度占背景高度的百分比（0–100）。
- `--char_pos_pct X,Y` / `--char-pos-pct X,Y`：角色左上角位置（百分比坐标）。
- `--out PATH`：输出图片路径。默认 `output.png`。
- `--compress`：启用 PNG 最佳压缩（尽可能减小文件大小）。
- `--format FORMAT`：输出格式，可选 `png` 或 `jpeg`。默认根据 `--out` 扩展名推断，无法推断时使用 `png`。
- `--quality NUMBER`：JPEG质量（1–100），默认 `85`。仅当 `--format jpeg` 时生效。

## 缩放与优先级
- 角色尺寸：
  - 若提供 `--char_width_pct` 与 `--char_height_pct`，优先使用 `--char_width_pct`；
  - 仅提供其一则按该维度缩放（保持纵横比）；
  - 均未提供时，默认将角色缩放到背景最小维度的 75% 并居中。
- 文本布局：
  - 未提供百分比相关参数时，文本默认位于下部 1/4 区域，宽度为左右各 24 像素边距后的区域。

## 示例
- 默认运行（自动选择资源）：
  - `cargo run`
- 指定文本与大小：
  - `cargo run -- --text "你好，魔女裁判风格！" --font_size 48 --out output.png`
- 百分比布局（角色与文本）：
  - `cargo run -- --text "测试百分比参数" --char_width_pct 30 --char_pos_pct 60,20 --text_pos_pct 5,80 --text_width_pct 60 --font_size_pct 6 --out output_pct.png`
- 高度百分比缩放：
  - `cargo run -- --text "高度百分比测试" --char_height_pct 40 --char_pos_pct 10,10 --out output_hpct.png`
- 压缩 PNG（最佳压缩）：
  - `cargo run -- --text "压缩PNG测试" --compress --out output_png_best.png`
- 输出 JPEG（更小体积，有损）：
  - `cargo run -- --text "压缩JPEG测试" --format jpeg --quality 65 --out output_jpeg_65.jpg`

## 注意事项
- JPEG 不支持透明通道；当前合成在背景上完成，保存时会自动丢弃 alpha。
- 为尽量减小体积，优先考虑 `--format jpeg` 并适当降低 `--quality`；若需无损与透明，使用 `--compress` + `png`。
