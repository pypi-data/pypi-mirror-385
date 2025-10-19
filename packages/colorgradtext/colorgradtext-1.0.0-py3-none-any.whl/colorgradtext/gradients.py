from .utils import gradient_text

# --- Named gradient presets with direction support ---

def aqua_wave(text: str, direction: str = "horizontal"):
    """Fresh Teal → Blue"""
    return gradient_text(text, (0, 230, 180), (0, 120, 255), direction)

def rose_blush(text: str, direction: str = "horizontal"):
    """Bright Red → Pink"""
    return gradient_text(text, (255, 50, 50), (255, 130, 180), direction)

def violet_dream(text: str, direction: str = "horizontal"):
    """Deep Blue → Vibrant Purple"""
    return gradient_text(text, (0, 50, 255), (160, 0, 255), direction)

def sunflare(text: str, direction: str = "horizontal"):
    """Orange → Gold"""
    return gradient_text(text, (255, 140, 0), (255, 220, 60), direction)

def frostbite(text: str, direction: str = "horizontal"):
    """Bright Cyan → White"""
    return gradient_text(text, (0, 220, 255), (255, 255, 255), direction)

def ember_glow(text: str, direction: str = "horizontal"):
    """Red → Yellow Flame"""
    return gradient_text(text, (255, 40, 0), (255, 240, 20), direction)

def tidepool(text: str, direction: str = "horizontal"):
    """Ocean Blue → Aqua"""
    return gradient_text(text, (0, 100, 255), (0, 255, 200), direction)

def evenfall(text: str, direction: str = "horizontal"):
    """Coral → Peach Sunset"""
    return gradient_text(text, (255, 90, 70), (255, 195, 110), direction)

def lime_light(text: str, direction: str = "horizontal"):
    """Bright Lime Green → Yellow-Green"""
    return gradient_text(text, (50, 205, 50), (180, 255, 60), direction)

def dreamcloud(text: str, direction: str = "horizontal"):
    """Pink → Sky Blue"""
    return gradient_text(text, (255, 160, 180), (135, 220, 250), direction)
