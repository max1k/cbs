from django.db import models
from django.db.models import Q

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
		if self.sent_set.filter(Q(Q(prefix='PB2') & Q(result__processed=True))).count():
			return True
		else:
			pb1 = bool(self.sent_set.filter(Q(Q(prefix='PB1') & Q(result__processed=True))))
			resp = bool(self.sent_set.filter(Q(Q(prefix='BV')|Q(prefix='BOS')|Q(prefix='BNS')), result__processed=True))
			if self.prefix in ('PNO','ROO'):
				return pb1
			elif self.prefix in ('RPO','ZNO'):
				return pb1 and resp

	def is_sent(self):
		sent_files = self.sent_set.all().count()
		if sent_files == 0:
			return False
		else:
			success_files = self.sent_set.filter(result__prefix='IZVTUB',result__processed=True).count()
			return sent_files == success_files

class Sent(CommonInfo):
	in_file = models.ForeignKey(File)

class Result(CommonInfo):
	out_file = models.ForeignKey(Sent)
	processed = models.BooleanField(default=False)
	description = models.CharField(max_length=400, null=True)
