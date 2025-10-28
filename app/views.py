from .models import *
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase.ttfonts import TTFont
import io, os
from django.db.models import IntegerField, F
from django.db.models.functions import Cast, Substr, Length
from reportlab.pdfgen import canvas

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # redirect ke home.html setelah login
        else:
            messages.error(request, "Username atau password tidak sesuai.")
            return render(request, "login.html")
    else:
        return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})

@login_required
def fakultas_list(request):
    fakultas = Fakultas.objects.all()
    return render(request, 'data/fakultas.html', {'fakultas': fakultas})

@login_required
def fakultas_add(request):
    # Jika user menekan tombol submit
    if request.method == "POST":
        kodept = request.POST.get("kodept")
        pimpinanpt = request.POST.get("pimpinanpt")
        akrelembaga = request.POST.get("akrelembaga")
        kodefakultas = request.POST.get("kodefakultas")
        namafakultas = request.POST.get("namafakultas")
        namafakultas_en = request.POST.get("namafakultas_en")
        dekan = request.POST.get("dekan")
        dekan_en = request.POST.get("dekan_en")
        namadekan = request.POST.get("namadekan")
        nipt = request.POST.get("nipt")

        # Validasi sederhana
        if not all([kodept, kodefakultas, namafakultas]):
            messages.error(request, "Kode PT, Kode Fakultas, dan Nama Fakultas wajib diisi!")
            return redirect("fakultas_list")

        # Simpan ke database
        Fakultas.objects.create(
            kodept=kodept,
            pimpinanpt=pimpinanpt,
            akrelembaga=akrelembaga,
            kodefakultas=kodefakultas,
            namafakultas=namafakultas,
            namafakultas_en=namafakultas_en,
            dekan=dekan,
            dekan_en=dekan_en,
            namadekan=namadekan,
            nipt=nipt,
        )

        messages.success(request, f"Data Fakultas '{namafakultas}' berhasil ditambahkan.")
        return redirect("fakultas_list")

    # Jika bukan POST (misal akses langsung)
    fakultas = Fakultas.objects.all().order_by("namafakultas")

    context = {
        "title": "Tambah Data Fakultas",
        "fakultas": fakultas
    }
    return render(request, "data/fakultas.html", context)

@login_required
def update_fakultas(request, id):
    fakultas = get_object_or_404(Fakultas, id=id)
    if request.method == 'POST':
        fakultas.pimpinanpt = request.POST.get('pimpinanpt')
        fakultas.akrelembaga = request.POST.get('akrelembaga')
        fakultas.namafakultas = request.POST.get('namafakultas')
        fakultas.namafakultas_en = request.POST.get('namafakultas_en')
        fakultas.dekan = request.POST.get('dekan')
        fakultas.dekan_en = request.POST.get('dekan_en')
        fakultas.namadekan = request.POST.get('namadekan')
        fakultas.nipt = request.POST.get('nipt')
        fakultas.save()
        messages.success(request, 'Data Fakultas berhasil diperbarui!')
        return redirect('fakultas_list')
    return redirect('fakultas_list')

@login_required
def delete_fakultas(request, id):
    fakultas = get_object_or_404(Fakultas, id=id)
    if request.method == 'POST':
        fakultas.delete()
        messages.success(request, 'Data Fakultas berhasil dihapus!')
    return redirect('fakultas_list')

@login_required
def prodi_list(request):
    prodi = Prodi.objects.select_related('fakultas').all().order_by('namaprodi')
    fakultas_list = Fakultas.objects.all().order_by('namafakultas')  # 🔥 tambahkan ini

    context = {
        'title': 'Daftar Program Studi',
        'prodi': prodi,
        'fakultas_list': fakultas_list,  # 🔥 kirim ke template
    }
    return render(request, 'data/prodi.html', context)

@login_required
def prodi_add(request):
    if request.method == "POST":
        fakultas_id = request.POST.get("fakultas")
        kode_prodi = request.POST.get("kode_prodi")
        namaprodi = request.POST.get("namaprodi")
        namaprodi_en = request.POST.get("namaprodi_en")
        akreditasi = request.POST.get("akreditasi")
        noakreditasi = request.POST.get("noakreditasi")
        gelar = request.POST.get("gelar")
        pisn = request.POST.get("pisn")

        if not fakultas_id or not kode_prodi:
            messages.error(request, "Fakultas dan Kode Prodi wajib diisi!")
            return redirect("prodi_add")

        fakultas_obj = get_object_or_404(Fakultas, id=fakultas_id)

        Prodi.objects.create(
            fakultas=fakultas_obj,
            kode_prodi=kode_prodi,
            namaprodi=namaprodi,
            namaprodi_en=namaprodi_en,
            akreditasi=akreditasi,
            noakreditasi=noakreditasi,
            gelar=gelar,
            pisn=pisn,
        )

        messages.success(request, f"Program Studi '{namaprodi}' berhasil ditambahkan.")
        return redirect("prodi_list")

    # ✅ ini penting: kirim daftar fakultas ke template
    fakultas_list = Fakultas.objects.all().order_by("namafakultas")

    context = {
        "title": "Tambah Data Program Studi",
        "fakultas_list": fakultas_list,
    }
    return render(request, "data/prodi_add.html", context)

@login_required
def update_prodi(request, id):
    prodi = get_object_or_404(Prodi, id=id)
    if request.method == 'POST':
       
        prodi.kode_prodi = request.POST.get('kode_prodi')
        prodi.namaprodi = request.POST.get('namaprodi')
        prodi.namaprodi_en = request.POST.get('namaprodi_en')
        prodi.akreditasi = request.POST.get('akreditasi')
        prodi.noakreditasi = request.POST.get('noakreditasi')
        prodi.gelar = request.POST.get('gelar')
        prodi.pisn = request.POST.get('pisn')
        prodi.save()
        messages.success(request, 'Data Program Studi berhasil diperbarui!')
        return redirect('prodi_list')
    return redirect('prodi_list')

