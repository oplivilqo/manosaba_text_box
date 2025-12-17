use std::path::{Path, PathBuf};

use image::{imageops, DynamicImage, GenericImageView, ImageBuffer, Rgba, RgbaImage};
use thiserror::Error;

use crate::core::text_processor::{draw_multiline_text, load_font, wrap_text_to_width, Align, TextStyle};

#[derive(Error, Debug)]
pub enum GenError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("image error: {0}")]
    Image(#[from] image::ImageError),
    #[error("font error: {0}")]
    Font(String),
}

pub struct GenerationParams {
    pub background_path: PathBuf,
    pub character_path: Option<PathBuf>,
    pub font_path: PathBuf,
    pub text: String,
    pub font_size: f32,
    pub text_color: Rgba<u8>,
    pub output_path: PathBuf,
    // 新增：以背景为基准的百分比参数
    pub overlay_width_pct: Option<f32>,      // 角色叠加宽度占背景宽度的百分比（0-100）
    pub overlay_height_pct: Option<f32>,     // 角色叠加高度占背景高度的百分比（0-100）
    pub overlay_pos_pct: Option<(f32, f32)>, // 角色左上角位置（x%, y%）
    pub text_pos_pct: Option<(f32, f32)>,    // 文本起始点位置（x%, y%）
    pub text_width_pct: Option<f32>,         // 文本区域宽度占背景宽度的百分比（0-100）
    pub font_size_pct: Option<f32>,          // 字体大小占背景高度的百分比（0-100）
    // 压缩/格式
    pub compress: bool,
    pub format: Option<String>, // "png" | "jpeg"
    pub quality: Option<u8>,    // JPEG quality
}

pub fn generate_image(params: GenerationParams) -> Result<PathBuf, GenError> {
    let bg = image::open(&params.background_path)?;
    let mut canvas = bg.to_rgba8();

    if let Some(chara_path) = &params.character_path {
        let overlay_img = image::open(chara_path)?.to_rgba8();
        let (cw, ch) = canvas.dimensions();
        let (ow, oh) = overlay_img.dimensions();
        // 计算缩放
        let (new_ow, new_oh) =
            if let Some(pct) = params.overlay_width_pct {
                let target_w = (cw as f32 * (pct / 100.0)).max(1.0);
                let scale = target_w / (ow as f32);
                let w = (ow as f32 * scale).round() as u32;
                let h = (oh as f32 * scale).round() as u32;
                (w, h)
            } else if let Some(pct) = params.overlay_height_pct {
                let target_h = (ch as f32 * (pct / 100.0)).max(1.0);
                let scale = target_h / (oh as f32);
                let w = (ow as f32 * scale).round() as u32;
                let h = (oh as f32 * scale).round() as u32;
                (w, h)
            } else {
                let target = cw.min(ch) as f32 * 0.75;
                let max_dim = ow.max(oh) as f32;
                let scale_factor = (target / max_dim).min(1.0);
                ((ow as f32 * scale_factor) as u32, (oh as f32 * scale_factor) as u32)
            };
        let resized = image::imageops::resize(&overlay_img, new_ow, new_oh, imageops::Lanczos3);
        // 计算位置
        let (pos_x, pos_y) = if let Some((x_pct, y_pct)) = params.overlay_pos_pct {
            let x = (cw as f32 * (x_pct / 100.0)).round() as u32;
            let y = (ch as f32 * (y_pct / 100.0)).round() as u32;
            (x, y)
        } else {
            ((cw / 2).saturating_sub(new_ow / 2), (ch / 2).saturating_sub(new_oh / 2))
        };
        imageops::overlay(&mut canvas, &resized, pos_x as i64, pos_y as i64);
    }

    let font_bytes = std::fs::read(&params.font_path).map_err(|e| GenError::Font(e.to_string()))?;
    let font = load_font(font_bytes);

    let (cw, ch) = canvas.dimensions();
    let margin = 24u32;
    let max_width = if let Some(pct) = params.text_width_pct {
        (cw as f32 * (pct / 100.0)).round() as u32
    } else {
        cw - margin * 2
    };
    let font_size = if let Some(pct) = params.font_size_pct {
        ch as f32 * (pct / 100.0)
    } else {
        params.font_size
    };
    let scale = rusttype::Scale::uniform(font_size);
    let lines = wrap_text_to_width(&params.text, &font, scale, max_width);

    let style = TextStyle {
        font: &font,
        size: font_size,
        color: params.text_color,
        shadow_color: Some(Rgba([0, 0, 0, 160])),
        shadow_offset: (2, 2),
        align: Align::Left,
        max_width,
    };
    let (start_x, start_y) = if let Some((x_pct, y_pct)) = params.text_pos_pct {
        let x = (cw as f32 * (x_pct / 100.0)).round() as i32;
        let y = (ch as f32 * (y_pct / 100.0)).round() as i32;
        (x, y)
    } else {
        (margin as i32, (ch as f32 * 0.75) as i32)
    };

    draw_multiline_text(&mut canvas, (start_x, start_y), &style, &lines);

    save_with_options(&canvas, &params)?;
    Ok(params.output_path)
}

pub fn find_first_png(dir: &Path) -> Option<PathBuf> {
    std::fs::read_dir(dir)
        .ok()?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|ext| ext.to_string_lossy().to_lowercase() == "png").unwrap_or(false))
        .min()
}

pub fn find_first_ttf(dir: &Path) -> Option<PathBuf> {
    std::fs::read_dir(dir)
        .ok()?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map(|ext| ext.to_string_lossy().to_lowercase() == "ttf").unwrap_or(false))
        .min()
}

fn save_with_options(canvas: &RgbaImage, params: &GenerationParams) -> Result<(), GenError> {
    use std::fs::File;
    use std::io::BufWriter;
    use image::codecs::png::{CompressionType, FilterType, PngEncoder};
    use image::codecs::jpeg::JpegEncoder;
    use image::ImageEncoder;

    let target_fmt = params.format.as_ref().map(|s| s.to_lowercase()).or_else(|| {
        params
            .output_path
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
    });

    let writer = BufWriter::new(File::create(&params.output_path)?);
    match target_fmt.as_deref() {
        Some("jpeg") | Some("jpg") => {
            let quality = params.quality.unwrap_or(85).clamp(1, 100);
            let mut enc = JpegEncoder::new_with_quality(writer, quality);
            // 丢弃 alpha，保存为 RGB
            let (w, h) = canvas.dimensions();
            let mut rgb = Vec::with_capacity((w * h * 3) as usize);
            for p in canvas.pixels() {
                rgb.push(p[0]);
                rgb.push(p[1]);
                rgb.push(p[2]);
            }
            enc.encode(&rgb, w, h, image::ColorType::Rgb8)?;
        }
        _ => {
            if params.compress {
                let enc = PngEncoder::new_with_quality(writer, CompressionType::Best, FilterType::Adaptive);
                enc.write_image(
                    canvas.as_raw(),
                    canvas.width(),
                    canvas.height(),
                    image::ColorType::Rgba8,
                )?;
            } else {
                let enc = PngEncoder::new(writer);
                enc.write_image(
                    canvas.as_raw(),
                    canvas.width(),
                    canvas.height(),
                    image::ColorType::Rgba8,
                )?;
            }
        }
    }
    Ok(())
}
