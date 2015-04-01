#from django.shortcuts import render
from django.views.generic import ListView, FormView
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from p365.models import File
from p365.forms import UploadFileForm
from p365.functions import handle_file

class P365ListView(ListView):
	model=File
	context_object_name='files'
	paginate_by='18'

	def get_queryset(self):
		qs=self.model.objects.all().order_by('-doc_date')
		return qs

class UploadFileView(FormView):
	form_class = UploadFileForm
	template_name = 'p365/upload.html'
	success_url = reverse_lazy('p365-success-add')

	def form_valid(self, form):
		handle_file(self.request.FILES['uploaded_file'])
		return super(UploadFileView, self).form_valid(form)

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(UploadFileView, self).dispatch(*args, **kwargs)