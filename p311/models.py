from django.db import models

# Create your models here.

class CommonInfo(models.Model):
	name = models.CharField(max_length=100)
	mod_date = models.DateField(auto_now=True)
	doc_date = models.DateField(null=True)

	def __str__(self):
		return self.name	

class File(CommonInfo):
	orgname = models.CharField(max_length=100)

	def is_done(self):
		if self.name.upper().startswith('SFC'):
			if self.result_set.filter(service='nal').count():
				return True
		elif self.name.upper().startswith('SBC'):
			if (self.result_set.filter(service='nal').count() and
				self.result_set.filter(service='pfr').count() and
				self.result_set.filter(service='fss').count()):
				return True
		return False

	def is_sent(self):
		return bool(self.result_set.filter(service='cb').filter(processed='True').count())


class Result(CommonInfo):
	src_file = models.ForeignKey(File)
	service = models.CharField(max_length=3)
	processed = models.BooleanField(default=False)
	description = models.CharField(max_length=250, null=True)