@login_required
def delete_prodi(request, id):
    prodi = get_object_or_404(Prodi, id=id)
    if request.method == 'POST':
        prodi.delete()
        messages.success(request, 'Data Program Studi berhasil dihapus!')
    return redirect('prodi_list')

@login_required
def mahasiswa_list(request):
    mahasiswa = Mahasiswa.objects.select_related('prodi').all()
    prodi_list = Prodi.objects.select_related('fakultas').all().order_by('namaprodi')

    context = {
        'mahasiswa': mahasiswa,
        'prodi_list': prodi_list,
    }
    return render(request, 'data/mahasiswa.html', context)

@login_required
def mahasiswa_add(request):
    if request.method == "POST":
        prodi_id = request.POST.get("prodi")
        nim = request.POST.get("nim")
        nama = request.POST.get("nama")
        nik = request.POST.get("nik")
        tempatlahir = request.POST.get("tempatlahir")
        tgllahir = request.POST.get("tgllahir")
        judul = request.POST.get("judul")
        noijazah = request.POST.get("noijazah")
        notranskip = request.POST.get("notranskip")
        jeniskelamin = request.POST.get("jeniskelamin")
        tglyudisium = request.POST.get("tglyudisium")
        tglwisuda = request.POST.get("tglwisuda")

        if not prodi_id or not nim:
            messages.error(request, "Prodi dan Kode Prodi wajib diisi!")
            return redirect("prodi_add")

        prodi_obj = get_object_or_404(Prodi, id=prodi_id)

        Mahasiswa.objects.create(
            prodi=prodi_obj,
            nim=nim,
            nama=nama,
            nik=nik,
            tempatlahir=tempatlahir,
            tgllahir=tgllahir,
            judul=judul,
            noijazah=noijazah,
            notranskip=notranskip,
            jeniskelamin=jeniskelamin,
            tglyudisium=tglyudisium,
            tglwisuda=tglwisuda,
        )

        messages.success(request, f"Mahasiswa '{nama}' berhasil ditambahkan.")
        return redirect("mahasiswa_list")

    # ✅ ini penting: kirim daftar fakultas ke template
    prodi_list = Prodi.objects.all().order_by("namaprodi")

    context = {
        "title": "Tambah Data Mahasiswa",
        "prodi_list": prodi_list,
    }
    return render(request, "data/mahasiswa.html", context)

@login_required
def update_mahasiswa(request, id):
    mahasiswa = get_object_or_404(Mahasiswa, id=id)
    if request.method == 'POST':
        mahasiswa.nim = request.POST.get('nim')
        mahasiswa.nama = request.POST.get('nama')
        mahasiswa.nik = request.POST.get('nik')
        mahasiswa.tempatlahir = request.POST.get('tempatlahir')
        mahasiswa.tgllahir = request.POST.get('tgllahir')
        mahasiswa.judul = request.POST.get('judul')
        mahasiswa.noijazah = request.POST.get('noijazah')
        mahasiswa.notranskip = request.POST.get('notranskip')
        mahasiswa.jeniskelamin = request.POST.get('jeniskelamin')
        mahasiswa.tglyudisium = request.POST.get('tglyudisium')
        mahasiswa.tglwisuda = request.POST.get('tglwisuda')

        mahasiswa.save()
        messages.success(request, 'Data Program Studi berhasil diperbarui!')
        return redirect('mahasiswa_list')
    return redirect('mahasiswa_list')

@login_required
def delete_mahasiswa(request, id):
    mahasiswa = get_object_or_404(Mahasiswa, id=id)
    if request.method == 'POST':
        mahasiswa.delete()
        messages.success(request, 'Data Mahasiswa berhasil dihapus!')
    return redirect('mahasiswa_list')

@login_required
def matakuliah_list(request):
    prodi_list = Prodi.objects.select_related('fakultas').all().order_by('namaprodi')
    selected_prodi = request.GET.get('prodi')

    matakuliah = None  # Awalnya kosong

    if selected_prodi:
        matakuliah = (
            MataKuliah.objects
            .filter(prodi_id=selected_prodi)
            .select_related('prodi')
            .order_by('semester', 'kodemk', 'angkatan')
        )

    context = {
        'matakuliah': matakuliah,
        'prodi_list': prodi_list,
        'selected_prodi': selected_prodi,
    }
    return render(request, 'data/matakuliah.html', context)

@login_required
def matakuliah_add(request):
    if request.method == "POST":
        prodi_id = request.POST.get("prodi")
        kodemk = request.POST.get("kodemk")
        namamk = request.POST.get("namamk")
        course = request.POST.get("course")
        angkatan = request.POST.get("angkatan")
        semester = request.POST.get("semester")
        sks = request.POST.get("sks")

        if not prodi_id or not kodemk:
            messages.error(request, "Prodi dan Kode Prodi wajib diisi!")
            return redirect("prodi_add")

        prodi_obj = get_object_or_404(Prodi, id=prodi_id)

        Mahasiswa.objects.create(
            prodi=prodi_obj,
            kodemk=kodemk,
            namamk=namamk,
            course=course,
            angkatan=angkatan,
            semester=semester,
            sks=sks,
        )

        messages.success(request, f"Matakuliah '{namamk}' berhasil ditambahkan.")
        return redirect("matakuliah_list")

    # ✅ ini penting: kirim daftar fakultas ke template
    prodi_list = Prodi.objects.all().order_by("namaprodi")

    context = {
        "title": "Tambah Data Matakuliah",
        "prodi_list": prodi_list,
    }
    return render(request, "data/matakuliah.html", context)

@login_required
def update_matakuliah(request, id):
    matakuliah = get_object_or_404(MataKuliah, id=id)
    if request.method == 'POST':
        matakuliah.namamk = request.POST.get('namamk')
        matakuliah.course = request.POST.get('course')
        matakuliah.angkatan = request.POST.get('angkatan')
        matakuliah.semester = request.POST.get('semester')
        matakuliah.sks = request.POST.get('sks')
        matakuliah.save()
        messages.success(request, 'Data Mata Kuliah berhasil diperbarui!')
        return redirect('matakuliah_list')
    return redirect('matakuliah_list')

