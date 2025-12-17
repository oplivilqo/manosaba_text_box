use image::{imageops, Rgba, RgbaImage};
use imageproc::drawing::{draw_text_mut, text_size};
use rusttype::{Font, Scale};

#[derive(Clone, Copy)]
pub enum Align {
    Left,
    Center,
    Right,
}

pub struct TextStyle<'a> {
    pub font: &'a Font<'a>,
    pub size: f32,
    pub color: Rgba<u8>,
    pub shadow_color: Option<Rgba<u8>>,
    pub shadow_offset: (i32, i32),
    pub align: Align,
    pub max_width: u32,
}

pub fn load_font(bytes: Vec<u8>) -> Font<'static> {
    Font::try_from_vec(bytes).expect("invalid TTF font")
}

pub fn wrap_text_to_width<'a>(
    text: &str,
    font: &Font<'a>,
    scale: Scale,
    max_width: u32,
) -> Vec<String> {
    let mut lines: Vec<String> = Vec::new();
    for raw_line in text.split('\n') {
        let mut current = String::new();
        for word in raw_line.split_whitespace() {
            let tentative = if current.is_empty() {
                word.to_string()
            } else {
                format!("{} {}", current, word)
            };
            let (w, _) = text_size(scale, font, &tentative);
            if w as u32 <= max_width {
                current = tentative;
            } else {
                if !current.is_empty() {
                    lines.push(current);
                    current = word.to_string();
                } else {
                    // Extremely long single word: hard wrap by characters
                    let mut buf = String::new();
                    for ch in word.chars() {
                        buf.push(ch);
                        let (cw, _) = text_size(scale, font, &buf);
                        if cw as u32 > max_width {
                            buf.pop();
                            lines.push(buf);
                            buf = ch.to_string();
                        }
                    }
                    current = if buf.is_empty() { String::new() } else { buf };
                }
            }
        }
        if !current.is_empty() {
            lines.push(current);
        }
        if raw_line.is_empty() {
            lines.push(String::new());
        }
    }
    lines
}

pub fn draw_multiline_text(
    canvas: &mut RgbaImage,
    origin: (i32, i32),
    style: &TextStyle,
    lines: &[String],
) {
    let scale = Scale::uniform(style.size);
    let (mut x, mut y) = origin;
    for line in lines {
        let (w, h) = text_size(scale, style.font, line);
        let draw_x = match style.align {
            Align::Left => x,
            Align::Center => x + (style.max_width as i32 - w as i32) / 2,
            Align::Right => x + style.max_width as i32 - w as i32,
        };
        if let Some(shadow) = style.shadow_color {
            let sx = draw_x + style.shadow_offset.0;
            let sy = y + style.shadow_offset.1;
            draw_text_mut(canvas, shadow, sx, sy, scale, style.font, line);
        }
        draw_text_mut(canvas, style.color, draw_x, y, scale, style.font, line);
        y += h as i32 + 4;
    }
}
