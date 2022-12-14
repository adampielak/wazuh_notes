#!/usr/bin/env python
import json
import sys
import time
import os
​
try:
    import requests
except Exception as e:
    print("No module 'requests' found. Install: pip install requests")
    sys.exit(1)
​
# ossec.conf configuration:
# <integration>
# <name>custom-teams</name>
# <hook_url>https://outlook.office.com/webhook/XXXXXXXXXXXX</hook_url>
# <level>10</level> <!-- Optionnal -->
# <alert_format>json</alert_format>
# </integration>
​
# Global vars
​
debug_enabled = False
pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
json_alert = {}
now = time.strftime("%a %b %d %H:%M:%S %Z %Y")
​
# Set paths
log_file = '{0}/logs/integrations.log'.format(pwd)
​
​
def main(args):
    debug("# Starting")
​
    # Read args
    alert_file_location = args[1]
    webhook = args[3]
​
    debug("# Webhook")
    debug(webhook)
​
    debug("# File location")
    debug(alert_file_location)
​
    # Load alert. Parse JSON object.
    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)
    debug("# Processing alert")
    debug(json_alert)
​
    debug("# Generating message")
    msg = generate_msg(json_alert)
    debug(msg)
​
    debug("# Sending message")
    send_msg(msg, webhook)
​
​
def debug(msg):
    if debug_enabled:
        msg = "{0}: {1}\n".format(now, msg)
        print(msg)
        f = open(log_file, "a")
        f.write(msg)
        f.close()
​
​
def generate_msg(alert):
​
    level = alert['rule']['level']
​
    if (level <= 4):
        color = "008000"
    elif (level >= 5 and level <= 7):
        color = "FFFF00"
    else:
        color = "CD5C5C"
​
    facts = {"facts": []}
​
    msg = {}
    msg['@context'] = "https://schema.org/extensions"
    msg['@type'] = "MessageCard"
    msg['sections'] = []
​
    facts["facts"].extend([
{
'name': "Agent" if 'agent' in alert else "Agentless Host",
'value': "({0}) - {1}".format(alert['agent']['id'], alert['agent']['name']) if 'agent' in alert else alert['agentless']['host']
},
​
{
'name': "Rule",
'value': "{0} _(Level {1})_".format(alert['rule']['id'], level)
},
​
{
'name': "Location",
'value': alert['location']
},
​
{
'name': "Path",
'value': alert["syscheck"]["path"] if "syscheck" in alert else "N/A"
},
​
{
'name': "Description",
'value': alert['rule']['description'] if 'description' in alert['rule'] else "N/A"
},
​
{
'name': "Full Log",
'value': alert.get('full_log')
}
])
    msg['sections'].append(facts)
​
    msg['summary'] = alert['rule']['description'] if 'description' in alert['rule'] else "N/A"
    msg['themeColor'] = color
    msg['title'] = alert['rule']['description'] if 'description' in alert['rule'] else "N/A"
​
    return json.dumps(msg)
​
​
def send_msg(msg, url):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    res = requests.post(url, data=msg, headers=headers)
    debug(res)
​
​
if __name__ == "__main__":
    try:
        # Read arguments
        bad_arguments = False
        if len(sys.argv) >= 4:
            msg = '{0} {1} {2} {3} {4}'.format(
                now,
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
                sys.argv[4] if len(sys.argv) > 4 else '',
            )
            debug_enabled = (len(sys.argv) > 4 and sys.argv[4] == 'debug')
        else:
            msg = '{0} Wrong arguments'.format(now)
            bad_arguments = True
​
        # Logging the call
        f = open(log_file, 'a')
        f.write(msg + '\n')
        f.close()
​
        if bad_arguments:
            debug("# Exiting: Bad arguments.")
            sys.exit(1)
​
        # Main function
        main(sys.argv)
​
    except Exception as e:
        debug(str(e))
        raise