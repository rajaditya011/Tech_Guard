# HomeGuardian AI — UI Design Prompts

**Version**: 1.0.0
**Last Updated**: 2026-04-11

Component visual specifications for every UI element. All values use CSS custom properties for theme flexibility.

---

## 1. Design Direction

- **Aesthetic**: Premium dark-first SaaS dashboard
- **Surface treatment**: Glassmorphism with subtle backdrop-filter blur
- **Accent system**: Neon semantic accents (blue, violet, emerald, amber, red)
- **Inspiration**: Linear, Vercel Dashboard, Raycast
- **Typography**: Inter (sans-serif), JetBrains Mono (monospace)
- **No emojis**: Use colored badges, numbered labels, monospace markers

---

## 2. Theme System

### Dark Theme (Default)

| Token               | Value                        | Usage                                    |
| -------------------- | ---------------------------- | ---------------------------------------- |
| bg-primary          | #08090f                      | Page background, main canvas             |
| bg-secondary        | #0f1119                      | Sidebar, card backgrounds                |
| bg-tertiary         | #161822                      | Elevated surfaces, nested cards          |
| bg-surface          | rgba(255,255,255,0.03)       | Input fields, subtle backgrounds         |
| bg-glass            | rgba(255,255,255,0.05)       | Glass card backgrounds                   |
| bg-glass-hover      | rgba(255,255,255,0.08)       | Glass card hover state                   |
| text-primary        | #f0f0f5                      | Headings, primary text                   |
| text-secondary      | #8b8fa3                      | Descriptions, body text                  |
| text-tertiary       | #555870                      | Labels, timestamps, metadata             |
| accent-blue         | #3b82f6                      | Live/active states, primary actions      |
| accent-violet       | #8b5cf6                      | AI/intelligence features, branding       |
| accent-emerald      | #10b981                      | Safe/normal states, success              |
| accent-amber        | #f59e0b                      | Warning states, elevated risk            |
| accent-red          | #ef4444                      | Critical states, danger, alerts          |
| border-primary      | rgba(255,255,255,0.06)       | Card borders, dividers                   |
| border-secondary    | rgba(255,255,255,0.10)       | Hover borders, stronger dividers         |

### Light Theme

| Token               | Value                        | Usage                                    |
| -------------------- | ---------------------------- | ---------------------------------------- |
| bg-primary          | #ffffff                      | Page background                          |
| bg-secondary        | #f8f9fc                      | Sidebar, card backgrounds                |
| bg-tertiary         | #f0f1f5                      | Elevated surfaces                        |
| bg-surface          | rgba(0,0,0,0.02)            | Input fields                             |
| bg-glass            | rgba(255,255,255,0.80)       | Glass card backgrounds                   |
| text-primary        | #111827                      | Headings, primary text                   |
| text-secondary      | #6b7280                      | Descriptions, body text                  |
| text-tertiary       | #9ca3af                      | Labels, metadata                         |
| accent-blue         | #2563eb                      | Reduced saturation for light backgrounds |
| accent-violet       | #7c3aed                      | Reduced saturation                       |
| accent-emerald      | #059669                      | Reduced saturation                       |
| accent-amber        | #d97706                      | Reduced saturation                       |
| accent-red          | #dc2626                      | Reduced saturation                       |

---

## 3. Component Specifications

### 3.1 Old Device Login Card

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Max width           | 384px (max-w-sm)                                |
| Background          | var(--bg-glass)                                 |
| Backdrop filter     | blur(12px)                                      |
| Border              | 1px solid var(--border-primary)                 |
| Border radius       | var(--radius-lg) (12px)                         |
| Padding             | 24px                                            |
| Shadow              | var(--shadow-md)                                |
| Input background    | var(--bg-surface)                               |
| Input border        | 1px solid var(--border-primary)                 |
| Input border-radius | var(--radius-md) (8px)                          |
| Input padding       | 10px 12px                                       |
| Input font size     | 14px                                            |
| Button background   | var(--accent-blue)                              |
| Button text         | #ffffff                                          |
| Button radius       | var(--radius-md) (8px)                          |
| Button padding      | 10px                                            |
| Button font weight  | 600                                             |
| Hover: border       | var(--border-secondary)                         |
| Focus: input border | var(--border-accent)                            |

