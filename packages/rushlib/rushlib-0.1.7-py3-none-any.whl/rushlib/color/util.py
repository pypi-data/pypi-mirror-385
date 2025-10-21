def vali_rgba(r, g, b, a=255):
    return (
        min(255, max(0, r)),
        min(255, max(0, g)),
        min(255, max(0, b)),
        min(255, max(0, a))
    )

def hex_to_rgb(hex_str: str) -> tuple[int, int, int, int]:
    r, g, b, a = 0, 0, 0, 255

    hex_str = hex_str.lstrip('#')

    if len(hex_str) not in (3, 4, 6, 8):
        raise ValueError("十六进制颜色代码必须是3, 4, 6或8个字符")

    if len(hex_str) == 3:
        hex_str = ''.join([c * 2 for c in hex_str])
    elif len(hex_str) == 4:
        hex_str = ''.join([c * 2 for c in hex_str])
        alpha_hex = hex_str[6:8]
        a = int(alpha_hex, 16)
        hex_str = hex_str[0:6]

    if len(hex_str) == 8:
        alpha_hex = hex_str[6:8]
        a = int(alpha_hex, 16)
        hex_str = hex_str[0:6]

    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    except ValueError:
        raise ValueError("无效的十六进制颜色代码")

    return r, g, b, a

def rgb_to_hex(r, g, b) -> str:
    return '#%02x%02x%02x' % vali_rgba(r, g, b)[0:3]
