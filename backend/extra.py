import os

if os.environ.get("SFVH_BLUR") == "1":
    with open("./static/styles.css", "r", encoding="utf-8") as f:
        styles = f.read()

    blur = """
    img {
        filter: blur(15px);
    }
    
    .manga-title-text {
        filter: blur(3px);
    }
    """

    styles += blur

    with open("./static/styles.css", "w", encoding="utf-8") as f:
        f.write(styles)