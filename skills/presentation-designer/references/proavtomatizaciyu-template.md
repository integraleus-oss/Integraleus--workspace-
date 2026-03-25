# Шаблон PROавтоматизацию 2025 — Reference

Conference presentation template for industrial automation events.
Source: `Шаблон_-_PROавтоматизацию2025-1920.pptx`

## Dimensions
- **Slide size**: 17275175 × 9717088 EMU = 18.89 × 10.63 inches = ~1813 × 1020 px @96dpi
- **Aspect ratio**: 16:9 (wide, conference projection format)
- **Note**: This is NOT standard PowerPoint 16:9 (13.333 × 7.5 in). Use the .pptx as template base.

## Theme: TechConf
### Color Scheme
| Role     | Color     | Hex       | Usage |
|----------|-----------|-----------|-------|
| dk1      | Black     | `#000000` | Dark text on light slides |
| dk2      | Slate     | `#44546A` | Secondary text |
| lt1      | White     | `#FFFFFF` | Light text on dark slides |
| lt2      | Light gray| `#E7E6E6` | Subtle backgrounds |
| accent1  | Teal/Cyan | `#0997C8` | **Primary accent** — links, highlights |
| accent2  | Green     | `#82C444` | **Bullet markers**, list accents |
| accent3  | Deep Blue | `#005497` | Headers, strong emphasis |
| accent4  | Dark Teal | `#067196` | Secondary accent |
| accent5  | Dark Green| `#61962F` | Tertiary accent |
| accent6  | Purple    | `#7030A0` | Rarely used |
| hlink    | Teal      | `#0997C8` | Hyperlinks |
| folHlink | Slate     | `#44546A` | Followed hyperlinks |

### Font Scheme
- **Major (headings)**: Arial (`+mj-lt`)
- **Minor (body)**: Arial (`+mn-lt`)
- **Accent font**: Montserrat (used at deeper bullet levels)

### Slide Number Color
- Gray `#838383`

## Layouts (14 total)

### 1. Главный-1 (Title slide, variant 1)
- Full-bleed background image
- Placeholders:
  - idx=0: CENTER_TITLE — report title (48pt, bold, white)
  - idx=1: SUBTITLE — speaker name (24pt, bold, white)
  - idx=10: BODY — position/job title (24pt, white)
  - idx=15: OBJECT — company logo area
- Position: content left-aligned, ~1.45in from left

### 2. Главный-2 (Title slide, variant 2)
- Similar to Главный-1, different vertical positioning
- Logo placeholder at right side (14.40in from left)

### 3. Заголовок и текст-б (Title + text, light)
- **White background**
- idx=0: TITLE (0.55, 0.56) — slide title
- idx=1: OBJECT (0.55, 1.89) — main content area, 17.94 × 7.63 in
- idx=14: FOOTER (0.55, 8.97) — footer text
- Bullet markers use accent2 (green `#82C444`)
- Body text: black (dk1)

### 4. Заголовок и текст-ч (Title + text, dark)
- **Dark background**
- Same structure as light, but:
  - Title: white (bg1)
  - Body text: white (bg2)
  - Bullet markers: green accent2
- Has slide number placeholder

### 5. Большой заголовок-б (Big title, light)
- Title area: 17.02 × 1.77 in (large)
- Content area starts at y=2.94in
- Body text sizes: 28pt → 24pt → 24pt descending
- Good for: section intros, key statements

### 6. Большой заголовок-ч (Big title, dark)
- Dark variant of above
- All text white (bg1)

### 7. Большая картинка-б (Big picture, light)
- Title + large picture placeholder (17.90 × 7.58 in)
- Footer below image
- Good for: screenshots, diagrams, photos

### 8. Большая картинка-ч (Big picture, dark)
- Dark variant

### 9. Две колонки-б (Two columns, light)
- Title at top
- Two equal content columns: each 8.64 × 7.58 in
  - Left: starts at x=0.55in
  - Right: starts at x=9.70in
- Body text 28pt → 24pt
- Bullet markers: green accent2
- Footer at bottom

### 10. Две колонки-ч (Two columns, dark)
- Dark variant, white text

### 11. Разделитель (Section divider)
- Large title (54pt, white)
- Description text below (32pt → 20pt)
- Background image
- Good for: separating major sections

### 12. Пустой-б (Blank, light)
- Only slide number
- Free-form layout

### 13. Пустой-ч (Blank, dark)
- Only slide number
- Free-form layout on dark background

### 14. Финальный-1 (Final/CTA)
- Large CTA title (60pt, white) — top left
- Subtitle area: speaker name, position, contacts (24pt)
- Company logo placeholder (top right, 5.33 × 2.33 in)
- QR code placeholder (bottom right, 3.15 × 3.15 in)

## Usage Notes for python-pptx

### Opening as template
```python
from pptx import Presentation
prs = Presentation('Шаблон_-_PROавтоматизацию2025-1920.pptx')
# Layouts are accessible via prs.slide_layouts[index]
# Index 0 = Главный-1, 1 = Главный-2, etc.
```

### Layout index map
```python
LAYOUTS = {
    'title_1': 0,       # Главный-1
    'title_2': 1,       # Главный-2
    'content_light': 2,  # Заголовок и текст-б
    'content_dark': 3,   # Заголовок и текст-ч
    'big_title_light': 4, # Большой заголовок-б
    'big_title_dark': 5,  # Большой заголовок-ч
    'big_picture_light': 6, # Большая картинка-б
    'big_picture_dark': 7,  # Большая картинка-ч
    'two_col_light': 8,  # Две колонки-б
    'two_col_dark': 9,   # Две колонки-ч
    'divider': 10,       # Разделитель
    'blank_light': 11,   # Пустой-б
    'blank_dark': 12,    # Пустой-ч
    'final': 13,         # Финальный-1
}
```

### Placeholder index map per layout
```python
PLACEHOLDERS = {
    'title_1': {'title': 0, 'subtitle': 1, 'body': 10, 'logo': 15},
    'title_2': {'title': 0, 'subtitle': 1, 'body': 10, 'logo': 15},
    'content_light': {'title': 0, 'content': 1, 'footer': 14},
    'content_dark': {'title': 0, 'content': 1, 'footer': 14, 'slide_num': 13},
    'big_title_light': {'title': 0, 'content': 1, 'footer': 14, 'slide_num': 13},
    'big_title_dark': {'title': 0, 'content': 1, 'footer': 14, 'slide_num': 13},
    'big_picture_light': {'title': 0, 'picture': 15, 'footer': 14, 'slide_num': 13},
    'big_picture_dark': {'title': 0, 'picture': 15, 'footer': 14, 'slide_num': 13},
    'two_col_light': {'title': 0, 'left': 1, 'right': 2, 'footer': 10, 'slide_num': 13},
    'two_col_dark': {'title': 0, 'left': 1, 'right': 2, 'footer': 10, 'slide_num': 13},
    'divider': {'title': 0, 'description': 1},
    'blank_light': {'slide_num': 13},
    'blank_dark': {'slide_num': 13},
    'final': {'title': 0, 'subtitle': 1, 'logo': 15, 'qr': 16},
}
```

### Important: remove template sample slides
After opening the template, delete all existing slides before adding new ones:
```python
# Remove all sample slides from template
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].get(qn('r:id'))
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])
```

### Working with placeholders
```python
slide = prs.slides.add_slide(prs.slide_layouts[2])  # content_light
slide.placeholders[0].text = "Заголовок слайда"
slide.placeholders[1].text = "Основной текст"
slide.placeholders[14].text = "Подпись"
```
