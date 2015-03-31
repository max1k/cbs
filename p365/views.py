#from django.shortcuts import render
from django.views.generic import ListView

from p365.models import File

class P365ListView(ListView):
	model=File
	context_object_name='file'
	paginate_by='18'

	def get_queryset(self):
		qs=self.model.objects.all().order_by('-doc_date')
		return qs