import math
import secrets
import string

import customtkinter as ctk

# ── Appearance ────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Character pools ───────────────────────────────────────────────────────────

LETTERS = string.ascii_letters
DIGITS  = string.digits
SYMBOLS = string.punctuation

MIN_LEN = 15
MAX_LEN = 128

# ── Strength colours (weak → strong) ─────────────────────────────────────────

STRENGTH_COLORS = {
    "Weak":             "#e74c3c",
    "Moderate":         "#e67e22",
    "Strong":           "#f1c40f",
    "Very Strong":      "#2ecc71",
    "Extremely Strong": "#1abc9c",
}


# ── Core logic (same engine as the CLI version) ───────────────────────────────

def build_pool(use_symbols: bool) -> str:
    pool = LETTERS + DIGITS
    if use_symbols:
        pool += SYMBOLS
    return pool


def generate_password(length: int, pool: str, require_digit: bool) -> str:
    while True:
        chars    = [secrets.choice(pool) for _ in range(length)]
        password = "".join(chars)
        if require_digit and not any(c in DIGITS for c in password):
            continue
        return password


def entropy_info(length: int, pool_size: int):
    bits = length * math.log2(pool_size)
    if bits < 40:
        label = "Weak"
    elif bits < 60:
        label = "Moderate"
    elif bits < 80:
        label = "Strong"
    elif bits < 120:
        label = "Very Strong"
    else:
        label = "Extremely Strong"
    return bits, label


# ── App ───────────────────────────────────────────────────────────────────────

class PasswordApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Password Generator")
        self.geometry("540x640")
        self.resizable(False, False)

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(28, 4), padx=32, fill="x")

        ctk.CTkLabel(
            header,
            text="🔐  Password Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")

        self.mode_btn = ctk.CTkButton(
            header,
            text="☀  Light",
            width=90,
            height=30,
            corner_radius=8,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            command=self._toggle_mode,
        )
        self.mode_btn.pack(side="right")

        ctk.CTkLabel(
            self,
            text="NIST SP 800-63-4 compliant  •  secrets module",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack()

        # ── Length slider ─────────────────────────────────────────────────────
        length_frame = ctk.CTkFrame(self, corner_radius=12)
        length_frame.pack(pady=(20, 0), padx=32, fill="x")

        top_row = ctk.CTkFrame(length_frame, fg_color="transparent")
        top_row.pack(padx=16, pady=(14, 4), fill="x")

        ctk.CTkLabel(top_row, text="Password Length", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.length_val = ctk.CTkLabel(top_row, text=str(MIN_LEN), font=ctk.CTkFont(size=13, weight="bold"))
        self.length_val.pack(side="right")

        self.slider = ctk.CTkSlider(
            length_frame,
            from_=MIN_LEN,
            to=MAX_LEN,
            number_of_steps=MAX_LEN - MIN_LEN,
            command=self._on_slider,
        )
        self.slider.set(MIN_LEN)
        self.slider.pack(padx=16, pady=(0, 14), fill="x")

        # ── Options ───────────────────────────────────────────────────────────
        opts_frame = ctk.CTkFrame(self, corner_radius=12)
        opts_frame.pack(pady=(12, 0), padx=32, fill="x")

        self.sym_var   = ctk.BooleanVar(value=True)
        self.digit_var = ctk.BooleanVar(value=True)

        ctk.CTkLabel(opts_frame, text="Options", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 6)
        )

        row1 = ctk.CTkFrame(opts_frame, fg_color="transparent")
        row1.pack(padx=16, pady=(0, 4), fill="x")
        ctk.CTkSwitch(row1, text="Include special characters  (!@#$…)", variable=self.sym_var).pack(side="left")

        row2 = ctk.CTkFrame(opts_frame, fg_color="transparent")
        row2.pack(padx=16, pady=(0, 14), fill="x")
        ctk.CTkSwitch(row2, text="Guarantee at least one digit", variable=self.digit_var).pack(side="left")

        # ── Generate button ───────────────────────────────────────────────────
        self.gen_btn = ctk.CTkButton(
            self,
            text="Generate Password",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._generate,
        )
        self.gen_btn.pack(pady=(18, 0), padx=32, fill="x")

        # ── Password output ───────────────────────────────────────────────────
        out_frame = ctk.CTkFrame(self, corner_radius=12)
        out_frame.pack(pady=(16, 0), padx=32, fill="x")

        ctk.CTkLabel(out_frame, text="Generated Password", font=ctk.CTkFont(size=12), text_color="gray").pack(
            anchor="w", padx=16, pady=(12, 4)
        )

        pw_row = ctk.CTkFrame(out_frame, fg_color="transparent")
        pw_row.pack(padx=16, pady=(0, 12), fill="x")

        self.pw_entry = ctk.CTkEntry(
            pw_row,
            placeholder_text="Click Generate…",
            font=ctk.CTkFont(family="Courier New", size=13),
            height=40,
            corner_radius=8,
        )
        self.pw_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.copy_btn = ctk.CTkButton(
            pw_row,
            text="Copy",
            width=64,
            height=40,
            corner_radius=8,
            command=self._copy,
        )
        self.copy_btn.pack(side="right")

        # ── Strength bar ──────────────────────────────────────────────────────
        strength_frame = ctk.CTkFrame(self, corner_radius=12)
        strength_frame.pack(pady=(12, 0), padx=32, fill="x")

        top = ctk.CTkFrame(strength_frame, fg_color="transparent")
        top.pack(padx=16, pady=(12, 4), fill="x")

        ctk.CTkLabel(top, text="Entropy", font=ctk.CTkFont(size=12), text_color="gray").pack(side="left")
        self.entropy_label = ctk.CTkLabel(top, text="—", font=ctk.CTkFont(size=12, weight="bold"))
        self.entropy_label.pack(side="right")

        self.strength_bar = ctk.CTkProgressBar(strength_frame, height=12, corner_radius=6)
        self.strength_bar.set(0)
        self.strength_bar.pack(padx=16, pady=(0, 8), fill="x")

        self.strength_label = ctk.CTkLabel(
            strength_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.strength_label.pack(pady=(0, 12))

        # ── Stats row ─────────────────────────────────────────────────────────
        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=460,
            justify="center",
        )
        self.stats_label.pack(pady=(10, 0), padx=32)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_slider(self, value):
        self.length_val.configure(text=str(int(value)))

    def _generate(self):
        length      = int(self.slider.get())
        use_symbols = self.sym_var.get()
        req_digit   = self.digit_var.get()

        pool     = build_pool(use_symbols)
        password = generate_password(length, pool, req_digit)
        bits, label = entropy_info(length, len(pool))

        # Update password field
        self.pw_entry.delete(0, "end")
        self.pw_entry.insert(0, password)

        # Update strength bar
        max_bits = MAX_LEN * math.log2(94)          # theoretical max
        progress = min(bits / max_bits, 1.0)
        color    = STRENGTH_COLORS[label]

        self.strength_bar.set(progress)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=label, text_color=color)
        self.entropy_label.configure(text=f"{bits:.1f} bits")

        # Stats line
        crack_sec = 2 ** bits / 1e12
        if crack_sec > 3.15e7:
            crack_str = f"{crack_sec / 3.15e7:,.0f} years"
        else:
            crack_str = f"{crack_sec:,.0f} seconds"

        self.stats_label.configure(
            text=f"Pool: {len(pool)} chars  •  Length: {length}  •  "
                 f"Brute-force @ 10¹² /sec ≈ {crack_str}"
        )

    def _copy(self):
        password = self.pw_entry.get()
        if not password or password == "Click Generate…":
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.copy_btn.configure(text="Copied ✓")
        self.after(1800, lambda: self.copy_btn.configure(text="Copy"))

    def _toggle_mode(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.mode_btn.configure(text="🌙  Dark")
        else:
            ctk.set_appearance_mode("dark")
            self.mode_btn.configure(text="☀  Light")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()
