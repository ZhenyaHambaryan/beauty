from django.db import models

class File(models.Model):
      file_url = models.FileField(upload_to='static/images/%Y/%m/%d/', 
                              null=False, blank=False, max_length = 1000)
      def __str__(self):
            return self.image_url