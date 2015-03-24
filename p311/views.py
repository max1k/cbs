from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy

from p311.models import File
from p311.forms import UploadFileForm


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
		return super(UploadFileView, self).form_valid(form)