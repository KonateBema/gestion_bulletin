from django.urls import path
from . import views

urlpatterns = [

    # =====================
    # NIVEAUX
    # =====================
    path('niveaux/', views.niveau_list, name='niveau_lmd_list'),
    path('niveaux/add/', views.niveau_add, name='niveau_lmd_add'),

    # =====================
    # FILIERES
    # =====================
    path('filieres/', views.filiere_list, name='filiere_lmd_list'),
    path('filieres/add/', views.filiere_add, name='filiere_lmd_add'),
     path('filieres/edit/<int:pk>/', views.filiere_edit, name='filiere_lmd_edit'),
    path('filieres/delete/<int:pk>/', views.filiere_delete, name='filiere_lmd_delete'),

    # =====================
    # CLASSES LMD
    # =====================
    path('classes/', views.classe_list, name='classe_lmd_list'),
    path('classes/add/', views.classe_add, name='classe_lmd_add'),

    # UE
    path('ue/', views.ue_list, name='ue_list'),
    path('ue/add/', views.ue_add, name='ue_add'),
    path('ue/edit/<int:pk>/', views.ue_edit, name='ue_edit'),
    path('ue/delete/<int:pk>/', views.ue_delete, name='ue_delete'),

    # =====================
    # ECUE
    # =====================
    # path('ecue/', views.ecue_list, name='ecue_list'),
    # path('ecue/add/', views.ecue_add, name='ecue_add'),


    path('ecue/', views.ecue_list, name='ecue_list'),
    path('ecue/add/', views.ecue_add, name='ecue_add'),
    path('ecue/edit/<int:pk>/', views.ecue_edit, name='ecue_edit'),
    path('ecue/delete/<int:pk>/', views.ecue_delete, name='ecue_delete'),

    # =====================
    # NOTES LMD
    # =====================
    # path('notes/', views.note_lmd_list, name='note_lmd_list'),
    path('notes/add/', views.note_lmd_add, name='note_lmd_add'),

    # =====================
    # BULLETINS LMD
    # =====================
    # path('bulletins/', views.bulletin_lmd_list, name='bulletin_lmd_list'),
    
    path('bulletins-lmd/',views.bulletin_lmd_list,name='bulletin_lmd_list'),
     

    # =====================
    # ETUDIANTS LMD
    # =====================
    path('etudiants/', views.etudiant_lmd_list, name='etudiant_lmd_list'),
    path('etudiants/add/', views.etudiant_lmd_add, name='etudiant_lmd_add'),
    path("etudiants/<int:pk>/edit/", views.etudiant_lmd_update, name="etudiant_lmd_update"),
    path("etudiants/<int:pk>/delete/", views.etudiant_lmd_delete, name="etudiant_lmd_delete"),
    path("etudiants/<int:pk>/edit/", views.etudiant_lmd_update, name="etudiant_lmd_edit"),


    path('bulletin-lmd/<int:etudiant_id>/',views.bulletin_lmd_pdf,name='bulletin_lmd_pdf'),
    path('bulletins/<int:etudiant_id>/', views.bulletin_lmd_pdf, name='bulletin_lmd_pdf'),

    path('notes-lmd/', views.note_lmd_list, name='note_lmd_list'),
    path('notes-lmd/add/', views.note_lmd_add, name='note_lmd_add'),
    path('notes-lmd/edit/<int:pk>/', views.note_lmd_edit, name='note_lmd_edit'),
    path('notes-lmd/delete/<int:pk>/', views.note_lmd_delete, name='note_lmd_delete'),

]