from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy

from p311.models import File
from p311.forms import UploadFileForm
from p311.functions import handle_file

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class P311ListView(ListView):
	model = File
	context_object_name = 'files'
	paginate_by = 30

class P311DetailView(DetailView):
	model = File

class UploadFileView(FormView):
	form_class = UploadFileForm
	template_name = 'p311/upload.html'
	success_url = reverse_lazy('p311-success-add')

	def form_valid(self, form):
		handle_file(self.request.FILES['uploaded_file'])
		return super(UploadFileView, self).form_valid(form)

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(UploadFileView, self).dispatch(*args, **kwargs)
