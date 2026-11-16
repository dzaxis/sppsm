import pwinput
from prettytable import PrettyTable

from .database import get_connection
from .utils import clear_screen, hash_password, pause


def lihat_semua_pengguna() -> None:
    clear_screen()
    print("=" * 75)
    print("                      DAFTAR SELURUH PENGGUNA")
    print("=" * 75)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_id, username, nama, role, alamat, no_telepon
        FROM users
        ORDER BY role ASC, user_id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nTidak ada data pengguna.")
        pause()
        return

    table = PrettyTable(["ID", "Username", "Nama", "Role", "Telepon", "Alamat"])
    for r in rows:
        table.add_row([
            r["user_id"],
            r["username"],
            r["nama"],
            r["role"].upper(),
            r["no_telepon"] or "-",
            (r["alamat"][:20] + "...") if len(r["alamat"]) > 20 else r["alamat"],
        ])

    print(table)
    pause()


def tambah_petugas_atau_admin() -> None:
    clear_screen()
    print("=" * 50)
    print("       TAMBAH PENGGUNA BARU (PETUGAS / ADMIN)")
    print("=" * 50)

    try:
        username = input("Username          : ").strip()
        if not username:
            print("[!] Username tidak boleh kosong.")
            pause()
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            print("[!] Username sudah digunakan!")
            pause()
            return

        password = pwinput.pwinput("Password          : ", mask="*").strip()
        if len(password) < 4:
            conn.close()
            print("[!] Password minimal 4 karakter.")
            pause()
            return

        nama = input("Nama Lengkap      : ").strip()
        role = input("Role (petugas/admin) [petugas]: ").strip().lower()
        if role not in ["admin", "petugas"]:
            role = "petugas"

        alamat = input("Alamat Kantor/Domisili: ").strip() or "Kantor"
        no_telepon = input("No Telepon / WA   : ").strip()

        hashed = hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, hashed, nama, alamat, no_telepon, role),
        )
        conn.commit()
        conn.close()

        print(f"\n[+] Akun {role.capitalize()} '{username}' berhasil ditambahkan!")
        pause()

    except (KeyboardInterrupt, EOFError):
        print("\n[!] Dibatalkan.")
        pause()


def hapus_pengguna(current_admin_id: int) -> None:
    clear_screen()
    print("=" * 75)
    print("                       HAPUS PENGGUNA")
    print("=" * 75)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_id, username, nama, role
        FROM users
        WHERE user_id != ?
        ORDER BY user_id ASC
        """,
        (current_admin_id,),
    )
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        print("\nTidak ada pengguna lain yang dapat dihapus.")
        pause()
        return

    table = PrettyTable(["ID", "Username", "Nama", "Role"])
    valid_ids = []
    for r in rows:
        valid_ids.append(r["user_id"])
        table.add_row([r["user_id"], r["username"], r["nama"], r["role"].upper()])

    print(table)

    try:
        pilihan = input("\nMasukkan ID pengguna yang ingin dihapus (0 untuk kembali): ").strip()
        if not pilihan or pilihan == "0":
            conn.close()
            return

        user_id = int(pilihan)
        if user_id not in valid_ids:
            conn.close()
            print("[!] ID pengguna tidak valid.")
            pause()
            return

        konfirmasi = input(f"Yakin ingin menghapus pengguna ID #{user_id}? (ketik 'YA' untuk konfirmasi): ")
        if konfirmasi == "YA":
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            print(f"\n[+] Pengguna #{user_id} berhasil dihapus beserta seluruh datanya.")
        else:
            print("\n[-] Penghapusan dibatalkan.")

        conn.close()
        pause()

    except ValueError:
        conn.close()
        print("[!] Input harus angka.")
        pause()
    except (KeyboardInterrupt, EOFError):
        conn.close()
        print("\n[!] Dibatalkan.")
        pause()


def lihat_profil_saya(session_data: dict) -> None:
    clear_screen()
    print("=" * 45)
    print("                 PROFIL SAYA")
    print("=" * 45)
    print(f"Username   : {session_data['username']}")
    print(f"Nama       : {session_data['nama']}")
    print(f"Peran/Role : {session_data['role'].capitalize()}")
    print(f"Alamat     : {session_data['alamat']}")
    print(f"No Telepon : {session_data['no_telepon'] or '-'}")
    print("=" * 45)
    pause()
