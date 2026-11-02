"""Read-only Blue Consciousness companion window for A.L.F.I."""

import json
import math
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "assets/alfi/alfi-neural-genesis-display.png"
STATUS = ROOT / ".alfi_visual_status.json"

STATES = {
    "idle": ("IDLE", "#80bfff"),
    "processing": ("PROCESSING", "#5dd9ff"),
    "responding": ("RESPONDING", "#d0efff"),
}


def main():
    if not ASSET.is_file():
        raise SystemExit(f"Missing visual asset: {ASSET}")

    root = tk.Tk()
    root.title("A.L.F.I. — Neural Genesis")
    root.geometry("440x520")
    root.minsize(400, 480)
    root.configure(bg="#080e1c")

    original = tk.PhotoImage(file=str(ASSET))
    artwork = original

    image_label = tk.Label(root, image=artwork, bg="#080e1c")
    image_label.pack(pady=(12, 4))

    state_label = tk.Label(
        root,
        text="IDLE",
        fg="#80bfff",
        bg="#080e1c",
        font=("Helvetica", 15, "bold"),
    )
    state_label.pack(pady=(4, 4))

    detail_label = tk.Label(
        root,
        text="Neural Genesis | Visual observer",
        fg="#8a9db7",
        bg="#080e1c",
        font=("Helvetica", 10),
    )
    detail_label.pack(pady=(0, 8))

    root.original_image = original
    root.artwork = artwork
    tick = [0]

    def refresh():
        state = "idle"

        try:
            payload = json.loads(STATUS.read_text())
            candidate = payload.get("state", "idle")
            if candidate in STATES:
                state = candidate
        except (OSError, ValueError, AttributeError):
            pass

        title, color = STATES[state]
        state_label.configure(text=title, fg=color)

        if state == "processing":
            tick[0] += 1
            brightness = 0.65 + 0.35 * (
                0.5 + 0.5 * math.sin(tick[0] * 0.45)
            )
            intensity = int(140 + 115 * brightness)
            state_label.configure(fg=f"#40{intensity:02x}ff")

        root.after(150, refresh)

    refresh()
    root.mainloop()


if __name__ == "__main__":
    main()