### 3.2 Old Device Stream View

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Aspect ratio        | 4:3 (640x480)                                   |
| Background          | var(--bg-tertiary)                              |
| Border radius       | var(--radius-lg) (12px)                         |
| LIVE badge bg       | rgba(239, 68, 68, 0.9)                          |
| LIVE badge text     | #ffffff, 12px, font-mono                        |
| LIVE dot            | 8px, white, animate-pulse                       |
| Control button      | Full width, 40px height, var(--radius-md)       |

### 3.3 Baseline Progress Bar

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Track height        | 8px                                             |
| Track background    | var(--bg-surface)                               |
| Track radius        | var(--radius-full) (9999px)                     |
| Fill (learning)     | var(--accent-blue)                              |
| Fill (complete)     | var(--accent-emerald)                           |
| Fill radius         | var(--radius-full)                              |
| Fill transition     | width 500ms ease                                |
| Label font          | 12px, font-mono, uppercase                      |
| Label color         | var(--text-tertiary)                            |
| Percentage color    | var(--accent-blue)                              |

### 3.4 New Device Login Card

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Max width           | 448px (max-w-md)                                |
| Background          | var(--bg-glass)                                 |
| Backdrop filter     | blur(12px)                                      |
| Border              | 1px solid var(--border-primary)                 |
| Border radius       | var(--radius-lg) (12px)                         |
| Padding             | 32px                                            |
| Title               | gradient-text, 36px, font-weight 800            |
| Subtitle            | var(--text-secondary), 14px                     |
| Badge               | var(--accent-violet-glow) bg, var(--accent-violet) text |
| Submit button       | gradient(135deg, accent-blue, accent-violet)    |
| Demo link           | var(--accent-emerald), 14px                     |

### 3.5 Dashboard Sidebar

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Width (expanded)    | 240px                                           |
| Width (collapsed)   | 64px                                            |
| Background          | var(--bg-secondary)                             |
| Border right        | 1px solid var(--border-primary)                 |
| Transition          | width 300ms ease                                |
| Nav item padding    | 10px 12px                                       |
| Nav item radius     | var(--radius-md) (8px)                          |
| Active item bg      | var(--bg-glass)                                 |
| Active icon bg      | var(--accent-blue)                              |
| Active icon color   | #ffffff                                          |
| Inactive color      | var(--text-secondary)                           |
| Logo size           | 32px, radius var(--radius-md)                   |
| Logo bg             | gradient(135deg, accent-blue, accent-violet)    |

### 3.6 Live Feed Grid

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Grid columns        | 2 (compact) or 3 (full)                         |
| Gap                 | 16px                                            |
| Card background     | var(--bg-glass)                                 |
| Aspect ratio        | 16:9 video area                                 |
| LIVE badge          | Same as Old Device Stream View                  |
| Status dot          | 8px, emerald (active), amber (learning)         |
| Info padding        | 12px                                            |
| Name font           | 14px, font-weight 500                           |
| ID font             | 12px, font-mono, var(--text-tertiary)           |

### 3.7 Camera Overlay (Bounding Boxes and Zone Labels)

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Box border          | 2px solid var(--accent-blue)                    |
| Box background      | transparent                                     |
| Label background    | var(--accent-blue) at 90% opacity               |
| Label text          | #ffffff, 10px, font-mono                        |
| Label position      | Top-left corner of bounding box                 |
| Zone label bg       | var(--bg-glass) at 80% opacity                  |
| Zone label text     | var(--text-primary), 11px, font-mono            |
| Zone label position | Bottom-center of zone area                      |
| Anomaly highlight   | 2px dashed var(--accent-red)                    |

### 3.8 Floor Plan SVG Visualizer

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Background          | var(--bg-surface)                               |
| Border radius       | var(--radius-lg) (12px)                         |
| Zone fill (normal)  | var(--accent-emerald) at 5-15% opacity          |
| Zone fill (elevated)| var(--accent-amber) at 15-30% opacity           |
| Zone fill (anomaly) | var(--accent-red) at 20-40% opacity             |
| Zone stroke         | var(--border-secondary)                         |
| Zone stroke (sel)   | var(--accent-blue), 2px                         |
| Zone label font     | 10px, font-mono, var(--text-secondary)          |
| Zone rx             | 4px                                             |
| Transition          | fill-opacity 600ms ease                         |

