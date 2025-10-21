# domishot

Capture **just one DOM element** from **any web page** and save it as an image.

- 🧠 **Headless browser** rendering (JS/CSS supported)
- 🎯 **Element-only** screenshots via **CSS selector**
- 🍪 Auto-accepts common cookie banners (best effort)
- 🖼️ **Hi-DPI** output (Playwright `device_scale_factor`)
- 🔧 Use it from the **CLI** or **Python API**
- 🔌 Choose your engine: **Playwright** (recommended) or **Selenium**

---

## Table of Contents
- [domishot](#domishot)
  - [Table of Contents](#table-of-contents)
  - [Why domishot?](#why-domishot)
  - [Quick Install](#quick-install)
  - [Quick Start](#quick-start)
  - [CLI Usage](#cli-usage)
  - [Python API](#python-api)
  - [Examples](#examples)
  - [Advanced Topics](#advanced-topics)
    - [Getting crisp text](#getting-crisp-text)
    - [Dynamic/Lazy content](#dynamiclazy-content)
    - [Cookie/consent banners](#cookieconsent-banners)
    - [Iframes / Shadow DOM](#iframes--shadow-dom)
    - [Headless quirks](#headless-quirks)
  - [Troubleshooting](#troubleshooting)
  - [Project Layout](#project-layout)
  - [Versioning \& Releases](#versioning--releases)
  - [Contributing](#contributing)
  - [License](#license)

---

## Why domishot?

When you only need **one widget/card/table** from a web page—**not** the whole page—manual cropping and full-page screenshots are clunky and fragile. **domishot**:

- Loads the page like a browser (executes JS, applies CSS).
- Locates your target with a **CSS selector**.
- Saves **only that element** as a crisp **PNG**.
- Works great for dashboards, daily digests, bots, monitoring, and reports.

---

## Quick Install

> Pick **one** backend (you can install both).

**Selenium (simpler start)**
```bash
pip install "domishot[selenium]"
```

**Playwright (recommended quality)**
```bash
pip install "domishot[playwright]"
playwright install chromium
```

> **zsh users**: always quote extras — `"domishot[selenium]"`

---

## Quick Start

**CLI**
```bash
domishot "https://www.omie.es/es/spot-hoy"   "div.market-data-block.average"   -o omie.png --backend selenium
```

**Python**
```python
from domishot import capture, CaptureOptions

capture(
    url="https://www.omie.es/es/spot-hoy",
    selector="div.market-data-block.average",
    out="omie.png",
    opts=CaptureOptions(backend="auto", device_scale_factor=3)  # sharper text
)
```

> `backend="auto"` = use Playwright if installed, otherwise fall back to Selenium.

---

## CLI Usage

```
domishot URL SELECTOR --out PATH
                      [--backend auto|playwright|selenium]
                      [--width 1400] [--height 1000] [--dpr 2]
                      [--locale es-ES] [--no-accept-cookies]
                      [--timeout 30000] [--extra-wait 400]
```

**Arguments**
- `URL` – page to load  
- `SELECTOR` – CSS selector for the element (e.g., `#id`, `.card`, `#main > .widget`)  
- `--out/-o` – output PNG path (e.g., `snippet.png`)  
- `--backend` – `auto` (default), `playwright`, or `selenium`  
- `--width/--height` – viewport size (px)  
- `--dpr` – device pixel ratio (Playwright only)  
- `--locale` – browser locale (default `es-ES`)  
- `--no-accept-cookies` – disable cookie auto-accept  
- `--timeout` – Playwright wait timeout in ms (default `30000`)  
- `--extra-wait` – extra settle delay after scroll/render in ms (default `400`)  

---

## Python API

```python
from domishot import capture, CaptureOptions

opts = CaptureOptions(
    backend="auto",            # or "playwright" / "selenium"
    viewport=(1400, 1000),
    device_scale_factor=2,     # Playwright-only
    wait_until="networkidle",  # Playwright: "load"|"domcontentloaded"|"networkidle"
    timeout_ms=30000,
    locale="es-ES",
    accept_cookies=True,
    extra_wait_ms=400,
)

capture("https://example.com", "#main > .card", "card.png", opts)
```

**Function reference**
- `capture(url: str, selector: str, out: str, opts: Optional[CaptureOptions] = None) -> None`
- `CaptureOptions` fields:
  - `backend`: `"auto" | "playwright" | "selenium"`
  - `viewport`: `(width, height)`
  - `device_scale_factor`: int (Playwright only; **2–3** for Hi-DPI)
  - `wait_until`: `"load" | "domcontentloaded" | "networkidle"` (Playwright)
  - `timeout_ms`: int (Playwright waits)
  - `locale`: e.g., `"es-ES"`
  - `accept_cookies`: bool (auto-consent clickers)
  - `extra_wait_ms`: int (post-render settle)

---

## Examples

**OMIE “spot-hoy”**
```bash
# narrow card
domishot "https://www.omie.es/es/spot-hoy" "#block-prices-and-volumes" -o omie.png --backend selenium

# wider container
domishot "https://www.omie.es/es/spot-hoy" "div.market-data-block.average" -o omie.png
```

**Hi-DPI with Playwright**
```bash
domishot "https://example.com" ".kpi" -o kpi.png --backend playwright --dpr 3
```

---

## Advanced Topics

### Getting crisp text
- Prefer **Playwright** and set `--dpr 2` or `3`.
- If using Selenium, increase the **viewport** to capture at higher resolution.

### Dynamic/Lazy content
- Increase `--extra-wait` (e.g., `800–1500` ms).
- With Playwright, `wait_until="networkidle"` helps in JS-heavy pages.

### Cookie/consent banners
- domishot tries common patterns (`OneTrust`, “Aceptar”, “Accept”…).
- For custom banners, use `--no-accept-cookies` and handle manually in a fork.

### Iframes / Shadow DOM
- If content lives inside an iframe or shadow root, you may need to extend the code:
  - Playwright: target the frame via `page.frame(...)` before selecting.
  - Selenium: `driver.switch_to.frame(...)` then find the element.

### Headless quirks
- Sites sometimes behave differently in headless mode.
- Try the other backend, increase `--extra-wait`, or temporarily run non-headless in your fork for debugging.

---

## Troubleshooting

**“No supported backend available”**  
Install an extra:
```bash
pip install "domishot[selenium]"
# or
pip install "domishot[playwright]" && playwright install chromium
```

**zsh error: `no matches found: .[selenium]`**  
Quote extras:
```bash
pip install -e ".[selenium]"
```

**Build error: `package directory 'src/domishot' does not exist`**  
Ensure layout:
```
pyproject.toml
README.md
src/domishot/__init__.py
src/domishot/core.py
src/domishot/cli.py
```

**Dependency conflicts (e.g., urllib3)**  
Use a dedicated virtual environment or upgrade the conflicting package.

**Dynamic content never appears**  
Increase `--extra-wait`; ensure the selector matches what actually renders; consider Playwright.

**Consent banner not dismissed**  
Pass `--no-accept-cookies` and extend selectors in `core.py` for your site.

---

## Project Layout

```
domishot/
├─ pyproject.toml
├─ README.md
└─ src/
   └─ domishot/
      ├─ __init__.py
      ├─ cli.py
      └─ core.py
```

---

## Versioning & Releases

- Follows **semver-ish**: `MAJOR.MINOR.PATCH`
- **Do not** reuse versions on PyPI/TestPyPI.
- Typical release flow:
  1. Bump `version` in `pyproject.toml`
  2. `python -m build`
  3. `twine upload` (TestPyPI first, then PyPI)

---

## Contributing

PRs welcome! A quick dev setup:

```bash
git clone https://github.com/<you-or-org>/domishot
cd domishot
pip install -e ".[playwright]"  # or ".[selenium]"
playwright install chromium      # if using Playwright
# smoke test:
domishot "https://www.omie.es/es/spot-hoy" "div.market-data-block.average" -o omie.png --backend playwright
```

---

## License

MIT © Eric Moral
