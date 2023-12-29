# use to find bundle id of an application

import subprocess

def get_bundle_id(app_name):
    script = f'''
    id of application "{app_name}"
    '''
    bundle_id = subprocess.check_output(['osascript', '-e', script])
    return bundle_id.decode("utf-8").strip()


# put the application name you want to find the bundle id for in the quotes
print(get_bundle_id("Spotify"))