### 3.9 Heat Zone Gradient System

| Intensity Level     | Color                         | Opacity         |
| -------------------- | ----------------------------- | --------------- |
| 0.0 - 0.1          | var(--accent-emerald)         | 3-5%            |
| 0.1 - 0.3          | var(--accent-emerald)         | 5-15%           |
| 0.3 - 0.5          | var(--accent-emerald)         | 15-25%          |
| 0.5 - 0.7          | var(--accent-amber)           | 15-25%          |
| 0.7 - 0.9          | var(--accent-amber)           | 25-35%          |
| 0.9 - 1.0          | var(--accent-red)             | 30-40%          |

### 3.10 Alert Feed Item

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Background          | var(--bg-surface)                               |
| Border              | 1px solid var(--border-primary)                 |
| Border radius       | var(--radius-md) (8px)                          |
| Padding             | 12px                                            |
| Risk badge          | Colored pill (accent color for level)           |
| Risk badge font     | 11px, font-mono, uppercase                      |
| Timestamp font      | 12px, var(--text-tertiary)                      |
| Summary font        | 14px, var(--text-primary)                       |
| Hover               | border-color var(--border-secondary)            |
| Animation           | slide-in-right on arrival                       |

### 3.11 Risk Score Arc Gauge

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Large size          | 180px diameter                                  |
| Small size          | 48px diameter                                   |
| Track stroke        | var(--border-primary)                           |
| Track width (lg)    | 12px                                            |
| Track width (sm)    | 4px                                             |
| Arc start angle     | 0.75 * PI (135 degrees)                         |
| Arc end angle       | 2.25 * PI (405 degrees)                         |
| Arc range           | 270 degrees                                     |
| Low color           | var(--accent-emerald)                           |
| Medium color        | var(--accent-amber)                             |
| High color          | var(--accent-amber)                             |
| Critical color      | var(--accent-red)                               |
| Line cap            | round                                           |
| Score font          | 30px, font-weight 700                           |
| Label font          | 12px, font-mono, uppercase, var(--text-tertiary)|
| Animation           | arc draw 600ms ease-out                         |

### 3.12 AI Narrative Modal

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Overlay             | rgba(0,0,0,0.6) with backdrop-filter blur(8px) |
| Modal max-width     | 640px                                           |
| Background          | var(--bg-secondary)                             |
| Border              | 1px solid var(--border-primary)                 |
| Border radius       | var(--radius-xl) (16px)                         |
| Padding             | 32px                                            |
| Header              | Risk badge + zone + timestamp                   |
| Narrative text      | 15px, line-height 1.7, var(--text-primary)      |
| Evidence section    | var(--bg-surface) background, 12px, font-mono   |
| Clip player         | Full width, aspect-ratio 16:9, radius-lg        |
| Animation           | fade-in + slide-up 300ms                        |

### 3.13 Clip Player

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Aspect ratio        | 16:9                                            |
| Background          | #000000                                          |
| Border radius       | var(--radius-lg) (12px)                         |
| Controls            | Native HTML5 video controls                     |
| Timestamp overlay   | Bottom-left, 12px, font-mono, white on dark bg  |

### 3.14 System Status Badge

| Status      | Dot Color              | Background             | Text Color             | Animation        |
| ----------- | ---------------------- | ---------------------- | ---------------------- | ---------------- |
| Active      | var(--accent-emerald)  | emerald at 10% opacity | var(--accent-emerald)  | pulse 3s         |
| Learning    | var(--accent-blue)     | blue at 10% opacity    | var(--accent-blue)     | pulse 3s         |
| Alert       | var(--accent-red)      | red at 10% opacity     | var(--accent-red)      | pulse 1.5s       |
| Inactive    | var(--text-tertiary)   | surface                | var(--text-tertiary)   | none             |

