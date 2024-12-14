import os

blur = """
/* BLUR_START */
img {
    filter: blur(25px);
}

.project-title-text {
    filter: blur(3px);
}
/* BLUR_END */
"""

with open("./static/styles.css", "r", encoding="utf-8") as f:
    styles = f.read()

if os.environ.get("SFVH_BLUR") == "1" and styles.find(blur) == -1:
    styles += blur

    with open("./static/styles.css", "w", encoding="utf-8") as f:
        f.write(styles)
elif os.environ.get("SFVH_BLUR") == "0" and styles.find(blur) != -1:
    styles = styles.replace(blur, "")

    with open("./static/styles.css", "w", encoding="utf-8") as f:
        f.write(styles)
