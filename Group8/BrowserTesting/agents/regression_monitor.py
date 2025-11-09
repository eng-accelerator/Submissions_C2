# agents/regression_monitor.py

import os
from typing import Optional

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    Image = None
    ImageChops = None
    ImageDraw = None

BASELINE_VERSION_SUFFIX = "_baseline_v2.png"
DIFF_VERSION_SUFFIX = "_diff_v2.png"


def _baseline_path(baseline_dir: str, key: str) -> str:
    return os.path.join(baseline_dir, f"{key}{BASELINE_VERSION_SUFFIX}")


def _diff_path(baseline_dir: str, key: str) -> str:
    return os.path.join(baseline_dir, f"{key}{DIFF_VERSION_SUFFIX}")


def _create_enhanced_diff(base_img, curr_img, diff_img, diff_path):
    """
    Create a visually enhanced diff image with red highlighting for changes.
    """
    try:
        result = curr_img.convert("RGBA").copy()
        width, height = result.size
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        if ImageDraw:
            diff_gray = diff_img.convert("L")
            pixels = diff_gray.load()
            
            changed_pixels = 0
            for y in range(height):
                for x in range(width):
                    if pixels[x, y] > 10:
                        overlay.putpixel((x, y), (255, 0, 0, 150))
                        changed_pixels += 1
            
            print(f"[Visual Check] Enhanced diff: {changed_pixels} changed pixels detected")
            result = Image.alpha_composite(result, overlay)
        else:
            diff_enhanced = diff_img.point(lambda p: 255 if p > 10 else 0)
            result = diff_enhanced.convert("RGBA")
        
        result.save(diff_path)
        return True
    except Exception as e:
        print(f"Warning: Could not create enhanced diff: {e}")
        try:
            diff_img.save(diff_path)
            return True
        except Exception:
            return False


