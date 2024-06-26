from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

# Create your models here.
# Banners
class Banners(models.Model):
	img=models.ImageField(upload_to="banners/")
	alt_text=models.CharField(max_length=150)

	class Meta:
		verbose_name_plural='Banners'

	def __str__(self):
		return self.alt_text

	def image_tag(self):
		return mark_safe(f"<img src='{self.img.url}' width='80' />")

# Services to offer
class Service(models.Model):
	title=models.CharField(max_length=150)
	detail=models.TextField()
	img=models.ImageField(upload_to="services/",null=True)

	def __str__(self):
		return self.title

	def image_tag(self):
		return mark_safe(f"<img src='{self.img.url}' width='80' />")

# Pages
class Page(models.Model):
    title = models.CharField(max_length=200)
    detail = models.TextField()
    
    def __str__(self):
        return self.title
    
# FAQ
class Faq(models.Model):
    quest =models.CharField(max_length=200)
    ans = models.TextField()
    
    def __str__(self):
        return self.quest
    

# Enquiry Model
class Enquiry(models.Model):
    full_name=models.CharField(max_length=150)
    email=models.CharField(max_length=150)
    detail=models.TextField()
    send_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'enquiries'
    def __str__(self):
        return self.full_name
    
# Gallery Model
class Gallery(models.Model):
    title=models.CharField(max_length=150)
    detail=models.TextField()
    img=models.ImageField(upload_to="gallery/",null=True)
    
    class Meta:
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe(f"<img src='{self.img.url}' width='80' />")
    

# Gallery Images
class GalleryImage(models.Model):
	gallery=models.ForeignKey(Gallery, on_delete=models.CASCADE,null=True)
	alt_text=models.CharField(max_length=150)
	img=models.ImageField(upload_to="gallery_imgs/",null=True)

	def __str__(self):
		return self.alt_text

	def image_tag(self):
		return mark_safe(f"<img src='{self.img.url}' width='80' />")

# Subscription Plans
class SubPlan(models.Model):
	title=models.CharField(max_length=150)
	price=models.IntegerField()
	max_member=models.IntegerField(null=True)
	highlight_status=models.BooleanField(default=False,null=True)
	validity_days=models.IntegerField(null=True)

	def __str__(self):
		return self.title

# Subscription Plans Features
class SubPlanFeature(models.Model):
	# subplan=models.ForeignKey(SubPlan, on_delete=models.CASCADE,null=True)
	subplan=models.ManyToManyField(SubPlan)
	title=models.CharField(max_length=150)

	def __str__(self):
		return self.title
    

# Package Discounts
class PlanDiscount(models.Model):
	subplan=models.ForeignKey(SubPlan, on_delete=models.CASCADE,null=True)
	total_months=models.IntegerField()
	total_discount=models.IntegerField()

	def __str__(self):
		return str(self.total_months)

# Subscriber
class Subscriber(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	mobile=models.CharField(max_length=20)
	address=models.TextField()
	img=models.ImageField(upload_to="subs/",null=True)

	def __str__(self):
		return str(self.user)

	def image_tag(self):
		if self.img:
			return mark_safe(f"<img src='{self.img.url}' width='80' />")
		else:
			return 'no-image'

@receiver(post_save, sender=User)
def create_subscriber(sender, instance, created, **kwrargs):
    if created:
        Subscriber.objects.create(user=instance)

# Subscription
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    plan = models.ForeignKey('SubPlan', on_delete=models.CASCADE, null=True)
    price = models.CharField(max_length=50)  # Consider using DecimalField for monetary values
    reg_date = models.DateField(auto_now_add=True, null=True)
    # end_date should be automatically calculated based on reg_date and plan validity
    # end_date = models.DateField(null=True, blank=True)  # Remove this field
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Deactivate other active subscriptions for the user
        if self.is_active:
            Subscription.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @property
    def end_date(self):
        # Calculate end_date based on reg_date and plan validity_days
        if self.reg_date and self.plan:
            return self.reg_date + timedelta(days=self.plan.validity_days)
        return None

    @property
    def is_expired(self):
        # Check if subscription is expired based on current date and end_date
        return timezone.now().date() > self.end_date if self.end_date else False

    def __str__(self):
        return f"{self.user.username} - {self.plan.title}"

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
# Trainer
class Trainer(models.Model):
	full_name=models.CharField(max_length=100)
	username=models.CharField(max_length=100,null=True)
	pwd=models.CharField(max_length=50,null=True)
	mobile=models.CharField(max_length=100)
	address=models.TextField()
	is_active=models.BooleanField(default=False)
	detail=models.TextField()
	img=models.ImageField(upload_to="trainers/")
	salary=models.IntegerField(default=0)

	facebook=models.CharField(max_length=200,null=True)
	twitter=models.CharField(max_length=200,null=True)
	pinterest=models.CharField(max_length=200,null=True)
	youtube=models.CharField(max_length=200,null=True)

	def __str__(self):
		return str(self.full_name)

	def image_tag(self):
		if self.img:
			return mark_safe(f"<img src='{self.img.url}' width='80' />")
		else:
			return 'no-image'


# Notifications Json Response Via Ajax
class Notify(models.Model):
	notify_detail=models.TextField()
	read_by_user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
	read_by_trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE,null=True,blank=True)

	def __str__(self):
		return str(self.notify_detail)