### 3.15 Sensor Node Health Indicator

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Layout              | Horizontal card, space-between                  |
| Background          | var(--bg-glass)                                 |
| Border              | 1px solid var(--border-primary)                 |
| Padding             | 16px                                            |
| Status dot          | 8px, color per status                           |
| Name font           | 14px, font-weight 500                           |
| ID/Type font        | 12px, font-mono, var(--text-tertiary)           |
| Status label        | 12px, font-mono, uppercase, status color        |
| Heartbeat font      | 12px, var(--text-tertiary)                      |

### 3.16 Two-Way Communication Panel

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Background          | var(--bg-glass)                                 |
| Padding             | 24px                                            |
| Select background   | var(--bg-surface)                               |
| Select border       | 1px solid var(--border-primary)                 |
| Textarea height     | 3 rows (~72px)                                  |
| Send button         | var(--accent-blue), full width                  |
| Send disabled       | var(--bg-surface) bg, var(--text-tertiary) text |

### 3.17 Theme Toggle Button

| Property            | Value                                           |
| -------------------- | ----------------------------------------------- |
| Position            | fixed, top 16px, right 16px                     |
| Background          | var(--bg-glass)                                 |
| Backdrop filter     | blur(12px)                                      |
| Border              | 1px solid var(--border-secondary)               |
| Border radius       | 8px                                             |
| Padding             | 6px 12px                                        |
| Font                | 12px, font-mono, uppercase, tracking-wider      |
| Color               | var(--text-secondary)                           |
| Hover border        | var(--accent-blue)                              |
| Z-index             | 1000                                            |

---

## 4. Global Animation Specs

| Animation Name      | Duration  | Easing                         | Trigger               | Description                              |
| -------------------- | --------- | ------------------------------ | --------------------- | ---------------------------------------- |
| pulse               | 3s        | cubic-bezier(0.4, 0, 0.6, 1) | Continuous (active)   | Subtle opacity pulse for status badges   |
| pulse-fast          | 1.5s      | cubic-bezier(0.4, 0, 0.6, 1) | Continuous (alert)    | Faster pulse for alert state             |
| glow-sweep          | 2s        | ease-in-out, alternate         | Alert arrival         | Brightness sweep on alert cards          |
| fade-in             | 300ms     | ease-out                       | Component mount       | Opacity 0 to 1                           |
| slide-up            | 400ms     | ease-out                       | Modal open            | translateY(10px) to 0 + fade-in          |
| slide-in-right      | 300ms     | ease-out                       | Alert arrival         | translateX(20px) to 0 + fade-in          |
| arc-draw            | 600ms     | ease-out                       | Gauge mount/update    | Arc stroke-dashoffset animation          |
| heat-fade           | 600ms     | ease-in-out                    | Zone activity change  | Fill-opacity transition                  |
| thumbnail-reveal    | 250ms     | ease-out                       | Clip thumbnail load   | Scale(0.95) to 1 + fade-in              |

---

## 5. Color Usage Rules

| Semantic Purpose      | Accent Color       | Usage Examples                                  |
| --------------------- | ------------------ | ----------------------------------------------- |
| Live / Active / Online| accent-blue        | LIVE badge, active sensor dot, streaming status |
| AI / Intelligence     | accent-violet      | AI narrative badge, prediction engine, branding |
| Safe / Normal / OK    | accent-emerald     | Normal status, low risk, baseline complete      |
| Warning / Elevated    | accent-amber       | Medium risk, elevated activity, learning state  |
| Critical / Danger     | accent-red         | Critical risk, alert state, intrusion detected  |

---

## 6. Spacing and Layout Rules

| Context                        | Spacing Value     |
| ------------------------------ | ----------------- |
| Page padding                   | 24px (space-6)    |
| Card padding                   | 16-24px           |
| Section gap                    | 24px (space-6)    |
| Component internal gap         | 8-16px            |
| Label to input gap             | 8px (space-2)     |
| Between nav items              | 4px (space-1)     |
| Dashboard grid gap             | 24px              |
| Sidebar width (expanded)       | 240px             |
| Sidebar width (collapsed)      | 64px              |
| Header height                  | 64px              |
