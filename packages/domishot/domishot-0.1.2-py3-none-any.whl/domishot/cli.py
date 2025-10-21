from .core import capture, CaptureOptions
import argparse

def main():
    p = argparse.ArgumentParser(description="Screenshot a specific element from a web page.")
    p.add_argument("url")
    p.add_argument("selector")
    p.add_argument("--out", "-o", required=True)
    p.add_argument("--backend", choices=["auto","playwright","selenium"], default="auto")
    p.add_argument("--width", type=int, default=1400)
    p.add_argument("--height", type=int, default=1000)
    p.add_argument("--dpr", type=int, default=2)
    p.add_argument("--locale", default="es-ES")
    p.add_argument("--no-accept-cookies", action="store_true")
    p.add_argument("--timeout", type=int, default=30000)
    p.add_argument("--extra-wait", type=int, default=400)
    a = p.parse_args()
    opts = CaptureOptions(
        backend=a.backend,
        viewport=(a.width, a.height),
        device_scale_factor=a.dpr,
        locale=a.locale,
        accept_cookies=not a.no_accept_cookies,
        timeout_ms=a.timeout,
        extra_wait_ms=a.extra_wait,
    )
    capture(a.url, a.selector, a.out, opts)
    print(f"Saved -> {a.out}")
