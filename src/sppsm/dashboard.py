import inquirer

from .admin import tampilkan_statistik_sistem
from .auth import logout, session
from .requests import (
    batalkan_request_warga,
    buat_request,
    lihat_antrean_petugas,
    lihat_riwayat_warga,
    lihat_semua_request_tabel,
    proses_penjemputan_petugas,
)
from .users import (
    hapus_pengguna,
    lihat_profil_saya,
    lihat_semua_pengguna,
    tambah_petugas_atau_admin,
)
from .utils import clear_screen


def dashboard_warga() -> None:
    while session["is_login"] and session["role"] == "warga":
        clear_screen()
        pertanyaan = [
            inquirer.List(
                "menu",
                message=f"=== DASHBOARD WARGA ({session['nama']}) ===",
                choices=[
                    "1. Buat Permohonan Penjemputan Sampah",
                    "2. Riwayat & Status Permohonan",
                    "3. Batalkan Permohonan Menunggu",
                    "4. Lihat Profil Saya",
                    "5. Logout",
                ],
            )
        ]
        jawaban = inquirer.prompt(pertanyaan)
        if not jawaban:
            break

        pilihan = jawaban["menu"][0]
        if pilihan == "1":
            buat_request(session["user_id"], session["alamat"])
        elif pilihan == "2":
            lihat_riwayat_warga(session["user_id"])
        elif pilihan == "3":
            batalkan_request_warga(session["user_id"])
        elif pilihan == "4":
            lihat_profil_saya(session)
        elif pilihan == "5":
            logout()
            break


def dashboard_petugas() -> None:
    while session["is_login"] and session["role"] == "petugas":
        clear_screen()
        pertanyaan = [
            inquirer.List(
                "menu",
                message=f"=== DASHBOARD PETUGAS ({session['nama']}) ===",
                choices=[
                    "1. Lihat Daftar Antrean Penjemputan",
                    "2. Proses & Timbang Penjemputan Sampah",
                    "3. Riwayat Seluruh Permohonan",
                    "4. Lihat Profil Saya",
                    "5. Logout",
                ],
            )
        ]
        jawaban = inquirer.prompt(pertanyaan)
        if not jawaban:
            break

        pilihan = jawaban["menu"][0]
        if pilihan == "1":
            lihat_antrean_petugas()
        elif pilihan == "2":
            proses_penjemputan_petugas()
        elif pilihan == "3":
            lihat_semua_request_tabel()
        elif pilihan == "4":
            lihat_profil_saya(session)
        elif pilihan == "5":
            logout()
            break


def dashboard_admin() -> None:
    while session["is_login"] and session["role"] == "admin":
        clear_screen()
        pertanyaan = [
            inquirer.List(
                "menu",
                message=f"=== DASHBOARD ADMIN ({session['nama']}) ===",
                choices=[
                    "1. Ringkasan Statistik & Rekapitulasi",
                    "2. Pantau Seluruh Permohonan Penjemputan",
                    "3. Kelola Pengguna (Lihat Semua)",
                    "4. Tambah Akun Petugas / Admin",
                    "5. Hapus Akun Pengguna",
                    "6. Lihat Profil Saya",
                    "7. Logout",
                ],
            )
        ]
        jawaban = inquirer.prompt(pertanyaan)
        if not jawaban:
            break

        pilihan = jawaban["menu"][0]
        if pilihan == "1":
            tampilkan_statistik_sistem()
        elif pilihan == "2":
            lihat_semua_request_tabel()
        elif pilihan == "3":
            lihat_semua_pengguna()
        elif pilihan == "4":
            tambah_petugas_atau_admin()
        elif pilihan == "5":
            hapus_pengguna(session["user_id"])
        elif pilihan == "6":
            lihat_profil_saya(session)
        elif pilihan == "7":
            logout()
            break
