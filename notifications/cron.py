from notifications.views import send_email, send_push, send_scheduled_email
from .models import Notification, NotificationType, ScheduledEmail, ScheduledNotification, ScheduledPushNotification
from datetime import datetime
from userdetails.models import UserDetail

def scheduled_push_notification():
      sch_notifs = ScheduledPushNotification.objects.filter(done=False, date__lte = datetime.now())
      for sch_notif in sch_notifs:
            lang = "EN"
            langs = sch_notif.user.settings.all()
            for lan in langs:
                  lang = lan.language.code
                  break
            text = sch_notif.notification_type.text_fr if lang=="FR" else sch_notif.notification_type.text_en
            if sch_notif.service is not None:
                  text = text.replace("<<SERVICE<<",sch_notif.service.name_en if lang=="EN" else sch_notif.service.name_fr)
            if sch_notif.fullname_user is not None:
                  text = text.replace("<<USERNAME<<",sch_notif.fullname_user.user.first_name +" "+sch_notif.fullname_user.user.last_name)
            if sch_notif.user.user.email is not None and sch_notif.user.user.email !="":
                  send_email(to_email=sch_notif.user.user.email,
                             code="DB",
                             service_name=sch_notif.service.name_fr if lang == "FR" else sch_notif.service.name_en,
                             user_name="",
                             lang=lang)
            if langs.count()>0:
                  if langs.first().push_notification:
                        for i in sch_notif.user.push_tokens.all():
                              send_push(to=i.token, title="",body=text)
            else:
                  for i in sch_notif.user.push_tokens.all():
                        send_push(to=i.token, title="",body=text)
            sch_notif.done= True
            sch_notif.save()
      
def scheduled_notification():
      sch_notifs = ScheduledNotification.objects.filter(done=False, execute_date__lte = datetime.now())
      if sch_notifs.count()>0:
            notif_type = NotificationType.objects.get(code = "SCHN")
            users = UserDetail.objects.filter(user_role__code="CL")
            for item in sch_notifs:
                  if item.for_users == 3:
                        users = users.filter(is_client=True)
                  elif item.for_users == 2:
                        users = users.filter(is_master=True)
                  for user in users:
                        Notification(notification_type=notif_type,
                                    owner=user,
                                    scheduled_notif=item).save()
                        lang = "EN"
                        langs = user.settings.all()
                        for lan in langs:
                              lang = lan.language.code
                              break
                        if lang == "FR":
                              text=item.text_fr
                        else:
                              text=item.text_en
                        if langs.count()>0:
                              if langs.first().push_notification:
                                    for i in user.push_tokens.all():
                                          send_push(to=i.token, title="",body=text)   
                        else:
                              for i in user.push_tokens.all():
                                    send_push(to=i.token, title="",body=text)   
                  item.done=True
                  item.save()
 
def scheduled_email():
      
      sch_notifs = ScheduledEmail.objects.filter(done=False, execute_date__lte = datetime.now())
      if sch_notifs.count()>0:
            users = UserDetail.objects.filter(user_role__code="CL")
            for item in sch_notifs:
                  if item.for_users == 3:
                        users = users.filter(is_client=True)
                  elif item.for_users == 2:
                        users = users.filter(is_master=True)
                  for user in users:
                        lang = "EN"
                        langs = user.settings.all()
                        for lan in langs:
                              lang = lan.language.code
                              break
                        if lang == "FR":
                              text=item.text_fr
                              subject=item.subject_fr
                        else:
                              text=item.text_en
                              subject=item.subject_en
                        send_scheduled_email(text=text,to_email=user.user.email,subject=subject)
            item.done=True
            item.save()