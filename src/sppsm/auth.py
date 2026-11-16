from typing import Any

import pwinput

from .database import get_connection
from .utils import clear_screen, hash_password, pause, verify_password

session: dict[str, Any] = {
    "user_id": None,
    "username": None,
    "nama": None,
    "role": None,
    "alamat": None,
    "no_telepon": None,
    "is_login": False,
}


def set_session(user_row: Any) -> None:
    session["user_id"] = user_row["user_id"]
    session["username"] = user_row["username"]
    session["nama"] = user_row["nama"]
    session["role"] = user_row["role"]
    session["alamat"] = user_row["alamat"]
    session["no_telepon"] = user_row["no_telepon"]
    session["is_login"] = True


def logout() -> None:
    session["user_id"] = None
    session["username"] = None
    session["nama"] = None
    session["role"] = None
    session["alamat"] = None
    session["no_telepon"] = None
    session["is_login"] = False
    print("\nAnda berhasil keluar.")
    pause()


def login() -> bool:
    clear_screen()
    print("=" * 40)
    print("           LOGIN PENGGUNA")
    print("=" * 40)

    try:
        username = input("Username: ").strip()
        if not username:
            print("[!] Username tidak boleh kosong.")
            pause()
            return False

        password = pwinput.pwinput("Password: ", mask="*").strip()
        if not password:
            print("[!] Password tidak boleh kosong.")
            pause()
            return False
    except (KeyboardInterrupt, EOFError):
        print("\n[!] Login dibatalkan.")
        pause()
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user["password"]):
        set_session(user)
        print(f"\n[+] Selamat datang kembali, {user['nama']} ({user['role'].capitalize()})!")
        pause()
        return True
    else:
        print("\n[!] Username atau password salah!")
        pause()
        return False


def register_warga() -> bool:
    clear_screen()
    print("=" * 40)
    print("      REGISTRASI WARGA BARU")
    print("=" * 40)

    try:
        username = input("Username          : ").strip()
        if not username:
            print("[!] Username tidak boleh kosong.")
            pause()
            return False

        # Cek ketersediaan username
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            print("[!] Username sudah terdaftar. Silakan pilih username lain.")
            pause()
            return False

        password = pwinput.pwinput("Password          : ", mask="*").strip()
        if len(password) < 4:
            conn.close()
            print("[!] Password minimal 4 karakter.")
            pause()
            return False

        nama = input("Nama Lengkap      : ").strip()
        alamat = input("Alamat Rumah      : ").strip()
        no_telepon = input("No Telepon / WA   : ").strip()

        if not nama or not alamat:
            conn.close()
            print("[!] Nama dan Alamat wajib diisi.")
            pause()
            return False

        hashed = hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role)
            VALUES (?, ?, ?, ?, ?, 'warga')
            """,
            (username, hashed, nama, alamat, no_telepon),
        )
        conn.commit()
        conn.close()

        print("\n[+] Registrasi berhasil! Silakan login dengan akun Anda.")
        pause()
        return True

    except (KeyboardInterrupt, EOFError):
        print("\n[!] Registrasi dibatalkan.")
        pause()
        return False
