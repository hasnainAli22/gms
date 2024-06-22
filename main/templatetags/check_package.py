from django import template
from main.models import Subscription,SubPlan
from django.contrib.auth.models import User
from datetime import date, timedelta
from django import template

register=template.Library()

@register.simple_tag
def check_user_package_h(user_id):
	user=User.objects.get(id=user_id)
	# plan=SubPlan.objects.get(id=plan_id)
	check_package=Subscription.objects.filter(user=user).count()
	if check_package > 0:
		return True
	else:
		return False

@register.simple_tag
def check_pckg_validity_h(user_id):
	expired=False
	user=User.objects.get(id=user_id)
	# plan=SubPlan.objects.get(id=plan_id)
	subscriptions=Subscription.objects.filter(user=user).order_by('-id')
	if subscriptions.exists():
		subscription=subscriptions.first()
		today=date.today()
		end_date = subscription.reg_date + timedelta(days=subscription.plan.validity_days)
		if today > end_date:
			expired=True
	else:
		expired=False
	return expired

@register.simple_tag
def check_user_package(user_id, plan_id):
	user=User.objects.get(id=user_id)
	plan=SubPlan.objects.get(id=plan_id)
	check_package=Subscription.objects.filter(user=user, plan=plan).count()
	if check_package > 0:
		return True
	else:
		return False

@register.simple_tag
def check_pckg_validity(user_id, plan_id):
	expired=False
	user=User.objects.get(id=user_id)
	plan=SubPlan.objects.get(id=plan_id)
	subscriptions=Subscription.objects.filter(user=user, plan=plan).order_by('-id')
	if subscriptions.exists():
		subscription=subscriptions.first()
		today=date.today()
		end_date = subscription.reg_date + timedelta(days=subscription.plan.validity_days)
		if today > end_date:
			expired=True
	else:
		expired=False
	return expired