@login_required
def delete_matakuliah(request, id):
    matakuliah = get_object_or_404(MataKuliah, id=id)
    if request.method == 'POST':
        matakuliah.delete()
        messages.success(request, 'Data Mata Kuliah berhasil dihapus!')
    return redirect('matakuliah_list')

# @login_required
# def nilai_list(request):
#     # Ambil semua data nilai dan relasi mahasiswa & matakuliah agar efisien
#     nilai_list = (
#         Nilai.objects
#         .select_related('mahasiswa', 'matakuliah')
#         .all()
#         .order_by('matakuliah__kodemk', 'mahasiswa__nama')
#     )

#     context = {
#         'title': 'Daftar Nilai Mahasiswa',
#         'nilai_list': nilai_list,
#     }
#     return render(request, 'data/nilai.html', context)

# @login_required
# def mahasiswa_nilai_list(request):
#     mahasiswa = Mahasiswa.objects.select_related('prodi').all().order_by('nama')
#     context = {
#         'title': 'Daftar Nilai Mahasiswa',
#         'mahasiswa': mahasiswa,
#     }
#     return render(request, 'data/nilai.html', context)

# @login_required
# def mahasiswa_nilai_detail(request, mahasiswa_id):
#     mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
#     nilai_list = (
#         Nilai.objects
#         .filter(mahasiswa=mahasiswa)
#         .select_related('matakuliah')
#         .order_by('matakuliah__kodemk')
#     )

#     data = [
#         {
#             'kode_mk': n.matakuliah.kodemk,
#             'nama_mk': n.matakuliah.namamk,
#             'sks': n.matakuliah.sks,
#             'nilai_huruf': n.nilai_huruf,
#             'nilai_angka': n.nilai_angka(),
#         }
#         for n in nilai_list
#     ]

#     # Hitung IPK sederhana jika method belum ada
#     try:
#         ipk = mahasiswa.hitung_ipk()
#     except:
#         total_sks = sum(n.matakuliah.sks for n in nilai_list)
#         total_bobot = sum(n.matakuliah.sks * n.nilai_angka() for n in nilai_list)
#         ipk = round(total_bobot / total_sks, 2) if total_sks > 0 else 0.0

#     return JsonResponse({
#         'mahasiswa': f"{mahasiswa.nim} - {mahasiswa.nama}",
#         'nilai': data,
#         'ipk': ipk,
#     })

def nilai_list(request):
    prodi_id = request.GET.get('prodi')
    mahasiswa_id = request.GET.get('mahasiswa')

    # dropdown data
    prodi_list = Prodi.objects.all().order_by('namaprodi')
    mahasiswa_list = Mahasiswa.objects.all().order_by('nama')

    if prodi_id:
        mahasiswa_list = mahasiswa_list.filter(prodi_id=prodi_id)

    # default: kosong dulu
    nilai_list = Nilai.objects.none()

    # tampilkan jika mahasiswa dipilih
    if mahasiswa_id:
        nilai_list = (
            Nilai.objects.select_related('mahasiswa', 'matakuliah', 'mahasiswa__prodi')
            .filter(mahasiswa_id=mahasiswa_id)
            # urutkan berdasarkan semester lalu kode mata kuliah
            .order_by('matakuliah__semester', 'matakuliah__kodemk')
        )


    context = {
        'prodi_list': prodi_list,
        'mahasiswa_list': mahasiswa_list,
        'nilai_list': nilai_list,
        'selected_prodi': prodi_id,
        'selected_mahasiswa': mahasiswa_id,
    }
    return render(request, 'data/nilai.html', context)

def input_nilai(request):
    prodi_list = Prodi.objects.all()
    mahasiswa_list = None
    matakuliah_list = None
    nilai_exist = {}
    angkatan_list = []

    selected_prodi = request.GET.get('prodi')
    selected_mahasiswa = request.GET.get('mahasiswa')
    selected_angkatan = request.GET.get('angkatan')

    # 🔹 Filter mahasiswa berdasarkan prodi
    if selected_prodi:
        mahasiswa_list = Mahasiswa.objects.filter(prodi_id=selected_prodi).order_by('nama')

        # 🔹 Ambil daftar angkatan hanya dari mata kuliah milik prodi terpilih
        angkatan_list = (
            MataKuliah.objects
            .filter(prodi_id=selected_prodi)
            .values_list('angkatan', flat=True)
            .distinct()
            .order_by('angkatan')
        )

    # 🔹 Filter mata kuliah jika prodi dan angkatan sudah dipilih
    if selected_prodi and selected_angkatan:
        matakuliah_list = (
            MataKuliah.objects
            .filter(prodi_id=selected_prodi, angkatan=selected_angkatan)
            .order_by('semester', 'kodemk')  # urut berdasarkan semester dulu, lalu kode MK
        )

    # 🔹 Ambil nilai yang sudah ada
    if selected_mahasiswa and matakuliah_list:
        nilai_qs = Nilai.objects.filter(mahasiswa_id=selected_mahasiswa)
        nilai_exist = {n.matakuliah_id: n.nilai_huruf for n in nilai_qs}

    # 🔹 Proses penyimpanan nilai
    if request.method == 'POST':
        mahasiswa_id = request.POST.get('mahasiswa')
        mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
        matakuliah_ids = request.POST.getlist('matakuliah_id')
        nilai_huruf_list = request.POST.getlist('nilai_huruf')

        for mk_id, nilai_huruf in zip(matakuliah_ids, nilai_huruf_list):
            mk = MataKuliah.objects.get(id=mk_id)
            Nilai.objects.update_or_create(
                mahasiswa=mahasiswa,
                matakuliah=mk,
                defaults={'nilai_huruf': nilai_huruf}
            )

        messages.success(request, 'Nilai berhasil disimpan atau diperbarui.')

        # 🔹 Arahkan ke halaman input_nilai tanpa parameter (reset)
        return redirect('input_nilai')

    context = {
        'prodi_list': prodi_list,
        'mahasiswa_list': mahasiswa_list,
        'matakuliah_list': matakuliah_list,
        'angkatan_list': angkatan_list,
        'selected_prodi': selected_prodi,
        'selected_mahasiswa': selected_mahasiswa,
        'selected_angkatan': selected_angkatan,
        'nilai_exist': nilai_exist,
    }

    return render(request, 'data/input_nilai.html', context)


