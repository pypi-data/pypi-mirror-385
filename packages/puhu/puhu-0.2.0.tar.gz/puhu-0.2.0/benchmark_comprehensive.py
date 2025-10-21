#!/usr/bin/env python3
"""
Comprehensive Benchmark: Puhu vs Pillow
Compare all API methods and performance metrics
"""

import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

try:
    import puhu
    from puhu import Image as PuhuImage
except ImportError:
    print("❌ Error: puhu is not installed. Install with: pip install puhu")
    sys.exit(1)

try:
    from PIL import Image as PILImage
except ImportError:
    print("❌ Error: Pillow is not installed. Install with: pip install Pillow")
    sys.exit(1)


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")


def print_section(text: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'─' * 80}{Colors.ENDC}")


def benchmark_operation(func: Callable, iterations: int = 10, warmup: int = 2) -> Tuple[bool, float, str]:
    """
    Benchmark an operation with warmup
    Returns: (success, avg_time_ms, error_message)
    """
    times = []
    error = ""
    
    # Warmup runs
    for _ in range(warmup):
        try:
            func()
        except Exception as e:
            return False, 0.0, str(e)
    
    # Actual benchmark runs
    for _ in range(iterations):
        try:
            start = time.perf_counter()
            result = func()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
            # Force evaluation for lazy operations
            if result is not None and hasattr(result, 'size'):
                _ = result.size
        except Exception as e:
            return False, 0.0, str(e)
    
    if times:
        avg_time = sum(times) / len(times)
        return True, avg_time, ""
    return False, 0.0, "No data"


def get_all_pillow_methods() -> Dict[str, List[str]]:
    """Get all Pillow methods categorized by type"""
    
    # Create a sample PIL image to inspect
    pil_img = PILImage.new("RGB", (100, 100))
    
    # Get all methods
    all_methods = [m for m in dir(pil_img) if not m.startswith('_')]
    
    # Categorize methods
    categories = {
        "Core Operations": [
            "open", "save", "new", "copy", "close", "crop", "resize", "rotate", 
            "thumbnail", "transpose", "transform", "convert"
        ],
        "Pixel Access": [
            "getpixel", "putpixel", "getdata", "putdata", "getbands", "getbbox",
            "getextrema", "getcolors", "getpalette", "putpalette"
        ],
        "Image Manipulation": [
            "paste", "split", "merge", "alpha_composite", "blend", "composite",
            "eval", "point", "quantize", "remap_palette"
        ],
        "Filters & Effects": [
            "filter", "enhance", "effect_spread", "entropy", "histogram", "reduce"
        ],
        "Format & Info": [
            "load", "verify", "draft", "seek", "tell", "getchannel", "tobytes",
            "tobitmap", "toqimage", "toqpixmap"
        ],
        "Creation Methods": [
            "fromarray", "frombytes", "frombuffer", "fromstring"
        ],
        "Properties": [
            "size", "width", "height", "mode", "format", "info", "palette",
            "category", "readonly"
        ]
    }
    
    return categories


def check_module_functions():
    """Check module-level functions"""
    print_section("Module-Level Functions")
    
    functions = [
        "open", "new", "fromarray", "frombytes", "frombuffer", "merge", "blend", "composite"
    ]
    
    print(f"{Colors.BOLD}{'Function':<25} {'Pillow':<10} {'Puhu':<10} {'Status':<20}{Colors.ENDC}")
    print("─" * 65)
    
    supported = 0
    total = len(functions)
    
    for func_name in functions:
        has_pillow = hasattr(PILImage, func_name)
        has_puhu = hasattr(puhu, func_name) or hasattr(PuhuImage, func_name)
        
        pillow_mark = f"{Colors.OKGREEN}✓{Colors.ENDC}" if has_pillow else f"{Colors.FAIL}✗{Colors.ENDC}"
        puhu_mark = f"{Colors.OKGREEN}✓{Colors.ENDC}" if has_puhu else f"{Colors.FAIL}✗{Colors.ENDC}"
        
        if has_puhu:
            status = f"{Colors.OKGREEN}Supported{Colors.ENDC}"
            supported += 1
        else:
            status = f"{Colors.WARNING}Not implemented{Colors.ENDC}"
        
        print(f"{func_name:<25} {pillow_mark:<18} {puhu_mark:<18} {status}")
    
    coverage = (supported / total) * 100 if total > 0 else 0
    print(f"\n{Colors.BOLD}Coverage: {coverage:.1f}% ({supported}/{total}){Colors.ENDC}")


