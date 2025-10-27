from .models import *
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from django.db.models import IntegerField, F
from django.db.models.functions import Cast, Substr, Length


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
    matakuliah = MataKuliah.objects.select_related('prodi').all()
    prodi_list = Prodi.objects.select_related('fakultas').all().order_by('namaprodi')

    context = {
        'matakuliah': matakuliah,
        'prodi_list': prodi_list,
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
        matakuliah.kodemk = request.POST.get('kodemk')
        matakuliah.namamk = request.POST.get('namamk')
        matakuliah.course = request.POST.get('course')
        matakuliah.angkatan = request.POST.get('angkatan')
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
            .annotate(
                # ambil panjang kode MK
                kode_len=Length('matakuliah__kodemk'),
                # ambil bagian angka setelah 2 huruf pertama (misal BD001 -> 001)
                kode_mk_num=Cast(Substr('matakuliah__kodemk', 3, Length('matakuliah__kodemk') - 2), IntegerField())
            )
            .order_by('mahasiswa__nama', 'kode_mk_num')
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
    selected_prodi = request.GET.get('prodi')
    selected_mahasiswa = request.GET.get('mahasiswa')
    selected_angkatan = request.GET.get('angkatan')

    if selected_prodi:
        mahasiswa_list = Mahasiswa.objects.filter(prodi_id=selected_prodi)

    if selected_prodi and selected_angkatan:
        matakuliah_list = MataKuliah.objects.filter(
            prodi_id=selected_prodi, angkatan=selected_angkatan
        )

    if selected_mahasiswa and matakuliah_list:
        nilai_qs = Nilai.objects.filter(mahasiswa_id=selected_mahasiswa)
        nilai_exist = {n.matakuliah_id: n.nilai_huruf for n in nilai_qs}

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

        # 🔧 Redirect yang benar:
        url = reverse('input_nilai')
        return redirect(f'{url}?prodi={selected_prodi}&mahasiswa={mahasiswa_id}&angkatan={selected_angkatan}')

    context = {
        'prodi_list': prodi_list,
        'mahasiswa_list': mahasiswa_list,
        'matakuliah_list': matakuliah_list,
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

def generate_ijazah(request, mhs_id):
    mhs = Mahasiswa.objects.select_related('prodi', 'prodi__fakultas').get(id=mhs_id)

    # ==============================
    #  REGISTER FONT TIMES NEW ROMAN
    # ==============================
    font_path = os.path.join("static", "fonts")
    pdfmetrics.registerFont(TTFont("Times-Roman", os.path.join(font_path, "times.ttf")))
    pdfmetrics.registerFont(TTFont("Times-Bold", os.path.join(font_path, "timesbd.ttf")))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.5*cm,
        leftMargin=0.5*cm,
        topMargin=0.5*cm,
        bottomMargin=0.5*cm,
    )

    # ==============================
    #  STYLE GLOBAL (Times New Roman 10.5 pt, spasi 1 baris)
    # ==============================
    styles = getSampleStyleSheet()
    base_font = 10.5
    base_leading = 13

    styles.add(ParagraphStyle(name='LeftSmall', alignment=TA_LEFT, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Roman'))
    styles.add(ParagraphStyle(name='BigTitle', alignment=TA_CENTER, fontSize=base_font+3, leading=base_leading+2, spaceAfter=15, fontName='Times-Bold'))
    styles.add(ParagraphStyle(name='Bold', alignment=TA_CENTER, fontSize=base_font, leading=base_leading, fontName='Times-Bold'))

    elements = []

    # ==============================
    #  HEADER (pojok kiri atas)
    # ==============================
    header_data = [
        [
            Paragraph("<b>Nomor Ijazah Nasional</b>", styles['LeftSmall']),
            Paragraph(": 41125111111111111112", styles['LeftSmall'])
        ],
        [
            Paragraph("Diploma Number", styles['LeftSmall']),
            ""
        ],
        ["", ""],
        [
            Paragraph("<b>S.K. Pendirian Perguruan Tinggi</b>", styles['LeftSmall']),
            Paragraph(": 562 / E / O / 2023", styles['LeftSmall'])
        ],
        [
            Paragraph("Awarding Institution’s License", styles['LeftSmall']),
            ""
        ],
    ]

    header_table = Table(header_data, colWidths=[7.5*cm, 6*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # ==============================
    #  IDENTITAS MAHASISWA
    # ==============================
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

    # ==============================
    #  PROGRAM STUDI DAN AKREDITASI
    # ==============================
    prodi = mhs.prodi
    fakultas = prodi.fakultas

    elements.append(Paragraph(
        f"telah menyelesaikan program Sarjana Terapan pada Program Studi {prodi.namaprodi} "
        f"({prodi.kode_prodi}), Terakreditasi: {prodi.akreditasi} "
        f"(Nomor Akreditasi: {prodi.noakreditasi}), "
        f"Fakultas {fakultas.namafakultas}, Universitas Mayasari Bakti.",
        styles['Center']
    ))
    elements.append(Paragraph(
        f"has completed the Applied Bachelor Degree program at {prodi.namaprodi_en or prodi.namaprodi} "
        f"({prodi.kode_prodi}) Study Program, Accredited: {prodi.akreditasi}, "
        f"{fakultas.namafakultas_en or fakultas.namafakultas}, Mayasari Bakti University.",
        styles['Center']
    ))
    elements.append(Spacer(1, 15))

    # ==============================
    #  GELAR
    # ==============================
    elements.append(Paragraph("Kepadanya diberikan gelar akademik", styles['Center']))
    elements.append(Paragraph("Therefore, it is awarded the academic degree of", styles['Center']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>{prodi.gelar or ''}</b>", styles['BigTitle']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("beserta segala hak dan kehormatan yang melekat pada gelar tersebut.", styles['Center']))
    elements.append(Paragraph("with all the rights and privileges pertaining thereto.", styles['Center']))
    elements.append(Spacer(1, 15))

    # ==============================
    #  TANGGAL TERBIT
    # ==============================
    today = datetime.now()
    tanggal_indo = today.strftime('%d %B %Y')
    tanggal_en = today.strftime('%B %d, %Y')
    elements.append(Paragraph(f"Diterbitkan di Tasikmalaya, {tanggal_indo}.", styles['Center']))
    elements.append(Paragraph(f"Issued in Tasikmalaya on {tanggal_en}.", styles['Center']))
    elements.append(Spacer(1, 20))

    # ==============================
    #  TANDA TANGAN
    # ==============================
    data = [
        ["Dekan / Dean", "", "Rektor / Rector"],
        [f"{fakultas.namafakultas} / {fakultas.namafakultas_en or ''}", "", "Universitas Mayasari Bakti"],
        ["", "", ""],
        ["", "", ""],
        [f"{fakultas.namadekan}", "", "Dr. Yusuf Abdullah, S.E., M.M."],
        [f"NIPT : {fakultas.nipt or '-'}", "", "NIPT : 103.0925.01091969"],
    ]
    table = Table(data, colWidths=[9*cm, 1*cm, 9*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), base_font),
        ('LEADING', (0,0), (-1,-1), base_leading),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(table)

    # ==============================
    #  BUILD PDF
    # ==============================
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ijazah_{mhs.nim}.pdf"'
    response.write(pdf)
    return response



