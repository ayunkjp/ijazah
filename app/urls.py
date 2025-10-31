from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    #Object Login
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('fakultas_list/', views.fakultas_list, name='fakultas_list'),
    path('fakultas_add/', views.fakultas_add, name='fakultas_add'),
    path('update_fakultas/<int:id>', views.update_fakultas, name='update_fakultas'),
    path('delete_fakultas/<int:id>', views.delete_fakultas, name='delete_fakultas'),

    path('prodi_list/', views.prodi_list, name='prodi_list'),
    path('prodi_add/', views.prodi_add, name='prodi_add'),
    path('update_prodi/<int:id>', views.update_prodi, name='update_prodi'),
    path('delete_prodi/<int:id>', views.delete_prodi, name='delete_prodi'),

    path('mahasiswa_list/', views.mahasiswa_list, name='mahasiswa_list'),
    path('mahasiswa_add/', views.mahasiswa_add, name='mahasiswa_add'),
    path('update_mahasiswa/<int:id>', views.update_mahasiswa, name='update_mahasiswa'),
    path('delete_mahasiswa/<int:id>', views.delete_mahasiswa, name='delete_mahasiswa'),

    path('matakuliah_list/', views.matakuliah_list, name='matakuliah_list'),
    path('matakuliah_add/', views.matakuliah_add, name='matakuliah_add'),
    path('update_matakuliah/<int:id>', views.update_matakuliah, name='update_matakuliah'),
    path('delete_matakuliah/<int:id>', views.delete_matakuliah, name='delete_matakuliah'),

    #path('nilai/', views.nilai_list, name='nilai_list'),
    #path('nilai/', views.mahasiswa_nilai_list, name='mahasiswa_nilai_list'),
    #path('nilai/detail/<int:mahasiswa_id>/', views.mahasiswa_nilai_detail, name='mahasiswa_nilai_detail'),
    path('nilai/', views.nilai_list, name='nilai_list'),
    path('input_nilai/', views.input_nilai, name='input_nilai'),
    path('mahasiswa/nilai/', views.mahasiswa_nilai_view, name='mahasiswa_nilai'),
    path('mahasiswa/<int:mhs_id>/generate-ijazah/', views.generate_ijazah, name='generate_ijazah'),
    #path('mahasiswa/<int:mhs_id>/generate-transkrip/', views.generate_transkrip, name='generate_transkrip'),

    #path('mahasiswa/<int:mhs_id>/transkrip/', views.generate_transkrip_html, name='generate_transkrip_html'),
    path('mahasiswa/<int:mhs_id>/transkrip-pdf/', views.generate_transkrip_pdf, name='generate_transkrip_pdf'),
    path('mahasiswa/<int:mhs_id>/transkrip-pdfen/', views.generate_transkrip_pdfen, name='generate_transkrip_pdfen'),

]