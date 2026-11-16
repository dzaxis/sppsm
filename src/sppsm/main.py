import sys

import inquirer

from .auth import login, register_warga, session
from .dashboard import dashboard_admin, dashboard_petugas, dashboard_warga
from .database import init_db
from .utils import clear_screen


def main() -> None:
    try:
        init_db()
    except (OSError, ValueError) as e:
        print(f"[!] Gagal inisialisasi database: {e}")
        sys.exit(1)

    while True:
        try:
            if not session["is_login"]:
                clear_screen()
                print("=" * 55)
                print("   SPPSM - Pengelolaan & Penjemputan Sampah Mandiri")
                print("=" * 55)

                pertanyaan = [
                    inquirer.List(
                        "menu_utama",
                        message="Silakan pilih opsi",
                        choices=[
                            "1. Login",
                            "2. Registrasi Warga Baru",
                            "3. Keluar",
                        ],
                    )
                ]
                jawaban = inquirer.prompt(pertanyaan)
                if not jawaban:
                    print("\nKeluar dari program. Sampai jumpa!")
                    break

                pilihan = jawaban["menu_utama"][0]
                if pilihan == "1":
                    login()
                elif pilihan == "2":
                    register_warga()
                elif pilihan == "3":
                    clear_screen()
                    print("Terima kasih telah menggunakan layanan SPPSM!")
                    break
            else:
                role = session["role"]
                if role == "admin":
                    dashboard_admin()
                elif role == "petugas":
                    dashboard_petugas()
                elif role == "warga":
                    dashboard_warga()
                else:
                    print(f"[!] Role '{role}' tidak dikenali.")
                    session["is_login"] = False

        except (KeyboardInterrupt, EOFError):
            print("\n\nOperasi dihentikan pengguna. Keluar...")
            break


if __name__ == "__main__":
    main()
