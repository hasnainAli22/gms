from . import models


def get_logo(request):
    logo = models.AppSetting.objects.first()
    if not logo:
        return {"logo": "Mughal Gym"}
    data = {"logo": logo.image_tag}
    return data
