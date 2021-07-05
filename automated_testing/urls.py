from django.conf.urls import url

from automated_testing.api.automated_testing import automated_testing, automated_testing_file_edit, api_test_case_create, test_report_view
from automated_testing.api.fold_manager import FolderManagerView



urlpatterns = [
    url(r'automated_testing', automated_testing.as_view()),
    url(r'automated_file', automated_testing_file_edit.as_view()),
    url(r'swagger_test_case_create', api_test_case_create.as_view()),
    url(r'test_report', test_report_view.as_view()),
    url(r'foldermanage', FolderManagerView.as_view()),
]

