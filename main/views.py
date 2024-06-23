import re
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.db.models import Count
from django.core.paginator import Paginator
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import stripe
import logging
from datetime import timedelta
from . import models
from . import forms

# Create your views here.
# Home Page
def home(request):
    banners = models.Banners.objects.all()
    services = models.Service.objects.all()[:3]
    gimgs = models.GalleryImage.objects.all().order_by("-id")[:6]
    return render(
        request, "home.html", {"banners": banners, "services": services, "gimgs": gimgs}
    )


def page_detail(request, id):
    page = models.Page.objects.get(id=id)
    return render(request, "page.html", {"page": page})


def faq_list(request):
    faqs = models.Faq.objects.all()
    return render(request, "faq.html", {"faqs": faqs})


# Contact
def contact_page(request):
    msg = ""
    if request.method == "POST":
        form = forms.EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            msg = "Data has been saved"
    form = forms.EnquiryForm
    return render(request, "contact_us.html", {"form": form, "msg": msg})

# Show galleries
def gallery(request):
    galleries = models.Gallery.objects.all().order_by("-id")
    return render(request, "gallery.html", {"galleries": galleries})

# Show gallery photos
def gallery_detail(request, id):
    gallery = models.Gallery.objects.get(id=id)
    gallery_imgs = models.GalleryImage.objects.filter(gallery=gallery).order_by("-id")
    return render(
        request, "gallery_imgs.html", {"gallery_imgs": gallery_imgs, "gallery": gallery}
    )

# Subscription Plans
def pricing(request):
    pricing = (
        models.SubPlan.objects.annotate(total_members=Count("subscription__id"))
        .all()
        .order_by("price")
    )  # put some emphasis on it
    # pricing = models.SubPlan.objects.all().order_by('price')
    print(pricing)
    dfeatures = models.SubPlanFeature.objects.all()
    return render(request, "pricing.html", {"plans": pricing, "dfeatures": dfeatures})

# SignUp
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect authenticated users

    if request.method == "POST":
        form = forms.SignUp(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Thank you for registering. You are now logged in."
            )
            return redirect('home')
    else:
        form = forms.SignUp()

    return render(request, "registration/signup.html", {"form": form})

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from . import forms

def login_view(request):
    if request.method == 'POST':
        form = forms.CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                messages.success(request, "Login Success")
                login(request, user)
                return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = forms.CustomLoginForm()
    return render(request, 'registration/login.html', context={'form': form})

# Checkout
@login_required
def checkout(request, plan_id):
    plan = models.SubPlan.objects.get(id=plan_id)
    current_subscription = models.Subscription.objects.filter(user=request.user, is_active=True).first()

    if current_subscription:
        messages.error(request, "You already have an active subscription.")
        return redirect('user_dashboard')

    if request.method == 'POST':
        subscription = models.Subscription(user=request.user, plan=plan, price=plan.price)
        subscription.save()
        messages.success(request, f"You have successfully subscribed to {plan.title} plan.")
        return redirect('user_dashboard')
    
    already_registered_user = models.Subscription.objects.filter(plan=plan).count()
    remaining_seats = plan.max_member - already_registered_user # type: ignore
    return render(request, "checkout.html", {"plan": plan, "already_registered": already_registered_user,"remaining_seats": remaining_seats})

stripe.api_key = "sk_test_51LMWjAIDIO1D6jfm6Uvwv86ccB8aC7YIRjseqHaBSmPbh1pZI4o5Shf4fopHzrKIqxlGvw2yhmmqIcqmo1tdRD9700bcQ3bUYw"

def checkout_session(request, plan_id,):
    plan = models.SubPlan.objects.get(pk=plan_id)
    discount_amount = float(request.POST.get('discount_amount', 0.00))  # Default to 0.00
    print("Discounted Amount",discount_amount)

    # Calculate line_item total considering discount
    line_item_total = max(plan.price * 100 - int(discount_amount * 100), 0)  # Ensure non-negative
    line_item_total = max(plan.price * 100 - int(discount_amount * 100), 0)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": plan.title,
                    },
                    "unit_amount":line_item_total
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://127.0.0.1:8000/pay_success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/pay_cancel",
        client_reference_id=plan_id,
    )
    return redirect(session.url, code=303)

from django.core.mail import EmailMessage

