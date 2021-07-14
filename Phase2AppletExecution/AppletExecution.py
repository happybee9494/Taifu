from Taifu.Phase2AppletExecution import AppletEnabler2
from Taifu.BehaviorMonitoring_NoiseTemplates.tatester.tatester.spiders.MonitoringJavaScriptAction import monitoring
#############################################################################################
# ENABLE A SET OF APPLETS AND OUTPUT ALL THE ACTION_SERVICES RELATED TO THE ENABLED APPLETS
#############################################################################################
trigger_service = 'android_photos' #blogger'
trigger = 'Any new photo'
results = AppletEnabler2.enableOnlyRequiredApplets(trigger, trigger_service, 1)


active_trigger = results['active_trigger']
active_trigger_service = results['active_trigger']
trigger_fields_of_active_trigger = results['trigger_fields_of_active_trigger']
action_details_list = results['action_details_list']
action_name_list = []
for actionD in action_details_list:
    action_service = actionD['action_service']
    action =  actionD['action']
    action_desc = actionD['action_desc']
    action_fields = actionD['action_fields']
    action_name_list.append(action_service)
print(action_name_list)

#############################################################################################
#############################################################################################
