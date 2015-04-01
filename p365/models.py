from django.db import models

class CommonInfo(models.Model):
	name = models.CharField(max_length=100)
	mod_date = models.DateField(auto_now=True)
	doc_date = models.DateField(null=True)
	prefix = models.CharField(max_length=6, null=True)

	def __str__(self):
		return self.name	

class File(CommonInfo):
	orgname = models.CharField(max_length=100)

	def is_done(self):
		return False

	def is_sent(self):
		return False

class Sent(CommonInfo):
	in_file = models.ForeignKey(File)

class Result(CommonInfo):
	out_file = models.ForeignKey(Sent)
	processed = models.BooleanField(default=False)
	description = models.CharField(max_length=400, null=True)