def check_image_methods():
    """Check Image instance methods"""
    print_section("Image Instance Methods")
    
    categories = get_all_pillow_methods()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        test_img_path = tmppath / "test.png"
        
        # Create test image
        pil_img = PILImage.new("RGB", (100, 100))
        pil_img.save(test_img_path)
        
        puhu_img = puhu.open(test_img_path)
        
        total_supported = 0
        total_methods = 0
        
        for category, methods in categories.items():
            print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
            print(f"{'Method':<25} {'Pillow':<10} {'Puhu':<10} {'Status':<20}")
            print("─" * 65)
            
            for method in methods:
                has_pillow = hasattr(pil_img, method) or hasattr(PILImage, method)
                has_puhu = hasattr(puhu_img, method) or hasattr(puhu, method)
                
                pillow_mark = f"{Colors.OKGREEN}✓{Colors.ENDC}" if has_pillow else f"{Colors.FAIL}✗{Colors.ENDC}"
                puhu_mark = f"{Colors.OKGREEN}✓{Colors.ENDC}" if has_puhu else f"{Colors.FAIL}✗{Colors.ENDC}"
                
                if has_puhu:
                    status = f"{Colors.OKGREEN}Supported{Colors.ENDC}"
                    total_supported += 1
                else:
                    status = f"{Colors.WARNING}Not implemented{Colors.ENDC}"
                
                if has_pillow:
                    total_methods += 1
                    print(f"{method:<25} {pillow_mark:<18} {puhu_mark:<18} {status}")
        
        coverage = (total_supported / total_methods) * 100 if total_methods > 0 else 0
        print(f"\n{Colors.BOLD}Overall Method Coverage: {coverage:.1f}% ({total_supported}/{total_methods}){Colors.ENDC}")