def mahasiswa_nilai_view(request):
    prodi_id = request.GET.get('prodi_id')
    prodi_list = Prodi.objects.all().order_by('namaprodi')

    mahasiswa_list = []
    if prodi_id:
        # ambil semua id mahasiswa yang punya nilai
        mhs_ids = Nilai.objects.values_list('mahasiswa_id', flat=True).distinct()
        # filter berdasarkan prodi yang dipilih dan hanya mahasiswa yang punya nilai
        mahasiswa_list = Mahasiswa.objects.filter(prodi_id=prodi_id, id__in=mhs_ids)

    context = {
        'title': 'Daftar Mahasiswa yang Sudah Memiliki Nilai',
        'prodi_list': prodi_list,
        'mahasiswa_list': mahasiswa_list,
        'selected_prodi': prodi_id,
    }
    return render(request, 'data/mahasiswa_nilai.html', context)

# def generate_ijazah(request, mhs_id):
#     mhs = Mahasiswa.objects.select_related('prodi', 'prodi__fakultas').get(id=mhs_id)

#     # ==============================
#     #  REGISTER FONT TIMES NEW ROMAN
#     # ==============================
#     font_path = os.path.join("static", "fonts")
#     pdfmetrics.registerFont(TTFont("Times-Roman", os.path.join(font_path, "times.ttf")))
#     pdfmetrics.registerFont(TTFont("Times-Bold", os.path.join(font_path, "timesbd.ttf")))

#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=landscape(A4),
#         rightMargin=0.5*cm,
#         leftMargin=0.5*cm,
#         topMargin=0.5*cm,
#         bottomMargin=0.5*cm,
#     )

#     # ==============================
#     #  STYLE GLOBAL (Times New Roman 10.5 pt, spasi 1 baris)
#     # ==============================
#     styles = getSampleStyleSheet()
#     base_font = 10.5
#     base_leading = 13

#     styles.add(ParagraphStyle(name='LeftSmall', alignment=TA_LEFT, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
#     styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
#     styles.add(ParagraphStyle(name='BigTitle', alignment=TA_CENTER, fontSize=base_font+3, leading=base_leading+2, spaceAfter=15, fontName='Times-Bold'))
#     styles.add(ParagraphStyle(name='Bold', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Bold'))

#     elements = []

#     # ==============================
#     #  HEADER (pojok kiri atas)
#     # ==============================
#     header_data = [
#         [
#             Paragraph("<b>Nomor Ijazah Nasional</b>", styles['LeftSmall']),
#             Paragraph(": 41125111111111111112", styles['LeftSmall'])
#         ],
#         [
#             Paragraph("Diploma Number", styles['LeftSmall']),
#             ""
#         ],
#         ["", ""],
#         [
#             Paragraph("<b>S.K. Pendirian Perguruan Tinggi</b>", styles['LeftSmall']),
#             Paragraph(": 562 / E / O / 2023", styles['LeftSmall'])
#         ],
#         [
#             Paragraph("Awarding Institution’s License", styles['LeftSmall']),
#             ""
#         ],
#     ]

#     header_table = Table(header_data, colWidths=[7.5*cm, 6*cm])
#     header_table.setStyle(TableStyle([
#         ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#         ('VALIGN', (0,0), (-1,-1), 'TOP'),
#         ('LEFTPADDING', (0,0), (-1,-1), 0),
#         ('RIGHTPADDING', (0,0), (-1,-1), 0),
#         ('TOPPADDING', (0,0), (-1,-1), 1),
#         ('BOTTOMPADDING', (0,0), (-1,-1), 1),
#         ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
#     ]))
#     elements.append(header_table)
#     elements.append(Spacer(1, 20))

#     # ==============================
#     #  IDENTITAS MAHASISWA
#     # ==============================
#     elements.append(Paragraph("<b>Diberikan kepada</b> / is conferred upon", styles['Center']))
#     elements.append(Spacer(1, 6))
#     elements.append(Paragraph(f"<b>{mhs.nama.upper()}</b>", styles['BigTitle']))
#     elements.append(Spacer(1, 6))
#     elements.append(Paragraph("Nomor Induk Mahasiswa / Student Identification Number", styles['Center']))
#     elements.append(Paragraph(f"{mhs.nim}", styles['Center']))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph("Nomor Induk Kependudukan / National Identification Number", styles['Center']))
#     elements.append(Paragraph(f"{mhs.nik}", styles['Center']))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(f"lahir di / born in {mhs.tempatlahir}, {mhs.tgllahir.strftime('%d %B %Y')}", styles['Center']))
#     elements.append(Spacer(1, 15))

#     # ==============================
#     #  PROGRAM STUDI DAN AKREDITASI
#     # ==============================
#     prodi = mhs.prodi
#     fakultas = prodi.fakultas

#     elements.append(Paragraph(
#         f"telah menyelesaikan program Sarjana Terapan pada Program Studi {prodi.namaprodi} "
#         f"({prodi.kode_prodi}), Terakreditasi: {prodi.akreditasi} "
#         f"(Nomor Akreditasi: {prodi.noakreditasi}), "
#         f"Fakultas {fakultas.namafakultas}, Universitas Mayasari Bakti.",
#         styles['Center']
#     ))
#     elements.append(Paragraph(
#         f"has completed the Applied Bachelor Degree program at {prodi.namaprodi_en or prodi.namaprodi} "
#         f"({prodi.kode_prodi}) Study Program, Accredited: {prodi.akreditasi}, "
#         f"{fakultas.namafakultas_en or fakultas.namafakultas}, Mayasari Bakti University.",
#         styles['Center']
#     ))
#     elements.append(Spacer(1, 15))

