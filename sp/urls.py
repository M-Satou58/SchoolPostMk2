from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.indexView, name='index'),
    path('teacher/login/', auth_views.LoginView.as_view(template_name='login/teacher-login.html'), name='t-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='main/index01.html'), name='logout'),
    path('register/teacher/', views.registerTeacherView, name='t-register'),
    path('register/student/', views.registerStudentView, name='s-register'),
    
    path('economy/', views.economyView, name='economy'),
    path('economy/active/<str:pk>/', views.setActive, name='set-active-economy'),
    path('economy/inactive/<str:pk>/', views.setInactive, name='set-inactive-economy'),

    path('settings/account/account-settings/', views.accountSettingsView, name='account-settings'),
    path('settings/school/school-settings/<str:user>/', views.schoolSettingsView, name='school-settings'),

    path('rules/jobs/<str:user>/', views.jobsView, name='jobs'),
    path('rules/jobs/update/<str:user>/<str:pk>/', views.updateJobsView, name='update-jobs'),
    path('rules/jobs/delete/<str:user>/<str:pk>/', views.deleteJobsView, name='delete-jobs'),

    path('rules/opportunities/<str:user>/', views.opportunitiesView, name='opportunities'),
    path('rules/opportunities/update/<str:user>/<str:pk>/', views.updateOpportunitiesView, name='update-opportunities'),
    path('rules/opportunities/delete/<str:user>/<str:pk>/', views.deleteOpportunitiesView, name='delete-opportunities'),

    path('rules/house-rules/<str:user>/', views.houseRulesView, name='house-rules'),
    path('rules/house-rules/update/<str:user>/<str:pk>/', views.updateHouseRulesView, name='update-house-rules'),
    path('rules/house-rules/delete/<str:user>/<str:pk>/', views.deleteHouseRulesView, name='delete-house-rules'),

    path('rules/rent/<str:user>/', views.rentView, name='rent'),

    path('monitoring/student/<str:user>/', views.studentMonitoringView, name='m-student'),

    path('item-store/<str:user>/', views.itemStoreView, name='item-store'),
    path('item-store/delete/<str:user>/<str:pk>/', views.deleteItemStoreView, name='delete-item-store'),

    path('materials/bill/<str:user>/', views.billView, name='bill'),
    path('materials/bill/money-circulation/<str:user>/', views.moneyCirculationView, name='money-circulation'),
    path('materials/bill/print-bill/<str:user>/<str:pk>/', views.printBillView, name='print-bill'),
    path('materials/bill/print-bill-10/<str:user>/<str:pk>/', views.printTenBillsView, name='print-bill-10'),
    path('materials/bill/print-bill-20/<str:user>/<str:pk>/', views.printTwentyBillsView, name='print-bill-20'),

    path('materials/jobs/print/<str:user>/', views.printJobsView, name='print-jobs'),
    path('materials/business-envelope/print/<str:user>/', views.printBusinessEnvelopeView, name='print-business-envelope'),
    path('materials/house-rule/print/<str:user>/', views.printHouseRulesView, name='print-house-rules'),
    path('materials/certificate/<str:user>/', views.certificateView, name='certificate'),
    path('materials/certificate/print/<str:user>/', views.printCertificateView, name='print-certificate'),

    path('materials/debriefing-session/<str:user>/', views.debriefingSessionView, name='debriefing-session'),
    path('materials/debriefing-session/update/<str:user>/<str:pk>/', views.updateDebriefingSessionView, name='update-debriefing-session'),
    path('materials/debriefing-session/delete/<str:user>/<str:pk>/', views.deleteDebriefingSessionView, name='delete-debriefing-session'),
    path('materials/debriefing-session/print/<str:user>/', views.printDebriefingSessionView, name='print-debriefing-session'),


    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='passwords/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="passwords/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='passwords/password_reset_complete.html'), name='password_reset_complete'),
    path("password-reset", views.password_reset_request, name="password-reset"),


    

    

]