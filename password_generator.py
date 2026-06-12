import math
import secrets
import string


# ── Character pools ──────────────────────────────────────────────────────────

LETTERS  = string.ascii_letters   # a-z + A-Z
DIGITS   = string.digits          # 0-9
SYMBOLS  = string.punctuation     # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_password_length() -> int:
    """Ask the user for a password length and validate it (NIST SP 800-63-4)."""
    MIN_LENGTH = 15   # NIST 2024 minimum for high-security contexts
    MAX_LENGTH = 128  # well above the required 64-char support ceiling

    while True:
        raw = input(f"\nEnter desired password length ({MIN_LENGTH}–{MAX_LENGTH}): ").strip()

        if not raw.isdigit():
            print("  ✗  Please enter a whole number.")
            continue

        length = int(raw)

        if length < MIN_LENGTH:
            print(f"  ✗  Length must be at least {MIN_LENGTH} characters (NIST SP 800-63-4).")
        elif length > MAX_LENGTH:
            print(f"  ✗  Length cannot exceed {MAX_LENGTH} characters.")
        else:
            return length


def ask_yes_no(prompt: str) -> bool:
    """Simple yes/no prompt that keeps asking until it gets a clear answer."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ✗  Please type y or n.")


def build_character_pool(use_symbols: bool) -> str:
    """Assemble the character pool based on user preferences."""
    pool = LETTERS + DIGITS
    if use_symbols:
        pool += SYMBOLS
    return pool


def generate_password(length: int, pool: str, require_digit: bool) -> str:
    """
    Generate a cryptographically secure password.

    Uses secrets.choice() (OS-level entropy) instead of random.choice()
    (Mersenne Twister — predictable and unsuitable for security work).

    The list + join pattern runs in O(N) memory rather than the O(N²)
    cost of repeated string concatenation.
    """
    while True:
        chars    = [secrets.choice(pool) for _ in range(length)]
        password = "".join(chars)

        # Guarantee at least one digit when the user requested it
        if require_digit and not any(c in DIGITS for c in password):
            continue

        return password


def calculate_entropy(length: int, pool_size: int) -> float:
    """
    Entropy in bits: E = L × log₂(R)

    L = password length
    R = size of the character pool
    """
    return length * math.log2(pool_size)


def entropy_label(bits: float) -> str:
    """Return a human-readable strength label for a given entropy value."""
    if bits < 40:
        return "Weak"
    if bits < 60:
        return "Moderate"
    if bits < 80:
        return "Strong"
    if bits < 120:
        return "Very Strong"
    return "Extremely Strong"


# ── Main flow ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("       Secure Password Generator")
    print("       NIST SP 800-63-4 compliant")
    print("=" * 52)

    # Phase 1 — input & validation
    length      = get_password_length()
    use_symbols = ask_yes_no("Include special characters? (y/n): ")
    req_digit   = ask_yes_no("Guarantee at least one digit?   (y/n): ")

    # Phase 2 — generation
    pool     = build_character_pool(use_symbols)
    password = generate_password(length, pool, req_digit)

    # Phase 3 — entropy report
    pool_size = len(pool)
    entropy   = calculate_entropy(length, pool_size)
    label     = entropy_label(entropy)

    print("\n" + "-" * 52)
    print(f"  Generated password:\n\n    {password}\n")
    print("-" * 52)
    print(f"  Length         : {length} characters")
    print(f"  Character pool : {pool_size} symbols")
    print(f"  Entropy        : {entropy:.1f} bits  ({label})")
    print("-" * 52)
    print(f"\n  At 10^12 guesses/sec a brute-force attack would")
    print(f"  need ~{2**entropy / 1e12:,.0f} seconds on average to crack this.")
    print()


if __name__ == "__main__":
    main()