#     # ==============================
#     #  GELAR
#     # ==============================
#     elements.append(Paragraph("Kepadanya diberikan gelar akademik", styles['Center']))
#     elements.append(Paragraph("Therefore, it is awarded the academic degree of", styles['Center']))
#     elements.append(Spacer(1, 10))
#     elements.append(Paragraph(f"<b>{prodi.gelar or ''}</b>", styles['BigTitle']))
#     elements.append(Spacer(1, 10))
#     elements.append(Paragraph("beserta segala hak dan kehormatan yang melekat pada gelar tersebut.", styles['Center']))
#     elements.append(Paragraph("with all the rights and privileges pertaining thereto.", styles['Center']))
#     elements.append(Spacer(1, 15))

#     # ==============================
#     #  TANGGAL TERBIT
#     # ==============================
#     today = datetime.now()
#     tanggal_indo = today.strftime('%d %B %Y')
#     tanggal_en = today.strftime('%B %d, %Y')
#     elements.append(Paragraph(f"Diterbitkan di Tasikmalaya, {tanggal_indo}.", styles['Center']))
#     elements.append(Paragraph(f"Issued in Tasikmalaya on {tanggal_en}.", styles['Center']))
#     elements.append(Spacer(1, 20))

#     # ==============================
#     #  TANDA TANGAN
#     # ==============================
#     data = [
#         ["Dekan / Dean", "", "Rektor / Rector"],
#         [f"{fakultas.namafakultas} / {fakultas.namafakultas_en or ''}", "", "Universitas Mayasari Bakti"],
#         ["", "", ""],
#         ["", "", ""],
#         [f"{fakultas.namadekan}", "", "Dr. Yusuf Abdullah, S.E., M.M."],
#         [f"NIPT : {fakultas.nipt or '-'}", "", "NIPT : 103.0925.01091969"],
#     ]
#     table = Table(data, colWidths=[9*cm, 1*cm, 9*cm])
#     table.setStyle(TableStyle([
#         ('ALIGN', (0,0), (-1,-1), 'CENTER'),
#         ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
#         ('FONTSIZE', (0,0), (-1,-1), base_font),
#         ('LEADING', (0,0), (-1,-1), base_leading),
#         ('TOPPADDING', (0,0), (-1,-1), 2),
#         ('BOTTOMPADDING', (0,0), (-1,-1), 2),
#     ]))
#     elements.append(table)

#     # ==============================
#     #  BUILD PDF
#     # ==============================
#     doc.build(elements)
#     pdf = buffer.getvalue()
#     buffer.close()

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename="ijazah_{mhs.nim}.pdf"'
#     response.write(pdf)
#     return response

