from django.db import models

# Create your models here.

class CommonInfo(models.Model):
	name = models.CharField(max_length=100)
	date = models.DateField(auto_now=True)

	def __str__(self):
		return self.name	

class File(CommonInfo):
	orgname = models.CharField(max_length=100)

class Result(CommonInfo):
	src_file = models.ForeignKey(File)
	service = models.CharField(max_length=3)
	processed = models.BooleanField(default=False)
	description = models.CharField(max_length=250)