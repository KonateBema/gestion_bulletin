from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('lmd/', include('lmd.urls')),
  path('lmd/', include('lmd.urls')),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('prof-dashboard/', views.dashboard_prof, name='dashboard_prof'),
    path('etudiant-dashboard/', views.dashboard_etudiant, name='dashboard_etudiant'),

    path('register/', views.register_user, name='register'),

    # BULLETIN
    path('bulletin/', views.bulletin_etudiant, name='bulletin_etudiant'),
    path('bulletin/classe/<int:classe_id>/', views.bulletin_classe, name='bulletin_classe'),
    path('bulletin/pdf/', views.download_bulletin_pdf, name='bulletin_pdf'),
    path("bulletins/", views.bulletin_list, name="bulletin_list"),

    # ETUDIANTS
    path('etudiants/', views.etudiant_list, name="etudiant_list"),
    path('etudiants/add/', views.etudiant_create, name="etudiant_add"),
    path('etudiants/edit/<int:id>/', views.etudiant_update, name="etudiant_edit"),
    path('etudiants/delete/<int:id>/', views.etudiant_delete, name="etudiant_delete"),

    # CLASSES
    path('classes/', views.classe_list, name="classe_list"),
    path('classes/add/', views.classe_create, name="classe_add"),
    path('classes/edit/<int:pk>/', views.classe_edit, name="classe_edit"),
    path('classes/delete/<int:pk>/', views.classe_delete, name="classe_delete"),

    # MATIERES
    path('matieres/', views.matiere_list, name="matiere_list"),
    path('matieres/add/', views.matiere_create, name="matiere_add"),
    path('matieres/edit/<int:id>/', views.matiere_update, name='matiere_edit'),
    path('matieres/delete/<int:id>/', views.matiere_delete, name='matiere_delete'),

    # AFFECTATIONS
    path("affectations/", views.affectation_list, name="affectation_list"),
    path("affectations/add/", views.affectation_create, name="affectation_add"),
    path("affectations/delete/<int:id>/", views.affectation_delete, name="affectation_delete"),

    # NOTES
    path("notes/", views.note_list, name="note_list"),
    path("notes/add/", views.note_create, name="note_add"),
    path("notes/edit/<int:id>/", views.note_update, name="note_edit"),
    path("notes/delete/<int:id>/", views.note_delete, name="note_delete"),


    path('bulletin/pdf/<int:etudiant_id>/<int:classe_id>/',views.download_bulletin_pdf, name='bulletin_pdf'),
 
]