mod core;

use std::path::PathBuf;

use clap::Parser;
use image::Rgba;

use crate::core::image_generator::{find_first_png, find_first_ttf, generate_image, GenerationParams};

#[derive(Parser, Debug)]
#[command(name = "text-to-picture")]
#[command(about = "生成带文本的合成图片（后台核心）")]
struct Args {
    #[arg(long, value_name = "PATH", help = "背景图片路径（默认取 assets/background 下第一个 PNG）")]
    background: Option<PathBuf>,
    #[arg(long, value_name = "PATH", help = "角色图片路径（可选，默认取 assets/chara 下第一个 PNG）")]
    character: Option<PathBuf>,
    #[arg(long = "char_width_pct", alias = "char-width-pct", value_name = "PERCENT", help = "角色叠加宽度占背景宽度的百分比（0-100）")]
    char_width_pct: Option<f32>,
    #[arg(long = "char_height_pct", alias = "char-height-pct", value_name = "PERCENT", help = "角色叠加高度占背景高度的百分比（0-100）")]
    char_height_pct: Option<f32>,
    #[arg(long = "char_pos_pct", alias = "char-pos-pct", value_name = "X,Y", help = "角色叠加左上角位置（x%、y%），以背景为参考")]
    char_pos_pct: Option<String>,
    #[arg(long, value_name = "PATH", help = "字体文件路径（默认取 assets/fonts 下第一个 TTF）")]
    font: Option<PathBuf>,
    #[arg(long, value_name = "TEXT", help = "要绘制的文本")]
    text: Option<String>,
    #[arg(long, default_value_t = 48.0, help = "字体大小（像素），若提供 --font_size_pct/--font-size-pct 则被覆盖")]
    font_size: f32,
    #[arg(long = "font_size_pct", alias = "font-size-pct", value_name = "PERCENT", help = "字体大小占背景高度的百分比（0-100）")]
    font_size_pct: Option<f32>,
    #[arg(long = "text_pos_pct", alias = "text-pos-pct", value_name = "X,Y", help = "文本起始位置（x%、y%），以背景为参考")]
    text_pos_pct: Option<String>,
    #[arg(long = "text_width_pct", alias = "text-width-pct", value_name = "PERCENT", help = "文本区域宽度占背景宽度的百分比（0-100）")]
    text_width_pct: Option<f32>,
    #[arg(long, value_name = "PATH", default_value = "output.png", help = "输出图片路径")]
    out: PathBuf,
    #[arg(long, help = "启用压缩（尽可能减小文件大小）")]
    compress: bool,
    #[arg(long, value_name = "FORMAT", help = "输出格式（png 或 jpeg），默认根据 --out 扩展名或使用 png")]
    format: Option<String>,
    #[arg(long, value_name = "QUALITY", help = "JPEG 质量（1-100），默认 85；PNG 无该参数")]
    quality: Option<u8>,
}

fn main() {
    let args = Args::parse();
    let project_root = std::env::current_dir().expect("cannot get cwd");
    let assets = project_root.join("assets");

    let background = args.background.or_else(|| {
        find_first_png(&assets.join("background"))
    }).expect("未找到背景图片，请提供 --background 或确保 assets/background 下存在 PNG");

    let character = args.character.or_else(|| {
        // 深度遍历 chara 子目录以寻找第一个 PNG
        let chara_root = assets.join("chara");
        std::fs::read_dir(&chara_root).ok().and_then(|mut it| {
            it.find_map(|entry| {
                let p = entry.ok()?.path();
                if p.is_dir() {
                    find_first_png(&p)
                } else {
                    None
                }
            })
        })
    });

    let font = args.font.or_else(|| {
        find_first_ttf(&assets.join("fonts"))
    }).expect("未找到字体文件，请提供 --font 或确保 assets/fonts 下存在 TTF");

    let text = args.text.unwrap_or_else(|| "魔女裁判・文本生成器（Rust）".to_string());

    fn parse_xy_pct(s: &Option<String>) -> Option<(f32, f32)> {
        s.as_ref().and_then(|v| {
            let parts: Vec<&str> = v.split(',').collect();
            if parts.len() != 2 { return None; }
            let x = parts[0].trim().parse::<f32>().ok()?;
            let y = parts[1].trim().parse::<f32>().ok()?;
            Some((x, y))
        })
    }

    let params = GenerationParams {
        background_path: background,
        character_path: character,
        font_path: font,
        text,
        font_size: args.font_size,
        text_color: Rgba([255, 255, 255, 255]),
        output_path: args.out,
        overlay_width_pct: args.char_width_pct,
        overlay_height_pct: args.char_height_pct,
        overlay_pos_pct: parse_xy_pct(&args.char_pos_pct),
        text_pos_pct: parse_xy_pct(&args.text_pos_pct),
        text_width_pct: args.text_width_pct,
        font_size_pct: args.font_size_pct,
        compress: args.compress,
        format: args.format,
        quality: args.quality,
    };

    match generate_image(params) {
        Ok(path) => {
            println!("图片已生成: {}", path.display());
        }
        Err(e) => {
            eprintln!("生成失败: {}", e);
            std::process::exit(1);
        }
    }
}