def generate_ijazah(request, mhs_id):
    mhs = get_object_or_404(
        Mahasiswa.objects.select_related("prodi", "prodi__fakultas"),
        id=mhs_id
    )
    prodi = mhs.prodi
    fakultas = prodi.fakultas

    # ========== FONT REGISTER ==========
    font_path = os.path.join("static", "fonts")
    pdfmetrics.registerFont(TTFont("Times-Roman", os.path.join(font_path, "times.ttf")))
    pdfmetrics.registerFont(TTFont("Times-Bold", os.path.join(font_path, "timesbd.ttf")))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.5 * cm,
        leftMargin=0.5 * cm,
        topMargin=0.5 * cm,
        bottomMargin=0.5 * cm,
    )

    # ========== STYLES ==========
    styles = getSampleStyleSheet()
    base_font = 10.5
    base_leading = 13
    styles.add(ParagraphStyle(name='LeftSmall', alignment=TA_LEFT, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='BigTitle', alignment=TA_CENTER, fontSize=base_font+3, leading=base_leading+2, spaceAfter=15, fontName='Times-Bold'))
    styles.add(ParagraphStyle(name='Bold', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Bold'))

    elements = []

    # ========== HEADER (Nomor Ijazah) ==========
    header_data = [
        [Paragraph("<b>Nomor Ijazah Nasional</b>", styles['LeftSmall']),
         Paragraph(f": {mhs.noijazah}", styles['LeftSmall'])],
        [Paragraph("Diploma Number", styles['LeftSmall']), ""],
        ["", ""],
        [Paragraph("<b>S.K. Pendirian Perguruan Tinggi</b>", styles['LeftSmall']),
         Paragraph(f": {fakultas.akrelembaga}", styles['LeftSmall'])],
        [Paragraph("Awarding Institution’s License", styles['LeftSmall']), ""],
    ]

    header_table = Table(header_data, colWidths=[7.5 * cm, 6 * cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # ========== IDENTITAS MAHASISWA ==========
    elements.append(Paragraph("<b>Diberikan kepada</b> / is conferred upon", styles['Center']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>{mhs.nama.upper()}</b>", styles['BigTitle']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Nomor Induk Mahasiswa / Student Identification Number", styles['Center']))
    elements.append(Paragraph(f"{mhs.nim}", styles['Center']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Nomor Induk Kependudukan / National Identification Number", styles['Center']))
    elements.append(Paragraph(f"{mhs.nik}", styles['Center']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"lahir di / born in {mhs.tempatlahir}, {mhs.tgllahir.strftime('%d %B %Y')}", styles['Center']))
    elements.append(Spacer(1, 15))

   # ========== PROGRAM STUDI & FAKULTAS (CENTER + JUSTIFY) ==========
    tgl_yudisium = mhs.tglyudisium or datetime.now()
    tanggal_indo = tgl_yudisium.strftime('%d %B %Y')
    tanggal_en = tgl_yudisium.strftime('%B %d, %Y')

    # Paragraf justify tapi ditaruh di tengah halaman
    style_justify_center = ParagraphStyle(
        'JustifyCenter',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=6,
    )

    # Konten dua bahasa
    paragraf_id = (
        f"Telah menyelesaikan program <b>Sarjana Terapan</b> pada Program Studi "
        f"<b>{prodi.namaprodi}</b> ({prodi.kode_prodi}), Terakreditasi: <b>{prodi.akreditasi}</b> "
        f"(Nomor Akreditasi: {prodi.noakreditasi or '-'}), Fakultas <b>{fakultas.namafakultas}</b>, "
        f"Universitas Mayasari Bakti, pada tanggal <b>{tanggal_indo}</b>."
    )
    paragraf_en = (
        f"Has completed the <b>Applied Bachelor Degree</b> program at "
        f"<b>{prodi.namaprodi_en or prodi.namaprodi}</b> ({prodi.kode_prodi}) Study Program, "
        f"Accredited: <b>{prodi.akreditasi}</b>, "
        f"{fakultas.namafakultas_en or fakultas.namafakultas}, "
        f"Mayasari Bakti University, on <b>{tanggal_en}</b>."
    )

    # Bungkus dalam Table agar paragraf tampil center secara horizontal
    center_table = Table(
        [[Paragraph(paragraf_id, style_justify_center)]],
        colWidths=[22 * cm]  # lebar area teks agar tampak di tengah
    )
    center_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(center_table)
    elements.append(Spacer(1, 8))

    center_table_en = Table(
        [[Paragraph(paragraf_en, style_justify_center)]],
        colWidths=[22 * cm]
    )
    center_table_en.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(center_table_en)
    elements.append(Spacer(1, 15))


    # ========== GELAR ==========
    elements.append(Paragraph("Kepadanya diberikan gelar akademik", styles['Center']))
    elements.append(Paragraph("Therefore, it is awarded the academic degree of", styles['Center']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>{prodi.gelar or '-'}</b>", styles['BigTitle']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("beserta segala hak dan kehormatan yang melekat pada gelar tersebut.", styles['Center']))
    elements.append(Paragraph("with all the rights and privileges pertaining thereto.", styles['Center']))
    elements.append(Spacer(1, 15))

    # ========== TANGGAL ==========
    tgl_yudisium = mhs.tglyudisium or datetime.now()
    tanggal_indo = tgl_yudisium.strftime('%d %B %Y')
    tanggal_en = tgl_yudisium.strftime('%B %d, %Y')
    elements.append(Paragraph(f"Diterbitkan di Tasikmalaya, {tanggal_indo}.", styles['Center']))
    elements.append(Paragraph(f"Issued in Tasikmalaya on {tanggal_en}.", styles['Center']))
    elements.append(Spacer(1, 20))

    # ========== TANDA TANGAN ==========
    data = [
        ["Dekan / Dean", "", "Rektor / Rector"],
        [f"{fakultas.namafakultas} / {fakultas.namafakultas_en or ''}", "", "Universitas Mayasari Bakti"],
        ["", "", ""],
        ["", "", ""],
        [f"{fakultas.namadekan}", "", "Dr. Yusuf Abdullah, S.E., M.M."],
        [f"NIPT : {fakultas.nipt or '-'}", "", "NIPT : 103.0925.01091969"],
    ]
    table = Table(data, colWidths=[9 * cm, 1 * cm, 9 * cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), base_font),
        ('LEADING', (0, 0), (-1, -1), base_leading),
    ]))
    elements.append(table)

    # ========== BUILD PDF ==========
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ijazah_{mhs.nim}.pdf"'
    response.write(pdf)
    return response

def generate_transkrip(request, mhs_id):
    from math import ceil
    # Ambil data mahasiswa beserta prodi & fakultas
    mhs = get_object_or_404(
        Mahasiswa.objects.select_related("prodi", "prodi__fakultas"),
        id=mhs_id
    )
    prodi = mhs.prodi
    fakultas = prodi.fakultas

    # ===================== REGISTER FONT =====================
    font_path = os.path.join("static", "fonts")
    pdfmetrics.registerFont(TTFont("Times-Roman", os.path.join(font_path, "times.ttf")))
    pdfmetrics.registerFont(TTFont("Times-Bold", os.path.join(font_path, "timesbd.ttf")))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=portrait(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    # ===================== STYLES =====================
    styles = getSampleStyleSheet()
    base_font = 10.5
    table_font = 6  # font tabel menjadi 6pt
    table_leading = 1  # spasi baris tabel
    base_leading = 13
    styles.add(ParagraphStyle(name='LeftSmall', alignment=TA_LEFT, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='BigTitle', alignment=TA_CENTER, fontSize=base_font+3, leading=base_leading+2, spaceAfter=15, fontName='Times-Bold'))
    styles.add(ParagraphStyle(name='Bold', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Bold'))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))

    elements = []

    # ===================== HEADER =====================
    elements.append(Paragraph("<b>Transkrip Nilai Mahasiswa</b>", styles['BigTitle']))
    elements.append(Spacer(1, 12))

    # ===================== BIODATA =====================
    biodata_data = [
        ["Nama", mhs.nama],
        ["NIK", mhs.nik],
        ["Tempat, Tanggal Lahir", f"{mhs.tempatlahir}, {mhs.tgllahir.strftime('%d %B %Y')}"],
        ["NIM", mhs.nim],
        ["Fakultas", fakultas.namafakultas],
        ["Program Studi", prodi.namaprodi],
    ]
    biodata_table = Table(biodata_data, colWidths=[150, 300])
    biodata_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), base_font),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(biodata_table)
    elements.append(Spacer(1, 12))

    # ===================== NILAI MAHASISWA =====================
    nilai_list = Nilai.objects.select_related('matakuliah').filter(mahasiswa_id=mhs_id).order_by('matakuliah__semester','matakuliah__kodemk')

    # Bagi menjadi dua list agar tabel berdampingan
    mid_index = ceil(len(nilai_list)/2)
    left_list = nilai_list[:mid_index]
    right_list = nilai_list[mid_index:]

    # Fungsi buat data tabel
    def build_table_data(nilai_sublist):
        data = [["No","Kode MK","Nama Mata Kuliah","Semester","SKS","Nilai"]]
        for i, n in enumerate(nilai_sublist, start=1):
            data.append([i, n.matakuliah.kodemk, n.matakuliah.namamk, n.matakuliah.semester, n.matakuliah.sks, n.nilai_huruf])
        return data

    left_table = Table(build_table_data(left_list), colWidths=[20,50,120,40,30,30], repeatRows=1)
    right_table = Table(build_table_data(right_list), colWidths=[20,50,120,40,30,30], repeatRows=1)

    for t in [left_table, right_table]:
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), table_font),
            ('LEADING', (0,0), (-1,-1), table_leading),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (2,1), (2,-1), 'LEFT'),
        ]))

    # Taruh tabel berdampingan
    combined_table = Table([[left_table, right_table]], colWidths=[doc.width/2-5, doc.width/2-5])
    elements.append(combined_table)
    elements.append(Spacer(1, 12))

    # ===================== IPK =====================
    ipk = mhs.hitung_ipk()
    total_sks = sum([n.matakuliah.sks for n in nilai_list])
    elements.append(Paragraph(f"<b>Total SKS:</b> {total_sks}", styles['LeftSmall']))
    elements.append(Paragraph(f"<b>IPK:</b> {ipk}", styles['LeftSmall']))

    # ===================== BUILD PDF =====================
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="transkrip_{mhs.nim}.pdf"'
    response.write(pdf)
    return response