def pay_success(request):
    session = stripe.checkout.Session.retrieve(request.GET["session_id"])
    plan_id = session.client_reference_id
    plan = models.SubPlan.objects.get(pk=plan_id)
    user = request.user
    models.Subscription.objects.create(plan=plan, user=user, price=plan.price)
    subject = "Order Email"
    html_content = get_template("orderemail.html").render({"title": plan.title})
    from_email = "our.hasnain22@gmail.com"
    #some work to do
    msg = EmailMessage(subject, html_content, from_email, ["john@gmail.com"])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    return render(request, "success.html")

# Cancel
def pay_cancel(request):
    return render(request, "cancel.html")

# User Dashboard Section Start
@login_required
def user_dashboard(request):
    try:
        current_plan = models.Subscription.objects.get(user=request.user, is_active=True)
    except models.Subscription.DoesNotExist:
        current_plan = None
        my_trainer = None

    if current_plan:
        if current_plan.is_expired:
            current_plan.is_active = False
            current_plan.save()
            current_plan = None
        else:
            try:
                my_trainer = models.AssignSubscriber.objects.get(user=request.user)
            except models.AssignSubscriber.DoesNotExist:
                my_trainer = None

    enddate = None
    if current_plan and current_plan.reg_date:
        enddate = current_plan.end_date

    # Notification
    data = models.Notify.objects.all().order_by("-id")
    notifStatus = False
    jsonData = []
    totalUnread = 0
    for d in data:
        try:
            notifStatusData = models.NotifUserStatus.objects.get(
                user=request.user, notif=d
            )
            if notifStatusData:
                notifStatus = True
        except models.NotifUserStatus.DoesNotExist:
            notifStatus = False
        if not notifStatus:
            totalUnread = totalUnread + 1

    return render(
        request,
        "user/dashboard.html",
        {
            "current_plan": current_plan,
            "my_trainer": my_trainer,
            "total_unread": totalUnread,
            "enddate": enddate,
        },
    )


# Edit Form
def update_profile(request):
    msg = None
    if request.method == "POST":
        form = forms.ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            msg = "Data has been saved"
    form = forms.ProfileForm(instance=request.user)
    return render(request, "user/update-profile.html", {"form": form, "msg": msg})


# trainer login
def trainerlogin(request):
    msg = ""
    if request.method == "POST":
        username = request.POST["username"]
        pwd = request.POST["pwd"]
        trainer = models.Trainer.objects.filter(username=username, pwd=pwd).count()
        if trainer > 0:
            trainer = models.Trainer.objects.filter(username=username, pwd=pwd).first()
            request.session["trainerLogin"] = True
            request.session["name"] = trainer.full_name # type: ignore
            request.session["trainerid"] = trainer.id # type: ignore
            messages.success(request, "Login Success!")
            return redirect("/trainer_dashboard")
        else:
            messages.error(request, "Invalid cardentials")
    form = forms.TrainerLoginForm
    return render(request, "trainer/login.html", {"form": form, "msg": msg})


# Trainer Logout
def trainerlogout(request):
    del request.session["trainerLogin"]
    return redirect("/trainerlogin")


# Trainer Dashboard
def trainer_dashboard(request):
    return render(request, "trainer/dashboard.html")


# Trainer Profile
def trainer_profile(request):
    t_id = request.session["trainerid"]
    trainer = models.Trainer.objects.get(pk=t_id)
    msg = None
    if request.method == "POST":
        form = forms.TrainerProfileForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            msg = "Profile has been updated"
    form = forms.TrainerProfileForm(instance=trainer)
    return render(request, "trainer/profile.html", {"form": form, "msg": msg})


# Trainer Subscribers
def trainer_subscribers(request):
    trainer = models.Trainer.objects.get(pk=request.session["trainerid"])
    trainer_subs = models.AssignSubscriber.objects.filter(trainer=trainer).order_by(
        "-id"
    )
    return render(
        request, "trainer/trainer_subscribers.html", {"trainer_subs": trainer_subs}
    )


# Trainer Payments
def trainer_payments(request):
    trainer = models.Trainer.objects.get(pk=request.session["trainerid"])
    trainer_pays = models.TrainerSalary.objects.filter(trainer=trainer).order_by("-id")
    return render(
        request, "trainer/trainer_payments.html", {"trainer_pays": trainer_pays}
    )


# Trainer Change Password
def trainer_changepassword(request):
    msg = None
    if request.method == "POST":
        new_password = request.POST["new_password"]
        updateRes = models.Trainer.objects.filter(
            pk=request.session["trainerid"]
        ).update(pwd=new_password)
        if updateRes:
            del request.session["trainerLogin"]
            return redirect("/trainerlogin")
        else:
            msg = "Something is wrong!!"
    form = forms.TrainerChangePassword
    return render(request, "trainer/trainer_changepassword.html", {"form": form})


