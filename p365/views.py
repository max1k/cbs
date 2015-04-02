#from django.shortcuts import render
from django.views.generic import ListView, FormView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from p365.models import File
from p365.forms import UploadFileForm
from p365.functions import handle_file
from datetime import datetime

class P365ListView(ListView):
	model=File
	context_object_name='files'
	paginate_by=18

	def get_queryset(self):
		qs=self.model.objects.all().order_by('-doc_date')
		return qs

class P365UnansweredListView(P365ListView):
	paginate_by=0

	def get_queryset(self):
		qs=super(P365ListView, self).get_queryset().filter(sent__result__isnull=True)
		return qs

class P365OrgListView(P365ListView):
	def get_queryset(self):
		qs = super(P365ListView, self).get_queryset().filter(orgname=self.kwargs['orgname'])
		return qs

class P365DateListView(P365ListView):
	paginate_by = 0
	def get_queryset(self):
		doc_date=datetime.strptime('{0}/{1}/{2}'.format(self.kwargs['year'],self.kwargs['month'],self.kwargs['day']),'%Y/%m/%d')
		qs = super(P365ListView, self).get_queryset().filter(doc_date=doc_date)
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

class P365DetailView(DetailView):
	model = File