from datetime import datetime

import inquirer
from prettytable import PrettyTable

from .database import get_connection
from .utils import clear_screen, pause


def buat_request(user_id: int, alamat_default: str) -> None:
    clear_screen()
    print("=" * 45)
    print("        FORM PENJEMPUTAN SAMPAH")
    print("=" * 45)

    try:
        print(f"Alamat default profil: {alamat_default}")
        pake_default = input("Gunakan alamat ini? (Y/n): ").strip().lower()
        if pake_default == "n":
            alamat = input("Masukkan alamat penjemputan: ").strip()
            if not alamat:
                print("[!] Alamat tidak boleh kosong.")
                pause()
                return
        else:
            alamat = alamat_default

        catatan = input("Catatan tambahan (jenis sampah/patokan lokasi, opsional): ").strip()

        tgl_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO requests (user_id, tanggal_pengajuan, alamat, status, catatan)
            VALUES (?, ?, ?, 'menunggu', ?)
            """,
            (user_id, tgl_sekarang, alamat, catatan),
        )
        conn.commit()
        conn.close()

        print("\n[+] Permohonan penjemputan berhasil dibuat dengan status 'menunggu'.")
        print("[*] Petugas akan segera memproses jadwal penjemputan Anda.")
        pause()

    except (KeyboardInterrupt, EOFError):
        print("\n[!] Dibatalkan.")
        pause()


def lihat_riwayat_warga(user_id: int) -> None:
    clear_screen()
    print("=" * 70)
    print("                 RIWAYAT PERMOHONAN SAYA")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT request_id, tanggal_pengajuan, jadwal_penjemputan, berat_sampah, alamat, status, catatan
        FROM requests
        WHERE user_id = ?
        ORDER BY request_id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nBelum ada permohonan penjemputan.")
        pause()
        return

    table = PrettyTable([
        "ID",
        "Tgl Pengajuan",
        "Jadwal Jemput",
        "Berat (kg)",
        "Status",
        "Alamat",
        "Catatan",
    ])

    for r in rows:
        jadwal = r["jadwal_penjemputan"] if r["jadwal_penjemputan"] else "-"
        berat = f"{r['berat_sampah']:.1f}" if r["berat_sampah"] is not None else "-"
        table.add_row([
            r["request_id"],
            r["tanggal_pengajuan"],
            jadwal,
            berat,
            r["status"].upper(),
            (r["alamat"][:20] + "...") if len(r["alamat"]) > 20 else r["alamat"],
            (r["catatan"][:20] + "...") if (r["catatan"] and len(r["catatan"]) > 20) else (r["catatan"] or "-"),
        ])

    print(table)
    pause()


def batalkan_request_warga(user_id: int) -> None:
    clear_screen()
    print("=" * 70)
    print("              BATALKAN PERMOHONAN PENJEMPUTAN")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT request_id, tanggal_pengajuan, alamat, catatan
        FROM requests
        WHERE user_id = ? AND status = 'menunggu'
        ORDER BY request_id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        print("\nTidak ada permohonan berstatus 'menunggu' yang dapat dibatalkan.")
        pause()
        return

    table = PrettyTable(["ID", "Tgl Pengajuan", "Alamat", "Catatan"])
    valid_ids = []
    for r in rows:
        valid_ids.append(r["request_id"])
        table.add_row([
            r["request_id"],
            r["tanggal_pengajuan"],
            r["alamat"],
            r["catatan"] or "-",
        ])

    print(table)

    try:
        req_id_str = input("\nMasukkan ID permohonan yang ingin dibatalkan (0 untuk kembali): ").strip()
        if not req_id_str or req_id_str == "0":
            conn.close()
            return

        req_id = int(req_id_str)
        if req_id not in valid_ids:
            conn.close()
            print("[!] ID permohonan tidak valid atau sudah diproses.")
            pause()
            return

        cursor.execute(
            "UPDATE requests SET status = 'dibatalkan' WHERE request_id = ? AND user_id = ?",
            (req_id, user_id),
        )
        conn.commit()
        conn.close()

        print(f"\n[+] Permohonan #{req_id} berhasil dibatalkan.")
        pause()

    except ValueError:
        conn.close()
        print("[!] Input harus berupa angka.")
        pause()
    except (KeyboardInterrupt, EOFError):
        conn.close()
        print("\n[!] Dibatalkan.")
        pause()


# ===================== FUNGSI KHUSUS PETUGAS =====================

def lihat_antrean_petugas() -> None:
    clear_screen()
    print("=" * 80)
    print("                 DAFTAR ANTREAN PENJEMPUTAN SAMPAH")
    print("=" * 80)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.request_id, u.nama, u.no_telepon, r.alamat, r.tanggal_pengajuan, r.status, r.catatan
        FROM requests r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status = 'menunggu'
        ORDER BY r.request_id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nTidak ada antrean permohonan penjemputan saat ini.")
        pause()
        return

    table = PrettyTable(["ID", "Pemohon", "Telepon", "Alamat", "Tgl Pengajuan", "Status", "Catatan"])
    for r in rows:
        table.add_row([
            r["request_id"],
            r["nama"],
            r["no_telepon"] or "-",
            (r["alamat"][:25] + "...") if len(r["alamat"]) > 25 else r["alamat"],
            r["tanggal_pengajuan"],
            r["status"].upper(),
            (r["catatan"][:20] + "...") if (r["catatan"] and len(r["catatan"]) > 20) else (r["catatan"] or "-"),
        ])

    print(table)
    pause()


def proses_penjemputan_petugas() -> None:
    clear_screen()
    print("=" * 80)
    print("              PROSES / SELESAIKAN PENJEMPUTAN SAMPAH")
    print("=" * 80)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.request_id, u.nama, u.no_telepon, r.alamat, r.tanggal_pengajuan, r.status, r.catatan
        FROM requests r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status = 'menunggu'
        ORDER BY r.request_id ASC
        """
    )
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        print("\nTidak ada permohonan yang menunggu untuk diproses.")
        pause()
        return

    table = PrettyTable(["ID", "Pemohon", "Telepon", "Alamat", "Tgl Pengajuan"])
    valid_ids = []
    for r in rows:
        valid_ids.append(r["request_id"])
        table.add_row([
            r["request_id"],
            r["nama"],
            r["no_telepon"] or "-",
            (r["alamat"][:25] + "...") if len(r["alamat"]) > 25 else r["alamat"],
            r["tanggal_pengajuan"],
        ])

    print(table)

    try:
        pilihan = input("\nMasukkan ID permohonan yang ingin ditindaklanjuti (0 untuk kembali): ").strip()
        if not pilihan or pilihan == "0":
            conn.close()
            return

        req_id = int(pilihan)
        if req_id not in valid_ids:
            conn.close()
            print("[!] ID tidak ditemukan dalam daftar antrean.")
            pause()
            return

        pertanyaan = [
            inquirer.List(
                "aksi",
                message=f"Tindakan untuk request #{req_id}:",
                choices=[
                    "1. Selesaikan (Timbang & Angkut)",
                    "2. Tolak Permohonan",
                    "3. Batal",
                ],
            )
        ]
        jawaban = inquirer.prompt(pertanyaan)
        if not jawaban or "Batal" in jawaban["aksi"]:
            conn.close()
            return

        aksi = jawaban["aksi"][0]

        if aksi == "1":
            berat_str = input("Masukkan berat sampah yang diangkut (kg, contoh: 4.5): ").strip()
            try:
                berat = float(berat_str)
                if berat < 0:
                    raise ValueError
            except ValueError:
                conn.close()
                print("[!] Berat sampah harus berupa angka positif.")
                pause()
                return

            catatan_opsional = input("Catatan tambahan penjemputan (opsional): ").strip()
            tgl_jemput = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                UPDATE requests
                SET status = 'selesai',
                    jadwal_penjemputan = ?,
                    berat_sampah = ?,
                    catatan = CASE 
                        WHEN catatan IS NULL OR catatan = '' THEN ? 
                        ELSE catatan || ' | Petugas: ' || ? 
                    END
                WHERE request_id = ?
                """,
                (tgl_jemput, berat, catatan_opsional, catatan_opsional, req_id),
            )
            conn.commit()
            print(f"\n[+] Request #{req_id} berhasil diselesaikan. Berat tercatat: {berat} kg.")

        elif aksi == "2":
            alasan = input("Alasan penolakan: ").strip()
            if not alasan:
                alasan = "Ditolak oleh petugas lapangan"

            cursor.execute(
                """
                UPDATE requests
                SET status = 'ditolak',
                    catatan = CASE 
                        WHEN catatan IS NULL OR catatan = '' THEN ? 
                        ELSE catatan || ' | Alasan Ditolak: ' || ? 
                    END
                WHERE request_id = ?
                """,
                (f"Ditolak: {alasan}", alasan, req_id),
            )
            conn.commit()
            print(f"\n[+] Request #{req_id} telah ditandai ditolak.")

        conn.close()
        pause()

    except ValueError:
        conn.close()
        print("[!] Input harus berupa angka.")
        pause()
    except (KeyboardInterrupt, EOFError):
        conn.close()
        print("\n[!] Dibatalkan.")
        pause()


def lihat_semua_request_tabel() -> None:
    clear_screen()
    print("=" * 85)
    print("                   SELURUH DATA PERMOHONAN PENJEMPUTAN")
    print("=" * 85)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.request_id, u.nama, r.tanggal_pengajuan, r.jadwal_penjemputan, 
               r.berat_sampah, r.status, r.alamat, r.catatan
        FROM requests r
        JOIN users u ON r.user_id = u.user_id
        ORDER BY r.request_id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nBelum ada data permohonan dalam sistem.")
        pause()
        return

    table = PrettyTable([
        "ID",
        "Pemohon",
        "Tgl Pengajuan",
        "Tgl Selesai",
        "Berat (kg)",
        "Status",
        "Alamat",
    ])

    for r in rows:
        jadwal = r["jadwal_penjemputan"] if r["jadwal_penjemputan"] else "-"
        berat = f"{r['berat_sampah']:.1f}" if r["berat_sampah"] is not None else "-"
        table.add_row([
            r["request_id"],
            r["nama"],
            r["tanggal_pengajuan"],
            jadwal,
            berat,
            r["status"].upper(),
            (r["alamat"][:25] + "...") if len(r["alamat"]) > 25 else r["alamat"],
        ])

    print(table)
    pause()
