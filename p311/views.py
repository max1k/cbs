#from django.shortcuts import render
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
	paginate_by = 15

	def get_queryset(self):
		qs = File.objects.all().order_by('-doc_date')
		return qs

class P311OrgListView(P311ListView):
	def get_queryset(self):
		qs = super(P311ListView, self).get_queryset().filter(orgname=self.kwargs['orgname'])
		return qs

class P311UnansweredListView(P311ListView):
	paginate_by = 200
	def get_queryset(self):
		qs = File.objects.all()
		such_fiz=qs.filter(name__startswith='SFC').filter(result__service='nal')
		such_ur= qs.filter(name__startswith='SBC').filter(result__service='nal').filter(result__service='pfr').filter(result__service='fss')
		return qs.exclude(pk__in=such_fiz).exclude(pk__in=such_ur)

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