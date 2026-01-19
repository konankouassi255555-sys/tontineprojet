"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import home, dashboard, calendar_view, accueil_view
from accounts.views import register_view, profile_view,profile_edit_view
from tontines.views import tontine_create_view, tontine_list_view, tontine_detail_view
from accounts.views import CustomPasswordChangeView, CustomPasswordChangeDoneView
from tontines.views import (
    tontine_list_view, tontine_create_view, tontine_detail_view,
    tontine_edit_view, tontine_activate_view, tontine_manage_view,
    tontine_invite_view, tontine_change_member_role, 
    tontine_change_member_status, tontine_remove_member, allocate_beneficiary_view
)
from tontines.views import (
    tontine_join_view, tontine_contribute_view, wallet_deposit_view,
    tontine_pay_from_wallet, vault_create_view, wallet_overview, vaults_overview
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accueil/', accueil_view, name='accueil'),
    path('dashboard/', dashboard, name='dashboard'),
    path('calendar/', calendar_view, name='calendar'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('tontines/', tontine_list_view, name='tontine_list'),
    path('tontines/create/', tontine_create_view, name='tontine_create'),
    path('tontines/<int:tontine_id>/', tontine_detail_view, name='tontine_detail'),
    path('password/change/', 
         CustomPasswordChangeView.as_view(), 
         name='change_password'),
    path('password/change/done/', 
         CustomPasswordChangeDoneView.as_view(), 
         name='password_change_done'),
     # URLs pour les tontines
    path('tontines/', tontine_list_view, name='tontine_list'),
    path('tontines/create/', tontine_create_view, name='tontine_create'),
    path('tontines/<int:tontine_id>/', tontine_detail_view, name='tontine_detail'),
    path('tontines/<int:tontine_id>/edit/', tontine_edit_view, name='tontine_edit'),
    path('tontines/<int:tontine_id>/activate/', tontine_activate_view, name='tontine_activate'),
    path('tontines/<int:tontine_id>/manage/', tontine_manage_view, name='tontine_manage'),
    path('tontines/<int:tontine_id>/allocate/', allocate_beneficiary_view, name='allocate_beneficiary'),
    path('tontines/<int:tontine_id>/invite/', tontine_invite_view, name='tontine_invite'),
    path('tontines/join/', tontine_join_view, name='tontine_join'),

     # URLs API pour la gestion des membres
    path('tontines/<int:tontine_id>/member/<int:member_id>/change-role/', 
         tontine_change_member_role, name='tontine_change_member_role'),
    path('tontines/<int:tontine_id>/member/<int:member_id>/change-status/', 
         tontine_change_member_status, name='tontine_change_member_status'),
    path('tontines/<int:tontine_id>/member/<int:member_id>/remove/', 
         tontine_remove_member, name='tontine_remove_member'),
    path('tontines/<int:tontine_id>/contribute/', tontine_contribute_view, name='tontine_contribute'),
    path('tontines/<int:tontine_id>/pay-wallet/', tontine_pay_from_wallet, name='tontine_pay_wallet'),
    path('wallet/deposit/', wallet_deposit_view, name='wallet_deposit'),
    path('wallet/topup/', wallet_deposit_view, name='wallet_topup'),
    path('wallet/', wallet_overview, name='wallet_overview'),
    path('vaults/', vaults_overview, name='vaults_overview'),
    path('vault/create/', vault_create_view, name='vault_create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