# Notifications
def notifs(request):
    data = models.Notify.objects.all().order_by("-id")
    return render(request, "notifs.html")


# Get All Notifications
def get_notifs(request):
    data = models.Notify.objects.all().order_by("-id")
    notifStatus = False
    jsonData = []
    totalUnread = 0
    for d in data:
        try:
            notifStatusData = models.NotifUserStatus.objects.get(
                user=request.user, notif=d
            )
            if notifStatusData:
                notifStatus = True
        except models.NotifUserStatus.DoesNotExist:
            notifStatus = False
        if not notifStatus:
            totalUnread = totalUnread + 1
        jsonData.append(
            {"pk": d.id, "notify_detail": d.notify_detail, "notifStatus": notifStatus} # type: ignore
        )
    # jsonData=serializers.serialize('json', data)
    return JsonResponse({"data": jsonData, "totalUnread": totalUnread})


# Mark Read By user
def mark_read_notif(request):
    notif = request.GET["notif"]
    notif = models.Notify.objects.get(pk=notif)
    user = request.user
    models.NotifUserStatus.objects.create(notif=notif, user=user, status=True)
    return JsonResponse({"bool": True})


# Trainer Notifications
def trainer_notifs(request):
    data = models.TrainerNotification.objects.all().order_by("-id")
    trainer = models.Trainer.objects.get(id=request.session["trainerid"])
    jsonData = []
    totalUnread = 0
    for d in data:
        try:
            notifStatusData = models.NotifTrainerStatus.objects.get(
                trainer=trainer, notif=d
            )
            if notifStatusData:
                notifStatus = True
        except models.NotifTrainerStatus.DoesNotExist:
            notifStatus = False
        if not notifStatus:
            totalUnread = totalUnread + 1
        jsonData.append(
            {"pk": d.id, "notify_detail": d.notif_msg, "notifStatus": notifStatus} # type: ignore
        )
    return render(
        request, "trainer/notifs.html", {"notifs": jsonData, "totalUnread": totalUnread}
    )


# Mark Read By trainer
def mark_read_trainer_notif(request):
    notif = request.GET["notif"]
    notif = models.TrainerNotification.objects.get(pk=notif)
    trainer = models.Trainer.objects.get(id=request.session["trainerid"])
    models.NotifTrainerStatus.objects.create(notif=notif, trainer=trainer, status=True)

    # Count Unread
    totalUnread = 0
    data = models.TrainerNotification.objects.all().order_by("-id")
    for d in data:
        try:
            notifStatusData = models.NotifTrainerStatus.objects.get(
                trainer=trainer, notif=d
            )
            if notifStatusData:
                notifStatus = True
        except models.NotifTrainerStatus.DoesNotExist:
            notifStatus = False
        if not notifStatus:
            totalUnread = totalUnread + 1

    return JsonResponse({"bool": True, "totalUnread": totalUnread})


# Trainer Messages
def trainer_msgs(request):
    data = models.TrainerMsg.objects.all().order_by("-id")
    return render(request, "trainer/msgs.html", {"msgs": data})


# Report for user
def report_for_user(request):
    trainer = models.Trainer.objects.get(id=request.session["trainerid"])
    msg = ""
    if request.method == "POST":
        form = forms.ReportForUserForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.report_from_trainer = trainer
            new_form.save()
            msg = "Data has been saved"
        else:
            msg = "Invalid Response!!"
    form = forms.ReportForUserForm
    return render(request, "report_for_user.html", {"form": form, "msg": msg})


# Report for trainer
def report_for_trainer(request):
    user = request.user
    msg = ""
    if request.method == "POST":
        form = forms.ReportForTrainerForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.report_from_user = user
            new_form.save()
            msg = "Data has been saved"
        else:
            msg = "Invalid Response!!"
    form = forms.ReportForTrainerForm
    return render(request, "report_for_trainer.html", {"form": form, "msg": msg})


# Equipments
def equipment_list(request):
  equipments = models.EquipmentInventory.objects.all().order_by('name')
  paginator = Paginator(equipments, 10)  # Change 10 to desired items per page

  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  context = {'equipments': page_obj}
  return render(request, 'equipment_list.html', context)

def all_services(request):
    services = models.Service.objects.all()
    return render(request, 'all_services.html', {'services':services})