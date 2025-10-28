from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# -------------------------------
# Custom User
# -------------------------------
class User(AbstractUser):
    def __str__(self):
        return self.username

# ==========================
# Fakultas
# ==========================
class Fakultas(models.Model):
    kodept = models.CharField(max_length=10)
    pimpinanpt = models.CharField(max_length=100)
    akrelembaga = models.CharField(max_length=100)
    kodefakultas = models.CharField(max_length=50, unique=True)
    namafakultas = models.CharField(max_length=150)
    namafakultas_en = models.CharField(max_length=150, blank=True, null=True)
    dekan = models.CharField(max_length=150)
    dekan_en = models.CharField(max_length=150, blank=True, null=True)
    namadekan = models.CharField(max_length=150)
    nipt = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Fakultas"

    def __str__(self):
        return f"{self.kodefakultas} - {self.namafakultas}"


# ==========================
# Program Studi
# ==========================
class Prodi(models.Model):
    fakultas = models.ForeignKey(Fakultas, on_delete=models.CASCADE, related_name='prodi')
    kode_prodi = models.CharField(max_length=10, unique=True)
    namaprodi = models.CharField(max_length=150)
    namaprodi_en = models.CharField(max_length=150, blank=True, null=True)
    akreditasi = models.CharField(max_length=50)
    noakreditasi = models.CharField(max_length=100, blank=True, null=True)
    gelar = models.CharField(max_length=100, blank=True, null=True)
    pisn = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Program Studi"

    def __str__(self):
        return f"{self.namaprodi} ({self.kode_prodi})"


# ==========================
# Mahasiswa
# ==========================
class Mahasiswa(models.Model):
    prodi = models.ForeignKey(Prodi, on_delete=models.CASCADE, related_name='mahasiswa')
    nim = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=150)
    judul = models.CharField(max_length=255)
    noijazah = models.CharField(max_length=25)
    notranskip = models.CharField(max_length=25)
    nik = models.CharField(max_length=20)
    tempatlahir = models.CharField(max_length=100)
    tgllahir = models.DateField()
    jeniskelamin = models.CharField(
        max_length=1,
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')]
    )
    tglyudisium = models.DateField(blank=True, null=True)
    tglwisuda = models.DateField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Mahasiswa"

    def __str__(self):
        return f"{self.nim} - {self.nama}"

    def hitung_ipk(self):
        nilai_list = self.nilai_list.select_related('matakuliah')
        total_sks = sum([n.matakuliah.sks for n in nilai_list])
        if total_sks == 0:
            return 0.0
        total_bobot = sum([n.nilai_angka() * n.matakuliah.sks for n in nilai_list])
        return round(total_bobot / total_sks, 2)

# ==========================
# Mata Kuliah
# ==========================
class MataKuliah(models.Model):
    prodi = models.ForeignKey(Prodi, on_delete=models.CASCADE, related_name='matakuliah')
    kodemk = models.CharField(max_length=10, unique=True)
    namamk = models.CharField(max_length=150)
    course = models.CharField(max_length=150)
    angkatan = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, default='')
    sks = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Mata Kuliah"

    def __str__(self):
        return f"{self.kodemk} - {self.namamk}"


# ==========================
# Nilai
# ==========================
class Nilai(models.Model):
    NILAI_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]

    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE, related_name='nilai_list')
    matakuliah = models.ForeignKey(MataKuliah, on_delete=models.CASCADE, related_name='nilai_list')
    nilai_huruf = models.CharField(max_length=1, choices=NILAI_CHOICES)

    def __str__(self):
        return f"{self.mahasiswa.nama} - {self.matakuliah.namamk} ({self.nilai_huruf})"

    def nilai_angka(self):
        mapping = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.0}
        return mapping.get(self.nilai_huruf, 0.0)