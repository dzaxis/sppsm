from prettytable import PrettyTable

from .database import get_connection
from .utils import clear_screen, pause


def tampilkan_statistik_sistem() -> None:
    clear_screen()
    print("=" * 60)
    print("               STATISTIK & REKAPITULASI SISTEM")
    print("=" * 60)

    conn = get_connection()
    cursor = conn.cursor()

    # Jumlah User berdasarkan Role
    cursor.execute("SELECT role, COUNT(*) as jml FROM users GROUP BY role")
    user_counts = {row["role"]: row["jml"] for row in cursor.fetchall()}

    # Rekap Requests
    cursor.execute("SELECT status, COUNT(*) as jml FROM requests GROUP BY status")
    req_counts = {row["status"]: row["jml"] for row in cursor.fetchall()}

    # Total Berat Sampah yang Berhasil Diangkut
    cursor.execute("SELECT SUM(berat_sampah) as total_berat FROM requests WHERE status = 'selesai'")
    total_berat_row = cursor.fetchone()
    total_berat = total_berat_row["total_berat"] if total_berat_row["total_berat"] else 0.0

    conn.close()

    print("\n[ Ringkasan Pengguna Terdaftar ]")
    user_table = PrettyTable(["Role", "Jumlah Akun"])
    user_table.add_row(["Admin", user_counts.get("admin", 0)])
    user_table.add_row(["Petugas", user_counts.get("petugas", 0)])
    user_table.add_row(["Warga", user_counts.get("warga", 0)])
    user_table.add_row(["TOTAL", sum(user_counts.values())])
    print(user_table)

    print("\n[ Ringkasan Status Permohonan ]")
    req_table = PrettyTable(["Status Permohonan", "Jumlah"])
    req_table.add_row(["Menunggu Diproses", req_counts.get("menunggu", 0)])
    req_table.add_row(["Selesai (Diangkut)", req_counts.get("selesai", 0)])
    req_table.add_row(["Ditolak", req_counts.get("ditolak", 0)])
    req_table.add_row(["Dibatalkan Warga", req_counts.get("dibatalkan", 0)])
    req_table.add_row(["TOTAL PERMOHONAN", sum(req_counts.values())])
    print(req_table)

    print(f"\n[+] Total Sampah Berhasil Diangkut: {total_berat:.2f} kg ({total_berat / 1000:.3f} ton)")
    print("=" * 60)
    pause()