# Markas Read Notification By User
class NotifUserStatus(models.Model):
	notif=models.ForeignKey(Notify, on_delete=models.CASCADE)
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	status=models.BooleanField(default=False)

	class Meta:
		verbose_name_plural='Notification Status'
  

# Assign Subscriber to Trainer
class AssignSubscriber(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user)

# Trainer Achivements
class TrainerAchivement(models.Model):
	trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)
	title=models.CharField(max_length=100)
	detail=models.TextField()
	img=models.ImageField(upload_to="trainers_achivements/")

	def __str__(self):
		return str(self.title)

	def image_tag(self):
		if self.img:
			return mark_safe(f"<img src='{self.img.url}' width='80' />")
		else:
			return 'no-image'


# TrainerSalary Model
class TrainerSalary(models.Model):
	trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)
	amt=models.IntegerField()
	amt_date=models.DateField()
	remarks=models.TextField(blank=True)

	class Meta:
		verbose_name_plural='Trainer Salary'

	def __str__(self):
		return str(self.trainer.full_name)


# Trainer Notifications
class TrainerNotification(models.Model):
	notif_msg=models.TextField()

	def __str__(self):
		return str(self.notif_msg)

	def save(self,*args,**kwargs):
		super(TrainerNotification, self).save(*args,**kwargs)
		channel_layer=get_channel_layer()
		notif=self.notif_msg
		total=TrainerNotification.objects.all().count()
		# total=TrainerNotification.objects.all().filter(notiftrainerstatus__status=True).count()

		async_to_sync(channel_layer.group_send)(
			'noti_group_name',{
				'type':'send_notification',
				'value':json.dumps({'notif':notif,'total':total})
			}
		)

# Markas Read Notification By Trainer
class NotifTrainerStatus(models.Model):
	notif=models.ForeignKey(TrainerNotification, on_delete=models.CASCADE)
	trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE)
	status=models.BooleanField(default=False)

	class Meta:
		verbose_name_plural='Trainer Notification Status'

# SubscriberMsg
class TrainerMsg(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE,null=True)
	message=models.TextField()

	class Meta:
		verbose_name_plural='Messages For Trainer'
  
# Reports
class TrainerSubscriberReport(models.Model):
	report_for_trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE,null=True,related_name='report_for_trainer')
	report_for_user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name='report_for_user')
	report_from_trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE,null=True,related_name='report_from_trainer',blank=True)
	report_from_user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name='report_from_user',blank=True)
	report_msg=models.TextField()
 
 
class AppSetting(models.Model):
	logo_img=models.ImageField(upload_to='app_logos/')

	def image_tag(self):
		if self.logo_img:
			return mark_safe(f"<img src='{self.logo_img.url}' width='80' />")
		else:
			return 'no-image'

from django.db import models

class EquipmentInventory(models.Model):
  STATUS_CHOICES = (
    ('available', 'Available'),
    ('under_maintenance', 'Under Maintenance'),
    ('unavailable', 'Unavailable'),
  )
  name = models.CharField(max_length=255)

  description = models.TextField(blank=True)
  maintenance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
  img=models.ImageField(upload_to="equipment_inventory/")
  
  def image_tag(self):
      if self.img:
          return mark_safe(f"<img src='{self.img.url}' width='80' /")
      else:
          return 'no-image'

  def __str__(self):
    return self.name

#phone numbers
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    


