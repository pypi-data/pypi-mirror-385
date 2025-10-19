def gradient_text(text: str, color1: tuple[int, int, int], color2: tuple[int, int, int], direction: str = "horizontal") -> str:
    """
    Apply a smooth RGB gradient between two colors to text.
    
    direction: "horizontal" (default) or "vertical"
    """
    lines = text.splitlines()
    if not lines:
        return ""

    if direction == "horizontal":
        # Apply gradient across characters in each line
        result_lines = []
        for line in lines:
            chars = list(line)
            n = len(chars)
            if n == 0:
                result_lines.append("")
                continue
            colored_line = []
            for i, ch in enumerate(chars):
                ratio = i / (n - 1) if n > 1 else 0
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                colored_line.append(f"\033[38;2;{r};{g};{b}m{ch}\033[0m")
            result_lines.append("".join(colored_line))
        return "\n".join(result_lines)

    elif direction == "vertical":
        # Apply gradient by line (same color for entire line)
        n = len(lines)
        result_lines = []
        for i, line in enumerate(lines):
            ratio = i / (n - 1) if n > 1 else 0
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            result_lines.append(f"\033[38;2;{r};{g};{b}m{line}\033[0m")
        return "\n".join(result_lines)

    else:
        raise ValueError("direction must be 'horizontal' or 'vertical'")
