"""Processing utilities for cua-bench batch outputs.

Implements 'aguvis' processor that converts a folder of
batch dump outputs into a Hugging Face dataset-like structure.

Each task: expects files like:
- task_<id>_screenshot.png
- task_<id>_snapshot.html

Rows schema per request:
- images: [screenshot_path]
- texts: list of {assistant: str, user: str}
- source: "cua-bench"

Supports:
- Save to disk (JSONL)
- Push to Hugging Face Hub (if `datasets` installed and auth available)
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

from bs4 import BeautifulSoup
import html as _html
import re
from tqdm.auto import tqdm


@dataclass
class ProcessArgs:
    outputs_path: Path
    mode: str = "aguvis"
    dataset_name: str | None = None
    save_dir: Path | None = None
    push_to_hub: bool = False
    repo_id: str | None = None
    private: bool = False
    max_samples: int | None = None


def _find_task_pairs(outputs_path: Path) -> List[Tuple[Path, Path, int]]:
    pairs: List[Tuple[Path, Path, int]] = []
    # Find all snapshot files and look for matching screenshot
    for snap in sorted(outputs_path.glob("task_*_snapshot.html")):
        # extract id
        try:
            tid = int(snap.stem.split("_")[1])
        except Exception:
            continue
        shot = snap.with_name(f"task_{tid}_screenshot.png")
        if shot.exists():
            pairs.append((shot, snap, tid))
    return pairs


def _extract_instructions_with_bbox(snapshot_html: str) -> List[Tuple[str, Dict[str, float]]]:
    """Return list of (instruction_text, bbox) with bbox from data-bbox-* on the element.

    bbox keys: x, y, width, height (floats)
    """
    soup = BeautifulSoup(snapshot_html, "html5lib")
    items: List[Tuple[str, Dict[str, float]]] = []
    seen = set()
    for tag in soup.find_all(attrs={"data-instruction": True}):
        val = tag.get("data-instruction")
        if not isinstance(val, str):
            continue
        text = val.strip()
        if not text:
            continue
        # Require center-hit to be true
        if tag.get("data-bbox-center-hit") != 'true':
            continue
        # Extract bbox from this tag if present
        try:
            x = float(tag.get("data-bbox-x"))
            y = float(tag.get("data-bbox-y"))
            w = float(tag.get("data-bbox-width"))
            h = float(tag.get("data-bbox-height"))
            bbox = {"x": x, "y": y, "width": w, "height": h}
        except (TypeError, ValueError):
            # Skip items without bbox
            continue
        if text not in seen:
            items.append((text, bbox))
            seen.add(text)
    return items


def _extract_aria_with_bbox(snapshot_html: str) -> List[Tuple[str, Dict[str, float]]]:
    """Return list of (aria-label, bbox) for elements that have aria-label and bbox."""
    soup = BeautifulSoup(snapshot_html, "html5lib")
    out: List[Tuple[str, Dict[str, float]]] = []
    seen = set()
    for tag in soup.find_all(attrs={"aria-label": True}):
        val = tag.get("aria-label")
        if not isinstance(val, str):
            continue
        label = val.strip()
        if not label:
            continue
        if tag.get("data-bbox-center-hit") != 'true':
            continue
        try:
            x = float(tag.get("data-bbox-x"))
            y = float(tag.get("data-bbox-y"))
            w = float(tag.get("data-bbox-width"))
            h = float(tag.get("data-bbox-height"))
            bbox = {"x": x, "y": y, "width": w, "height": h}
        except (TypeError, ValueError):
            continue
        key = (label, x, y, w, h)
        if key in seen:
            continue
        out.append((label, bbox))
        seen.add(key)
    return out


def _extract_actions(snapshot_html: str) -> List[Dict[str, str]]:
    """Extract pre-defined action pairs from any element's data-actions JSON.

    Looks for attributes `data-actions` on all elements. Each attribute should be
    a JSON array of objects with string fields 'user' and 'assistant'.
    """
    soup = BeautifulSoup(snapshot_html, "html5lib")
    out: List[Dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for el in soup.find_all(attrs={"data-actions": True}):
        val = el.get("data-actions")
        if not isinstance(val, str) or not val.strip():
            continue
        try:
            data = json.loads(val)
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            u = item.get("user")
            a = item.get("assistant")
            if isinstance(u, str) and isinstance(a, str) and u and a:
                key = (u, a)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"user": u, "assistant": a})
    return out


def _extract_text_with_bbox(snapshot_html: str, min_len: int = 3, max_len: int = 80) -> List[Tuple[str, Dict[str, float]]]:
    """Return list of (text_content, bbox) for elements with textual content and bbox.

    We associate the text with the nearest ancestor element that has data-bbox-*,
    or the element itself if it already has bbox attributes.
    """
    soup = BeautifulSoup(snapshot_html, "html5lib")
    out: List[Tuple[str, Dict[str, float]]] = []
    seen = set()
    # Iterate elements (not raw NavigableStrings) to access attributes
    for el in soup.find_all(True):
        # Only consider elements with no element children (leaf nodes)
        if el.find(True, recursive=False) is not None:
            continue
        txt = el.get_text(strip=True)
        if not txt:
            continue
        # Normalize whitespace
        txt = " ".join(txt.split())
        if len(txt) < min_len or len(txt) > max_len:
            continue
        # Find bbox on this element or its ancestor
        cur = el
        bbox = None
        while cur is not None:
            try:
                x = float(cur.get("data-bbox-x"))
                y = float(cur.get("data-bbox-y"))
                w = float(cur.get("data-bbox-width"))
                h = float(cur.get("data-bbox-height"))
                bbox = {"x": x, "y": y, "width": w, "height": h}
                # Require that the center hits the element bearing the bbox
                if cur.get("data-bbox-center-hit") != 'true':
                    bbox = None
                break
            except (TypeError, ValueError):
                cur = cur.parent if hasattr(cur, "parent") else None
        if not bbox:
            continue
        key = (txt, bbox["x"], bbox["y"], bbox["width"], bbox["height"])
        if key in seen:
            continue
        out.append((txt, bbox))
        seen.add(key)
    return out

def _center_from_bbox(bbox: Dict[str, float]) -> Tuple[float, float]:
    return bbox["x"] + bbox["width"] / 2.0, bbox["y"] + bbox["height"] / 2.0


def _build_augmented_texts(
    instr_items: List[Tuple[str, Dict[str, float]]],
    aria_items: List[Tuple[str, Dict[str, float]]],
    text_items: List[Tuple[str, Dict[str, float]]],
    shot_path: Path,
    n: int = 5,
    action_items: List[Dict[str, str]] | None = None,
) -> List[Dict[str, str]]:
    """Build texts following the requested action augmentations mapping.

    User prompts:
      - "Double-click to '{*[data-instruction]}'"
      - "Right-click to '{*[data-instruction]}'"
      - "Click to '{*[data-instruction]}'"
      - "Move to '{*[data-instruction]}'"

      - "Double-click the '{*[aria-label]}'"
      - "Right-click the '{*[aria-label]}'"
      - "Click the '{*[aria-label]}'"
      - "Move to the '{*[aria-label]}'"

      - "Double-click the text '{*[.. text content ..]}'"
      - "Right-click the text '{*[.. text content ..]}'"
      - "Click the text '{*[.. text content ..]}'"
      - "Move to the text '{*[.. text content ..]}'"

    Assistant (normalized coords):
      - double_click(x=.., y=..)
      - right_click(x=.., y=..)
      - click(x=.., y=..)
      - move_mouse(x=.., y=..)
    """
    verbs_to = [("Double-click to", "double_click"), ("Right-click to", "right_click"), ("Click to", "click"), ("Move to", "move_mouse")]
    verbs_the = [("Double-click the", "double_click"), ("Right-click the", "right_click"), ("Click the", "click"), ("Move to the", "move_mouse")]
    verbs_at = [("Double-click the text", "double_click"), ("Right-click the text", "right_click"), ("Click the text", "click"), ("Move to the text", "move_mouse")]
    out: List[Dict[str, str]] = []

    # Compute image size once
    from PIL import Image  # type: ignore
    with Image.open(shot_path) as im:
        W, H = im.size
        px = im.load()

        def _shrink_bbox_to_content(b: Dict[str, float]) -> Dict[str, float] | None:
            # Convert to integer box within image bounds
            x = max(0, min(int(round(b.get("x", 0))), W - 1))
            y = max(0, min(int(round(b.get("y", 0))), H - 1))
            w = max(1, int(round(b.get("width", 0))))
            h = max(1, int(round(b.get("height", 0))))
            if x + w > W:
                w = max(1, W - x)
            if y + h > H:
                h = max(1, H - y)
            if w < 2 or h < 2:
                return None

            # Helper comparators
            def col_equal(c0: int, c1: int) -> bool:
                for yy in range(y, y + h):
                    if px[c0, yy] != px[c1, yy]:
                        return False
                return True

            def row_equal(r0: int, r1: int) -> bool:
                for xx in range(x, x + w):
                    if px[xx, r0] != px[xx, r1]:
                        return False
                return True

            # Left
            while w > 2 and x + 1 < W and col_equal(x, x + 1):
                x += 1
                w -= 1
            # Top
            while h > 2 and y + 1 < H and row_equal(y, y + 1):
                y += 1
                h -= 1
            # Right
            while w > 2 and x + w - 1 < W and x + w - 2 >= 0 and col_equal(x + w - 1, x + w - 2):
                w -= 1
            # Bottom
            while h > 2 and y + h - 1 < H and y + h - 2 >= 0 and row_equal(y + h - 1, y + h - 2):
                h -= 1

            if w < 2 or h < 2:
                return None
            return {"x": float(x), "y": float(y), "width": float(w), "height": float(h)}

    # Prepare filtered pools: only keep items with normalized centers strictly inside (0,1)
    def to_pool(items: List[Tuple[str, Dict[str, float]]], *, shrink: bool = False) -> List[Tuple[str, float, float]]:
        pool: List[Tuple[str, float, float]] = []
        for ref, bbox in items:
            if bbox.get("x", 0) <= 0.0 or bbox.get("y", 0) <= 0.0 or bbox.get("width", 0) >= W or bbox.get("height", 0) >= H:
                continue
                
            if shrink:
                sb = _shrink_bbox_to_content(bbox)
                if not sb:
                    continue
                cx, cy = _center_from_bbox(sb)
            else:
                cx, cy = _center_from_bbox(bbox)
            nx = round(min(max(cx / W, 0.0), 1.0), 4)
            ny = round(min(max(cy / H, 0.0), 1.0), 4)
            if 0.0 < nx < 1.0 and 0.0 < ny < 1.0:
                pool.append((ref, nx, ny))
        return pool

    instr_pool = to_pool(instr_items, shrink=False)
    aria_pool = to_pool(aria_items, shrink=False)
    text_pool = to_pool(text_items, shrink=True)

    # Prepare action pool (pre-defined pairs), normalizing any pixel coords to normalized [0,1]
    action_pool: List[Tuple[str, str]] = []
    if action_items:
        # We have W, H from above
        import re as _re
        click_xy = _re.compile(r"x=([0-9.]+)\s*,\s*y=([0-9.]+)")
        drag_xy = _re.compile(r"drag\(.*?from_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\]\s*,\s*to_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\].*?\)")
        def _norm_val(v: float, denom: float) -> float:
            # If v > 1, treat as pixels; else assume already normalized
            if v > 1.0:
                return round(min(max(v / denom, 0.0), 1.0), 4)
            return round(min(max(v, 0.0), 1.0), 4)
        for item in action_items:
            u = item.get("user") if isinstance(item, dict) else None
            a = item.get("assistant") if isinstance(item, dict) else None
            if not (isinstance(u, str) and isinstance(a, str) and u and a):
                continue
            # Normalize click x=, y=
            m = click_xy.search(a)
            if m:
                x = float(m.group(1)); y = float(m.group(2))
                nx = _norm_val(x, W); ny = _norm_val(y, H)
                if not (0.0 < nx < 1.0 and 0.0 < ny < 1.0):
                    continue
                a = click_xy.sub(f"x={nx}, y={ny}", a)
                action_pool.append((u, a))
                continue
            # Normalize drag from/to coords
            m = drag_xy.search(a)
            if m:
                fx = float(m.group(1)); fy = float(m.group(2)); tx = float(m.group(3)); ty = float(m.group(4))
                nfx = _norm_val(fx, W); nfy = _norm_val(fy, H)
                ntx = _norm_val(tx, W); nty = _norm_val(ty, H)
                # Require both endpoints inside (0,1)
                if not (0.0 < nfx < 1.0 and 0.0 < nfy < 1.0 and 0.0 < ntx < 1.0 and 0.0 < nty < 1.0):
                    continue
                a = drag_xy.sub(
                    f"drag(from_coord=[{nfx},{nfy}], to_coord=[{ntx},{nty}])",
                    a,
                )
                action_pool.append((u, a))
                continue
            # If no coords found, keep as-is
            action_pool.append((u, a))

    attempts = 0
    max_attempts = max(n * 10, 50)
    while len(out) < n and attempts < max_attempts:
        attempts += 1
        # Include 'action' pool if available
        choices = ["to", "the", "at"] + (["action"] if action_pool else [])
        pool_choice = random.choice(choices)  # equal probability among available pools
        if pool_choice == "to":
            if not instr_pool:
                continue
            ref, nx, ny = random.choice(instr_pool)
            verb_text, act = random.choice(verbs_to)
        elif pool_choice == "the":
            if not aria_pool:
                continue
            ref, nx, ny = random.choice(aria_pool)
            verb_text, act = random.choice(verbs_the)
        elif pool_choice == "at":
            if not text_pool:
                continue
            ref, nx, ny = random.choice(text_pool)
            verb_text, act = random.choice(verbs_at)
        else:
            # Pre-defined action pair; use as-is
            if not action_pool:
                continue
            u, a = random.choice(action_pool)
            out.append({"assistant": a, "user": u})
            continue

        user = f"{verb_text} '{ref}'" if ref else verb_text
        assistant = f"{act}(x={nx}, y={ny})"
        out.append({"assistant": assistant, "user": user})

    # Deduplicate by hash(user + assistant) while preserving order
    seen_keys = set()
    unique: List[Dict[str, str]] = []
    for pair in out:
        u = str(pair.get("user", ""))
        a = str(pair.get("assistant", ""))
        key = u + "\u241F" + a  # use an unlikely separator
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(pair)
    return unique


def _save_jsonl(rows: List[Dict[str, Any]], save_dir: Path, dataset_name: str) -> Path:
    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / f"{dataset_name}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out_path


def _push_to_hub(rows: List[Dict[str, Any]], repo_id: str, private: bool) -> None:
    from datasets import Dataset, Features, Value, Sequence
    from datasets.features import Image
    from PIL import Image as PILImage

    # Build dataset
    data = {
        "images": [[PILImage.open(img) for img in r["images"]] for r in rows],
        "texts": [r["texts"] for r in rows],
        "source": [r["source"] for r in rows],
    }
    # # Define features: images as a sequence of Image, texts as a sequence of structs
    # features = Features({
    #     "images": Sequence(Image()),
    #     "texts": Sequence({
    #         "assistant": Value("string"),
    #         "user": Value("string"),
    #     }),
    #     "source": Value("string"),
    # })

    ds = Dataset.from_dict(data)

    # Push to hub
    ds.push_to_hub(repo_id, private=private)


def execute(args) -> None:
    # Normalize args into ProcessArgs
    pargs = ProcessArgs(
        outputs_path=Path(args.outputs_path).expanduser().resolve(),
        mode=args.mode or "aguvis",
        dataset_name=args.dataset_name,
        save_dir=Path(args.save_dir).expanduser().resolve() if args.save_dir else None,
        push_to_hub=bool(args.push_to_hub),
        repo_id=args.repo_id,
        private=bool(args.private),
        max_samples=args.max_samples,
    )

    if not pargs.outputs_path.exists():
        raise SystemExit(f"Outputs path not found: {pargs.outputs_path}")
    if pargs.mode != "aguvis":
        raise SystemExit(f"Unsupported mode: {pargs.mode}")

    pairs = _find_task_pairs(pargs.outputs_path)
    if pargs.max_samples is not None:
        pairs = pairs[: pargs.max_samples]

    rows: List[Dict[str, Any]] = []
    for shot, snap, tid in tqdm(pairs, desc="Processing", unit="task"):
        # Seed for reproducibility per task
        random.seed(tid)
        snapshot_html = snap.read_text(encoding="utf-8", errors="ignore")
        action_items = _extract_actions(snapshot_html)
        instr_items = _extract_instructions_with_bbox(snapshot_html)
        aria_items = _extract_aria_with_bbox(snapshot_html)
        text_items = _extract_text_with_bbox(snapshot_html)
        texts = _build_augmented_texts(
            instr_items, aria_items, text_items, shot, n=5, action_items=action_items
        )
        row = {
            "images": [str(shot)],
            "texts": texts,
            "source": "cua-bench",
        }
        rows.append(row)

    # Build previews (first 50)
    def _write_previews(rows: List[Dict[str, Any]], base_dir: Path, limit: int = 50) -> Path:
        preview_dir = base_dir / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        index_path = preview_dir / "index.html"
        # Simple stylesheet and per-sample block
        parts: List[str] = []
        parts.append("<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>cua-bench Previews</title>")
        parts.append(
            "<style>\n"
            ".item{margin:16px 0;padding:12px;border:1px solid #ddd;border-radius:8px;}\n"
            ".frame{position:relative;display:inline-block;}\n"
            ".frame img{display:block;max-width:100%;height:auto;}\n"
            ".cross{position:absolute;width:24px;height:24px;margin-left:-12px;margin-top:-12px;pointer-events:none;}\n"
            ".cross:before,.cross:after{content:'';position:absolute;background:red;}\n"
            ".cross:before{left:50%;top:0;bottom:0;width:2px;transform:translateX(-50%);}\n"
            ".cross:after{top:50%;left:0;right:0;height:2px;transform:translateY(-50%);}\n"
            ".cross.half-left:after{left:0;right:50%;}\n"
            ".cross.half-right:after{left:50%;right:0;}\n"
            ".cross .num{position:absolute;top:-16px;left:10px;background:red;color:#fff;font:600 12px/12px ui-monospace,Menlo,monospace;padding:2px 4px;border-radius:10px;}\n"
            "pre{background:#f7f7f7;padding:8px;border-radius:6px;overflow:auto;white-space:pre-wrap;}\n"
            "</style></head><body>\n<h1>cua-bench Previews</h1>\n"
        )
        xy_re = re.compile(r"x=([0-9.]+)\s*,\s*y=([0-9.]+)")
        drag_re = re.compile(r"drag\(.*?from_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\]\s*,\s*to_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\].*?\)")
        for i, r in enumerate(rows[:limit]):
            img_list = r.get("images", [])
            if not img_list:
                continue
            img_path = str(img_list[0])
            texts = r.get("texts", [])
            # Open image size for potential pixel->normalized conversion
            try:
                from PIL import Image as _PIL
                with _PIL.open(img_path) as _im:
                    _W, _H = _im.size
            except Exception:
                _W, _H = (1, 1)
            # Prepare markers list; entries can be single point or drag endpoints
            # Markers format: (idx, x, y, user, assistant, cls)
            markers = []
            for idx, pair in enumerate(texts, start=1):
                user = str(pair.get("user", ""))
                assistant = str(pair.get("assistant", ""))
                md = drag_re.search(assistant)
                if md:
                    fx = float(md.group(1)); fy = float(md.group(2)); tx = float(md.group(3)); ty = float(md.group(4))
                    # Normalize if pixel-like
                    def _n(v, d):
                        return v / d if v > 1.0 else v
                    nfx, nfy = _n(fx, _W), _n(fy, _H)
                    ntx, nty = _n(tx, _W), _n(ty, _H)
                    # Clamp to [0,1]
                    nfx = min(max(nfx, 0.0), 1.0); nfy = min(max(nfy, 0.0), 1.0)
                    ntx = min(max(ntx, 0.0), 1.0); nty = min(max(nty, 0.0), 1.0)
                    markers.append((idx, nfx, nfy, user, assistant, "half-left"))
                    markers.append((idx, ntx, nty, user, assistant, "half-right"))
                else:
                    m = xy_re.search(assistant)
                    if m:
                        x = float(m.group(1)); y = float(m.group(2))
                        # Normalize if pixel-like
                        x = x / _W if x > 1.0 else x
                        y = y / _H if y > 1.0 else y
                    else:
                        raise ValueError(f"Invalid action: {assistant}")
                    # Clamp
                    x = min(max(x, 0.0), 1.0); y = min(max(y, 0.0), 1.0)
                    markers.append((idx, x, y, user, assistant, ""))
            # Build block
            parts.append('<div class="item">')
            parts.append('<div class="frame">')
            parts.append(f'<img src="file://{_html.escape(img_path)}" alt="preview_{i}">')
            for idx, x, y, user, assistant, cls in markers:
                cls_attr = f" cross {cls}" if cls else " cross"
                parts.append(f'<div class="{cls_attr}" style="left:{x*100:.2f}%; top:{y*100:.2f}%;"><div class="num">{idx}</div></div>')
            parts.append('</div>')
            parts.append('<pre>')
            # Dump all pairs, appending [idx] to assistant
            for idx, _, _, user, assistant, cls in markers:
                if cls == "half-left":
                    continue
                parts.append(f'user: {_html.escape(user)}')
                parts.append(f'assistant: {_html.escape(assistant)} [{idx}]')
                if idx != len(markers):
                    parts.append('')
            parts.append('</pre>')
            parts.append('</div>')
        parts.append("</body></html>")
        index_path.write_text("\n".join(parts), encoding="utf-8")
        return index_path

    def _write_preview_gif(
        rows: List[Dict[str, Any]],
        base_dir: Path,
        *,
        limit: int = 50,
        fps: int = 1,
        size: Tuple[int, int] = (640, 360),
    ) -> Path:
        """Create a single GIF preview of the first N tasks.

        - Canvas: size (e.g., 1280x720)
        - Left: screenshot placed inside the entire remaining content area (left of sidebar)
        - Right: sidebar with user/assistant texts
        - Crosshair markers drawn over screenshot using normalized coords parsed from assistant
        - 1 frame per task, up to `limit`; saved at `fps`.
        """
        from PIL import Image as _PIL_Image  # type: ignore
        from PIL import ImageDraw as _PIL_Draw  # type: ignore
        from PIL import ImageFont as _PIL_Font  # type: ignore
        import textwrap as _textwrap
        import math as _math
        import re as _re

        preview_dir = base_dir / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        gif_path = preview_dir / "preview.gif"

        W, H = size
        # Layout: reserve a sidebar on the right
        sidebar_w = 200
        content_w = W - sidebar_w
        content_h = H
        # Use the full content area for the screenshot box
        box_w = content_w
        box_h = content_h
        box_x = 0
        box_y = 0

        # Regex to parse actions
        xy_re = _re.compile(r"x=([0-9.]+)\s*,\s*y=([0-9.]+)")
        drag_re = _re.compile(r"drag\(.*?from_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\]\s*,\s*to_coord=\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\].*?\)")

        frames: List[_PIL_Image.Image] = []
        # Try to load a default font; fall back to basic if unavailable
        try:
            font = _PIL_Font.load_default()
        except Exception:
            font = None

        for i, r in enumerate(rows[:limit]):
            img_list = r.get("images", [])
            if not img_list:
                continue
            img_path = str(img_list[0])
            texts = r.get("texts", [])

            # Base canvas
            frame = _PIL_Image.new("RGB", (W, H), (255, 255, 255))
            draw = _PIL_Draw.Draw(frame)

            # Load screenshot and fit into 16:9 box while preserving aspect (letterbox in box)
            try:
                shot = _PIL_Image.open(img_path).convert("RGB")
            except Exception:
                # If image missing, leave blank area
                shot = _PIL_Image.new("RGB", (box_w, box_h), (240, 240, 240))
            sW, sH = shot.size
            # Scale to fit inside box_w x box_h
            scale = min(box_w / sW, box_h / sH)
            new_w = max(1, int(round(sW * scale)))
            new_h = max(1, int(round(sH * scale)))
            shot_resized = shot.resize((new_w, new_h), _PIL_Image.BICUBIC)
            # Paste centered in the 16:9 box region
            paste_x = box_x + (box_w - new_w) // 2
            paste_y = box_y + (box_h - new_h) // 2
            frame.paste(shot_resized, (paste_x, paste_y))

            # Determine normalized->pixel mapping inside the pasted image
            def norm_to_px(nx: float, ny: float) -> Tuple[int, int]:
                nx = min(max(nx, 0.0), 1.0)
                ny = min(max(ny, 0.0), 1.0)
                return paste_x + int(round(nx * (new_w - 1))), paste_y + int(round(ny * (new_h - 1)))

            # Collect markers as in HTML preview
            markers: List[Tuple[int, float, float, str, str, str]] = []
            # Open original size to normalize from pixel-like values
            _W, _H = (sW, sH)
            for idx, pair in enumerate(texts, start=1):
                user = str(pair.get("user", ""))
                assistant = str(pair.get("assistant", ""))
                md = drag_re.search(assistant)
                if md:
                    fx = float(md.group(1)); fy = float(md.group(2)); tx = float(md.group(3)); ty = float(md.group(4))
                    def _n(v, d):
                        return v / d if v > 1.0 else v
                    nfx, nfy = _n(fx, _W), _n(fy, _H)
                    ntx, nty = _n(tx, _W), _n(ty, _H)
                    nfx = min(max(nfx, 0.0), 1.0); nfy = min(max(nfy, 0.0), 1.0)
                    ntx = min(max(ntx, 0.0), 1.0); nty = min(max(nty, 0.0), 1.0)
                    markers.append((idx, nfx, nfy, user, assistant, "half-left"))
                    markers.append((idx, ntx, nty, user, assistant, "half-right"))
                else:
                    m = xy_re.search(assistant)
                    if m:
                        x = float(m.group(1)); y = float(m.group(2))
                        x = x / _W if x > 1.0 else x
                        y = y / _H if y > 1.0 else y
                    else:
                        raise ValueError(f"Invalid action: {assistant}")
                    x = min(max(x, 0.0), 1.0); y = min(max(y, 0.0), 1.0)
                    markers.append((idx, x, y, user, assistant, ""))

            # Draw crosshair helper
            def draw_cross(px: int, py: int, idx: int, cls: str = "") -> None:
                size = 16
                color = (220, 30, 30)
                # vertical
                draw.line((px, py - size, px, py + size), fill=color, width=2)
                # horizontal; if half-left/right, draw only half
                if cls == "half-left":
                    draw.line((px - size, py, px, py), fill=color, width=2)
                elif cls == "half-right":
                    draw.line((px, py, px + size, py), fill=color, width=2)
                else:
                    draw.line((px - size, py, px + size, py), fill=color, width=2)
                # index badge
                badge_text = str(idx)
                bx, by = px + 8, py - 20
                draw.rectangle((bx - 2, by - 10, bx + 12, by + 4), fill=color)
                if font:
                    draw.text((bx, by - 8), badge_text, fill=(255, 255, 255), font=font)

            for idx, nx, ny, user, assistant, cls in markers:
                px, py = norm_to_px(nx, ny)
                draw_cross(px, py, idx, cls)

            # Sidebar background
            sidebar_x0 = content_w
            draw.rectangle((sidebar_x0, 0, W, H), fill=(245, 245, 245))
            # Title and texts
            pad = 12
            tx = sidebar_x0 + pad
            ty = pad
            if font:
                draw.text((tx, ty), f"Task {i+1}", fill=(0, 0, 0), font=font)
            ty += 18

            # Wrap user/assistant pairs; skip half-left duplicates
            listed = set()
            for idx, _, _, user, assistant, cls in markers:
                if cls == "half-left":
                    continue
                if idx in listed:
                    continue
                listed.add(idx)
                # user line
                u_lines = _textwrap.wrap(f"user: {user}", width=46)
                a_lines = _textwrap.wrap(f"assistant: {assistant} [{idx}]", width=46)
                for line in u_lines:
                    if font:
                        draw.text((tx, ty), line, fill=(20, 20, 20), font=font)
                    ty += 14
                for line in a_lines:
                    if font:
                        draw.text((tx, ty), line, fill=(20, 20, 20), font=font)
                    ty += 16
                ty += 6

            frames.append(frame)

        if not frames:
            return gif_path

        # Duration per frame in ms for requested fps
        duration_ms = int(round(1000 / max(1, fps)))
        try:
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration_ms,
                loop=0,
                optimize=False,
                disposal=2,
            )
        except Exception:
            # Try without disposal/optimize for compatibility
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration_ms,
                loop=0,
            )
        return gif_path

    # Save or push as requested
    ds_name = pargs.dataset_name or f"td_{pargs.mode}_dataset"

    if pargs.save_dir:
        out = _save_jsonl(rows, pargs.save_dir, ds_name)
        print(f"Saved JSONL dataset to: {out}")
        # Previews next to save_dir
        prev = _write_previews(rows, pargs.save_dir)
        print(f"Saved HTML preview to: {prev}")
        gif = _write_preview_gif(rows, pargs.save_dir, limit=50)
        print(f"Saved GIF preview to: {gif}")

    if pargs.push_to_hub:
        if not pargs.repo_id:
            raise SystemExit("--repo-id is required when --push-to-hub is set (e.g., username/repo)")
        _push_to_hub(rows, pargs.repo_id, pargs.private)
        print(f"Pushed dataset to hub: {pargs.repo_id} (private={pargs.private})")

    if not pargs.save_dir and not pargs.push_to_hub:
        # Default: save beside outputs
        default_dir = pargs.outputs_path / "processed"
        out = _save_jsonl(rows, default_dir, ds_name)
        print(f"Saved JSONL dataset to: {out}")
        prev = _write_previews(rows, default_dir)
        print(f"Saved HTML preview to: {prev}")
        gif = _write_preview_gif(rows, default_dir, limit=50)
        print(f"Saved GIF preview to: {gif}")