def run_visual_check(
    test_id: str,
    screenshot_path: str,
    baseline_dir: str = "screenshots",
    diff_threshold: float = 0.001,
    baseline_id: Optional[str] = None,
    create_baseline_only: bool = False,
):
    print(f"\n{'='*70}")
    print(f"[Visual Check] STARTING VISUAL REGRESSION CHECK")
    print(f"[Visual Check] test_id={test_id}")
    print(f"[Visual Check] baseline_id={baseline_id}")
    print(f"[Visual Check] create_baseline_only={create_baseline_only}")
    print(f"[Visual Check] diff_threshold={diff_threshold} ({diff_threshold*100}%)")
    print(f"{'='*70}")
    
    if not screenshot_path or not os.path.exists(screenshot_path):
        print(f"[Visual Check] ERROR: Screenshot not found at {screenshot_path}")
        return {
            "status": "unavailable",
            "message": "No screenshot found for visual regression check.",
            "baseline_path": None,
            "diff_path": None,
        }

    os.makedirs(baseline_dir, exist_ok=True)

    baseline_key = baseline_id or test_id
    baseline_path = _baseline_path(baseline_dir, baseline_key)
    diff_path = _diff_path(baseline_dir, test_id)

    print(f"[Visual Check] Baseline path: {baseline_path}")
    print(f"[Visual Check] Baseline exists: {os.path.exists(baseline_path)}")

    # Mode 1: Force baseline creation
    if create_baseline_only:
        print(f"[Visual Check] MODE: Force baseline creation (create_baseline_only=True)")
        try:
            if Image is not None:
                with Image.open(screenshot_path) as img:
                    img.convert("RGBA").save(baseline_path)
            else:
                with open(screenshot_path, "rb") as src, open(baseline_path, "wb") as dst:
                    dst.write(src.read())
            print(f"[Visual Check] ✓ Baseline created at {baseline_path}")
            return {
                "status": "baseline_created",
                "message": "Baseline screenshot captured/updated for visual regression.",
                "baseline_path": baseline_path,
                "diff_path": None,
            }
        except Exception as e:
            print(f"[Visual Check] ✗ Failed to create baseline: {e}")
            return {
                "status": "unavailable",
                "message": f"Failed to save baseline screenshot: {e}",
                "baseline_path": None,
                "diff_path": None,
            }

    if Image is None or ImageChops is None:
        print(f"[Visual Check] ERROR: Pillow not available")
        if not os.path.exists(baseline_path):
            return {
                "status": "unavailable",
                "message": "Baseline screenshot not found and Pillow is not available.",
                "baseline_path": None,
                "diff_path": None,
            }
        return {
            "status": "unavailable",
            "message": "Baseline exists but Pillow is not installed.",
            "baseline_path": baseline_path,
            "diff_path": None,
        }

    # Mode 2: Explicit comparison (baseline_id is set)
    if baseline_id is not None:
        print(f"[Visual Check] MODE: Explicit comparison (baseline_id={baseline_id})")
        if not os.path.exists(baseline_path):
            print(f"[Visual Check] ✗ Baseline not found at {baseline_path}")
            return {
                "status": "unavailable",
                "message": f"Baseline screenshot not found. Please run the baseline scenario first.",
                "baseline_path": None,
                "diff_path": None,
            }
        print(f"[Visual Check] ✓ Baseline found, proceeding to comparison")

    # Mode 3: Self-baseline (baseline_id is None and create_baseline_only is False)
    elif not os.path.exists(baseline_path):
        print(f"[Visual Check] MODE: Self-baseline - No baseline exists, creating one")
        try:
            with Image.open(screenshot_path) as img:
                img.convert("RGBA").save(baseline_path)
            print(f"[Visual Check] ✓ Baseline created at {baseline_path}")
            return {
                "status": "baseline_created",
                "message": "Baseline screenshot captured for future visual regression checks.",
                "baseline_path": baseline_path,
                "diff_path": None,
            }
        except Exception as e:
            print(f"[Visual Check] ✗ Failed to create baseline: {e}")
            return {
                "status": "unavailable",
                "message": f"Failed to save baseline screenshot: {e}",
                "baseline_path": None,
                "diff_path": None,
            }
    else:
        print(f"[Visual Check] MODE: Self-baseline - Baseline exists, comparing")

    # Perform comparison
    print(f"\n[Visual Check] PERFORMING COMPARISON")
    print(f"[Visual Check] Baseline: {baseline_path}")
    print(f"[Visual Check] Current:  {screenshot_path}")
    
    try:
        with Image.open(baseline_path) as base_img, Image.open(screenshot_path) as curr_img:
            base = base_img.convert("RGBA")
            curr = curr_img.convert("RGBA")

            print(f"[Visual Check] Baseline size: {base.size}")
            print(f"[Visual Check] Current size:  {curr.size}")

            # CRITICAL FIX: Don't resize - treat size difference as a visual regression failure
            if base.size != curr.size:
                print(f"[Visual Check] ✗ SIZE MISMATCH DETECTED - This is a visual regression!")
                print(f"[Visual Check] Baseline: {base.size[0]}x{base.size[1]} pixels")
                print(f"[Visual Check] Current:  {curr.size[0]}x{curr.size[1]} pixels")
                
                # Create a side-by-side comparison image
                try:
                    max_width = max(base.size[0], curr.size[0])
                    total_height = base.size[1] + curr.size[1]
                    comparison = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))
                    comparison.paste(base, (0, 0))
                    comparison.paste(curr, (0, base.size[1]))
                    comparison.save(diff_path)
                    print(f"[Visual Check] Side-by-side comparison saved to: {diff_path}")
                except Exception as e:
                    print(f"[Visual Check] Could not create comparison image: {e}")
                    diff_path = None
                
                return {
                    "status": "failed",
                    "message": f"Visual regression check FAILED: Image size mismatch. Baseline: {base.size[0]}x{base.size[1]}, Current: {curr.size[0]}x{curr.size[1]}",
                    "baseline_path": baseline_path,
                    "diff_path": diff_path,
                }

            # Calculate pixel differences
            diff = ImageChops.difference(base, curr)
            bbox = diff.getbbox()

            if not bbox:
                print(f"[Visual Check] ✓ No differences found (bbox is None)")
                return {
                    "status": "passed",
                    "message": "Visual regression check passed (no pixel differences).",
                    "baseline_path": baseline_path,
                    "diff_path": None,
                }

            print(f"[Visual Check] Difference bounding box: {bbox}")

            # Calculate difference ratio
            hist = diff.convert("L").histogram()
            non_zero = sum(c for i, c in enumerate(hist) if i > 0)
            total = sum(hist)
            ratio = (non_zero / float(total)) if total else 0.0

            print(f"[Visual Check] Total pixels: {total:,}")
            print(f"[Visual Check] Changed pixels: {non_zero:,}")
            print(f"[Visual Check] Difference ratio: {ratio:.6%}")
            print(f"[Visual Check] Threshold: {diff_threshold:.6%}")
            print(f"[Visual Check] Result: {'PASS' if ratio <= diff_threshold else 'FAIL'}")

            # Create enhanced diff visualization
            diff_created = _create_enhanced_diff(base, curr, diff, diff_path)
            final_diff_path = diff_path if diff_created else None

            if ratio <= diff_threshold:
                print(f"[Visual Check] ✓ PASSED - Differences within threshold")
                return {
                    "status": "passed",
                    "message": f"Visual regression check passed ({ratio:.4%} of pixels differ, within threshold {diff_threshold:.4%}).",
                    "baseline_path": baseline_path,
                    "diff_path": final_diff_path,
                }
            else:
                print(f"[Visual Check] ✗ FAILED - Differences exceed threshold")
                print(f"[Visual Check] Diff image saved to: {final_diff_path}")
                return {
                    "status": "failed",
                    "message": f"Visual regression check FAILED ({ratio:.4%} of pixels differ; threshold {diff_threshold:.4%}).",
                    "baseline_path": baseline_path,
                    "diff_path": final_diff_path,
                }
    except Exception as e:
        print(f"[Visual Check] ✗ ERROR during comparison: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "unavailable",
            "message": f"Visual regression comparison error: {e}",
            "baseline_path": baseline_path if os.path.exists(baseline_path) else None,
            "diff_path": None,
        }


__all__ = ["run_visual_check"]