def center_window(root, width, height):
    screen_width = 1920
    screen_height = 1080

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    root.geometry(f"{width}x{height}+{x}+{y}")