def benchmark_operations():
    """Benchmark common operations"""
    print_section("Performance Benchmarks")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test images of different sizes
        test_sizes = [
            (100, 100, "Small (100x100)"),
            (500, 500, "Medium (500x500)"),
            (1000, 1000, "Large (1000x1000)")
        ]
        
        for width, height, size_label in test_sizes:
            print(f"\n{Colors.BOLD}{size_label}:{Colors.ENDC}")
            print(f"{'Operation':<30} {'Puhu (ms)':<15} {'Pillow (ms)':<15} {'Speedup':<15}")
            print("─" * 75)
            
            # Create test image
            test_img = tmppath / f"test_{width}x{height}.png"
            pil_test = PILImage.new("RGB", (width, height), color="red")
            pil_test.save(test_img)
            
            # Pre-load images for fair comparison
            puhu_img = puhu.open(test_img)
            pil_img = PILImage.open(test_img)
            
            benchmarks = [
                ("Load image", 
                 lambda: puhu.open(test_img),
                 lambda: PILImage.open(test_img)),
                
                ("Resize (50%)",
                 lambda: puhu_img.resize((width // 2, height // 2)),
                 lambda: pil_img.resize((width // 2, height // 2))),
                
                ("Crop (center 50%)",
                 lambda: puhu_img.crop((width // 4, height // 4, 3 * width // 4, 3 * height // 4)),
                 lambda: pil_img.crop((width // 4, height // 4, 3 * width // 4, 3 * height // 4))),
                
                ("Rotate 90°",
                 lambda: puhu_img.rotate(90),
                 lambda: pil_img.rotate(90)),
                
                ("Convert to grayscale",
                 lambda: puhu_img.convert("L"),
                 lambda: pil_img.convert("L")),
                
                ("Copy",
                 lambda: puhu_img.copy(),
                 lambda: pil_img.copy()),
                
                ("Save to PNG",
                 lambda: puhu_img.save(tmppath / f"puhu_save_{width}.png"),
                 lambda: pil_img.save(tmppath / f"pil_save_{width}.png")),
            ]
            
            for op_name, puhu_func, pil_func in benchmarks:
                puhu_success, puhu_time, puhu_error = benchmark_operation(puhu_func, iterations=3, warmup=1)
                pil_success, pil_time, pil_error = benchmark_operation(pil_func, iterations=3, warmup=1)
                
                if puhu_success and pil_success:
                    speedup = pil_time / puhu_time if puhu_time > 0 else 0
                    
                    if speedup > 1.0:
                        speedup_str = f"{Colors.OKGREEN}{speedup:.2f}x faster{Colors.ENDC}"
                    elif speedup < 1.0:
                        speedup_str = f"{Colors.WARNING}{1/speedup:.2f}x slower{Colors.ENDC}"
                    else:
                        speedup_str = "Same"
                    
                    print(f"{op_name:<30} {puhu_time:<15.2f} {pil_time:<15.2f} {speedup_str}")
                else:
                    error = puhu_error if not puhu_success else pil_error
                    print(f"{op_name:<30} {Colors.FAIL}Error: {error[:30]}{Colors.ENDC}")


def test_format_support():
    """Test image format support"""
    print_section("Image Format Support")
    
    formats = ["PNG", "JPEG", "BMP", "TIFF", "GIF", "WEBP", "ICO"]
    
    print(f"{Colors.BOLD}{'Format':<12} {'Pillow Read':<15} {'Puhu Read':<15} {'Pillow Write':<15} {'Puhu Write':<15}{Colors.ENDC}")
    print("─" * 72)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        for fmt in formats:
            test_file = tmppath / f"test.{fmt.lower()}"
            
            # Test Pillow write
            try:
                pil_img = PILImage.new("RGB", (50, 50), "blue")
                if fmt == "JPEG":
                    pil_img.save(test_file, format=fmt, quality=95)
                else:
                    pil_img.save(test_file, format=fmt)
                pil_write = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                pil_write = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            # Test Pillow read
            try:
                PILImage.open(test_file)
                pil_read = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                pil_read = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            # Test Puhu read
            try:
                puhu.open(test_file)
                puhu_read = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                puhu_read = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            # Test Puhu write
            try:
                puhu_img = puhu.open(test_file)
                puhu_out = tmppath / f"puhu_out.{fmt.lower()}"
                puhu_img.save(puhu_out, format=fmt)
                puhu_write = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                puhu_write = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            print(f"{fmt:<12} {pil_read:<23} {puhu_read:<23} {pil_write:<23} {puhu_write:<23}")


def test_color_modes():
    """Test color mode support"""
    print_section("Color Mode Support")
    
    modes = ["L", "LA", "RGB", "RGBA", "1", "P", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"]
    
    print(f"{Colors.BOLD}{'Mode':<12} {'Description':<25} {'Pillow':<12} {'Puhu':<12}{Colors.ENDC}")
    print("─" * 61)
    
    mode_descriptions = {
        "L": "Grayscale",
        "LA": "Grayscale + Alpha",
        "RGB": "True Color",
        "RGBA": "True Color + Alpha",
        "1": "Bilevel (B&W)",
        "P": "Palette",
        "CMYK": "Cyan-Magenta-Yellow-Black",
        "YCbCr": "YCbCr Video",
        "LAB": "CIE L*a*b*",
        "HSV": "Hue-Saturation-Value",
        "I": "32-bit Integer",
        "F": "32-bit Float"
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        test_img_path = tmppath / "test.png"
        
        # Create base RGB image
        pil_img = PILImage.new("RGB", (50, 50), "red")
        pil_img.save(test_img_path)
        
        for mode in modes:
            desc = mode_descriptions.get(mode, "Unknown")
            
            # Test Pillow
            try:
                PILImage.open(test_img_path).convert(mode)
                pil_support = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                pil_support = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            # Test Puhu
            try:
                puhu.open(test_img_path).convert(mode)
                puhu_support = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            except Exception:
                puhu_support = f"{Colors.FAIL}✗{Colors.ENDC}"
            
            print(f"{mode:<12} {desc:<25} {pil_support:<20} {puhu_support:<20}")


def list_unsupported_methods():
    """List all unsupported Pillow methods"""
    print_section("Unsupported Methods (Pillow features not in Puhu)")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        test_img_path = tmppath / "test.png"
        
        # Create test image
        pil_img = PILImage.new("RGB", (100, 100))
        pil_img.save(test_img_path)
        puhu_img = puhu.open(test_img_path)
        
        categories = get_all_pillow_methods()
        
        unsupported_by_category = {}
        total_unsupported = 0
        
        for category, methods in categories.items():
            unsupported = []
            for method in methods:
                has_pillow = hasattr(pil_img, method) or hasattr(PILImage, method)
                has_puhu = hasattr(puhu_img, method) or hasattr(puhu, method)
                
                if has_pillow and not has_puhu:
                    unsupported.append(method)
                    total_unsupported += 1
            
            if unsupported:
                unsupported_by_category[category] = unsupported
        
        if unsupported_by_category:
            for category, methods in unsupported_by_category.items():
                print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
                for i, method in enumerate(methods, 1):
                    print(f"  {i}. {Colors.WARNING}{method}{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}All Pillow methods are supported!{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Total unsupported methods: {Colors.WARNING}{total_unsupported}{Colors.ENDC}")


def generate_summary():
    """Generate overall summary"""
    print_section("Summary")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        test_img_path = tmppath / "test.png"
        
        # Create test image
        pil_img = PILImage.new("RGB", (100, 100))
        pil_img.save(test_img_path)
        
        # Test basic operations
        basic_ops = [
            ("open", lambda: puhu.open(test_img_path)),
            ("new", lambda: puhu.new("RGB", (50, 50))),
            ("resize", lambda: puhu.open(test_img_path).resize((50, 50))),
            ("crop", lambda: puhu.open(test_img_path).crop((10, 10, 60, 60))),
            ("save", lambda: puhu.open(test_img_path).save(tmppath / "out.png")),
            ("rotate", lambda: puhu.open(test_img_path).rotate(90)),
            ("convert", lambda: puhu.open(test_img_path).convert("L")),
            ("copy", lambda: puhu.open(test_img_path).copy()),
            ("thumbnail", lambda: puhu.open(test_img_path).thumbnail((25, 25))),
            ("transpose", lambda: puhu.open(test_img_path).transpose(puhu.Transpose.FLIP_LEFT_RIGHT)),
        ]
        
        working = 0
        for op_name, op_func in basic_ops:
            try:
                op_func()
                working += 1
            except Exception:
                pass
        
        coverage = (working / len(basic_ops)) * 100
        
        print(f"{Colors.BOLD}Basic Operations Coverage:{Colors.ENDC} {working}/{len(basic_ops)} ({coverage:.1f}%)")
        
        if coverage >= 90:
            status = f"{Colors.OKGREEN}EXCELLENT{Colors.ENDC}"
            message = "Puhu is production-ready for most use cases!"
        elif coverage >= 70:
            status = f"{Colors.OKGREEN}GOOD{Colors.ENDC}"
            message = "Puhu covers most essential operations."
        elif coverage >= 50:
            status = f"{Colors.WARNING}FAIR{Colors.ENDC}"
            message = "Puhu covers some essential operations."
        else:
            status = f"{Colors.FAIL}LIMITED{Colors.ENDC}"
            message = "Puhu has limited coverage."
        
        print(f"{Colors.BOLD}Status:{Colors.ENDC} {status}")
        print(f"{Colors.BOLD}Assessment:{Colors.ENDC} {message}")
        
        print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
        print(f"  • Puhu excels at: {Colors.OKGREEN}Core image operations, format conversion{Colors.ENDC}")
        print(f"  • Use Pillow for: {Colors.WARNING}Advanced filters, pixel manipulation, exotic color modes{Colors.ENDC}")
        print(f"  • Version info: Puhu {puhu.__version__}, Pillow {PILImage.__version__}")


def main():
    """Main benchmark runner"""
    print_header("Comprehensive Benchmark: Puhu vs Pillow")
    
    print(f"{Colors.BOLD}Running comprehensive API and performance comparison...{Colors.ENDC}\n")
    
    try:
        # Run all tests
        check_module_functions()
        check_image_methods()
        test_color_modes()
        test_format_support()
        list_unsupported_methods()
        benchmark_operations()
        generate_summary()
        
        print_header("Benchmark Complete")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Benchmark interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Error during benchmark: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