from xhtml2pdf import pisa
from io import BytesIO
from math import ceil

FOLIO_WIDTH_MM = 210 * 2  # contoh: folio ~ 21 x 33 cm, disesuaikan
FOLIO_HEIGHT_MM = 330

def generate_transkrip_html(request, mhs_id):
    mhs = get_object_or_404(Mahasiswa.objects.select_related("prodi", "prodi__fakultas"), id=mhs_id)
    nilai_list = Nilai.objects.select_related('matakuliah').filter(mahasiswa_id=mhs_id).order_by('matakuliah__semester', 'matakuliah__kodemk')

    mid_index = ceil(len(nilai_list)/2)
    left_list = nilai_list[:mid_index]
    right_list = nilai_list[mid_index:]

    total_sks = sum([n.matakuliah.sks for n in nilai_list])
    ipk = mhs.hitung_ipk()

    context = {
        'mhs': mhs,
        'left_list': left_list,
        'right_list': right_list,
        'total_sks': total_sks,
        'ipk': ipk
    }
    return render(request, 'data/transkrip.html', context)

pdfmetrics.registerFont(TTFont('Times', 'static/fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('Times-Bold', 'static/fonts/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('Times-Italic', 'static/fonts/timesi.ttf'))

def generate_transkrip_pdf(request, mhs_id):
    mahasiswa = Mahasiswa.objects.select_related('prodi', 'prodi__fakultas').get(id=mhs_id)
    buffer = io.BytesIO()

    # Ukuran Folio
    folio_size = (21.5*cm, 33*cm)
    margin = 0.5*cm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=folio_size,
        topMargin=margin,
        bottomMargin=margin,
        leftMargin=margin,
        rightMargin=margin
    )

    elements = []

    # ----------------------------
    # Styles
    # ----------------------------
    style_center = ParagraphStyle(name='Center', fontName='Times', fontSize=8, leading=10, alignment=TA_CENTER)
    style_left = ParagraphStyle(name='Left', fontName='Times', fontSize=8, leading=10, alignment=TA_LEFT)
    style_header = ParagraphStyle(name='Header', fontName='Times', fontSize=8, leading=9, alignment=TA_CENTER)
    style_sub = ParagraphStyle(name='Info', fontName='Times', fontSize=11, leading=10, alignment=TA_CENTER)
    style_info = ParagraphStyle(name='Info', fontName='Times', fontSize=9, leading=10, alignment=TA_LEFT)  # lebih rapat
    style_title = ParagraphStyle(name='Title', fontName='Times-Bold', fontSize=16, leading=16, alignment=TA_CENTER)
    style_summary = ParagraphStyle(name='Summary', fontName='Times', fontSize=12, leading=14, alignment=TA_LEFT)
    style_catatan = ParagraphStyle(name='Catatan', fontName='Times-Italic', fontSize=8, leading=10, alignment=TA_LEFT)
    style_judul = ParagraphStyle(name='Judul', fontName='Times', fontSize=12, leading=14, alignment=TA_LEFT)

    # ----------------------------
    # Header
    # ----------------------------
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("<b>TRANSKRIP AKADEMIK</b>", style_title))
    elements.append(Spacer(1, 0.1*cm))
    elements.append(Paragraph(f"<b>Nomor:</b> {mahasiswa.notranskip}", style_sub))
    elements.append(Spacer(1, 0.5*cm))

    # ----------------------------
    # Data mahasiswa 2 kolom sejajar
    # ----------------------------
    # Gunakan font Times (proporsional) tapi pakai f-string dengan padding sederhana
    style_info = ParagraphStyle(name='Info', fontName='Times', fontSize=9, leading=10, alignment=TA_LEFT)

    # Hitung lebar label maksimum
    max_label_len = 25  # sesuaikan

    def format_label(label, value):
        # tambahkan spasi agar ":" kira-kira rata
        return f"{label:<{max_label_len}}: {value}"

    # Data kiri-kanan
    info_data = [
        [Paragraph(format_label("Nama", mahasiswa.nama), style_info),
        Paragraph(format_label("Fakultas", mahasiswa.prodi.fakultas.namafakultas), style_info)],
        [Paragraph(format_label("Nomor Induk Kependudukan", mahasiswa.nik), style_info),
        Paragraph(format_label("Program Studi", mahasiswa.prodi.namaprodi), style_info)],
        [Paragraph(format_label("Tempat, Tanggal Lahir", f"{mahasiswa.tempatlahir}, {mahasiswa.tgllahir.strftime('%d-%m-%Y')}"), style_info),
        Paragraph(format_label("Akreditasi", mahasiswa.prodi.akreditasi if mahasiswa.prodi.akreditasi else "-"), style_info)],
        [Paragraph(format_label("Nomor Induk Mahasiswa", mahasiswa.nim), style_info),
        Paragraph(format_label("Tanggal Lulus", mahasiswa.tglwisuda.strftime('%d-%m-%Y') if mahasiswa.tglwisuda else "-"), style_info)]
    ]

    # Buat table 2 kolom sederhana (tidak nested)
    info_table = Table(info_data, colWidths=[10*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4))

    # ----------------------------
    # Tabel Nilai Dua Kolom
    # ----------------------------
    nilai_list = list(mahasiswa.nilai_list.select_related('matakuliah').all().order_by('matakuliah__semester', 'matakuliah__kodemk'))
    total_sks = sum([n.matakuliah.sks for n in nilai_list])
    ipk = mahasiswa.hitung_ipk()

    mid = (len(nilai_list)+1)//2
    kolom_kiri = nilai_list[:mid]
    kolom_kanan = nilai_list[mid:]

    nomor_global = list(range(1, len(nilai_list)+1))
    nomor_kiri = nomor_global[:len(kolom_kiri)]
    nomor_kanan = nomor_global[len(kolom_kiri):]

    page_width = folio_size[0] - margin*2
    spacer_width = 0.5*cm
    total_table_width = page_width - spacer_width

    def buat_tabel(nilai_sublist, nomor_list):
        headers = ["No", "Kode MK", "Mata Kuliah", "SKS", "Nilai Huruf", "Angka Mutu"]
        data = [[Paragraph(h, style_header) for h in headers]]
        for idx, n in zip(nomor_list, nilai_sublist):
            if n:
                mk = n.matakuliah
                row = [
                    Paragraph(str(idx), style_center),
                    Paragraph(mk.kodemk, style_center),
                    Paragraph(mk.namamk, style_left),
                    Paragraph(str(mk.sks), style_center),
                    Paragraph(n.nilai_huruf, style_center),
                    Paragraph(str(n.nilai_angka()), style_center)
                ]
                data.append(row)
            else:
                data.append(['', '', '', '', '', ''])
        col_widths = [0.8*cm, 1.4*cm, None, 0.8*cm, 1*cm, 1*cm]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Times'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (0,1), (1,-1), 'CENTER'),
            ('ALIGN', (3,1), (5,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('LEFTPADDING', (0,0), (-1,-1), 1),
            ('RIGHTPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        return t

    tabel_kiri = buat_tabel(kolom_kiri, nomor_kiri)
    tabel_kanan = buat_tabel(kolom_kanan, nomor_kanan)

    spacer_width = 0.2*cm
    table_berdampingan = Table(
        [[tabel_kiri, Spacer(spacer_width,0), tabel_kanan]],
        colWidths=[total_table_width/2, spacer_width, total_table_width/2],
        hAlign='LEFT'
    )
    table_berdampingan.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(KeepTogether(table_berdampingan))
    elements.append(Spacer(1, 4))

    # ----------------------------
    # Footer
    # ----------------------------
    # Catatan kecil
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "*) Bila ada coretan bagaimanapun bentuk/alasannya, maka transkrip ini dinyatakan tidak sah",
        style_catatan
    ))
    elements.append(Spacer(1, 6))

    # Total SKS, IPK, Predikat
    elements.append(Paragraph(f"Total Kredit = {total_sks}", style_summary))
    elements.append(Paragraph(f"Indeks Prestasi Kumulatif (IPK) = {ipk}", style_summary))

    if ipk >= 3.51:
        predikat = "Dengan Pujian"
    elif ipk >= 3.01:
        predikat = "Sangat Memuaskan"
    elif ipk >= 2.76:
        predikat = "Memuaskan"
    else:
        predikat = "Cukup"
    elements.append(Paragraph(f"Predikat Kelulusan = {predikat}", style_summary))
    elements.append(Spacer(1, 4))

    # Judul skripsi
    elements.append(Paragraph(f"Judul Skripsi : {mahasiswa.judul}", style_judul))
    elements.append(Spacer(1, 12))

    # Kolom TTD otomatis
    nama_rektor = mahasiswa.prodi.fakultas.pimpinanpt
    nipt_rektor = "123456789"  # jika belum ada kolom, bisa diisi manual

    # Ambil data rektor
    nama_rektor = mahasiswa.prodi.fakultas.pimpinanpt
    nipt_rektor = "123456789"  # placeholder jika belum ada data

    # Kolom TTD dengan format lengkap
    kota_foto = "\n\n\n\n(Foto)"  # Bisa diganti dengan Image kalau ada

    # Data TTD 3 kolom
    ttd_data = [
        [
            f"Dekan,\nFakultas {mahasiswa.prodi.fakultas.namafakultas}\n\n\n\n\n\n{mahasiswa.prodi.fakultas.namadekan}\nNIPT: {mahasiswa.prodi.fakultas.nipt}",
            kota_foto,
            f"Rektor\nPerguruan Tinggi\n\n\n\n\n\n{nama_rektor}\nNIPT: {nipt_rektor}"
        ]
    ]

    # Lebar masing-masing kolom (sesuaikan)
    col_widths = [8*cm, 4*cm, 8*cm]

    ttd_table = Table(ttd_data, colWidths=col_widths)
    ttd_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(ttd_table)

    # ----------------------------
    # Build PDF
    # ----------------------------
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'Transkrip_{mahasiswa.nim}.pdf')




