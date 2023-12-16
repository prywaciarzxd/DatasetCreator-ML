import csv
import os
from xml.dom.minidom import parseString

MAX_ROWS = 10000
rows_written = 0

intents_to_find = ['android.intent.action.BOOT_COMPLETED', 'android.intent.action.PACKAGE_REPLACED', 'android.intent.action.SEND_MULTIPLE', 'android.intent.action.TIME_SET', 'android.intent.action.PACKAGE_REMOVED', 'android.intent.action.TIMEZONE_CHANGED', 'android.intent.action.ACTION_POWER_DISCONNECTED', 'android.intent.action.PACKAGE_ADDED', 'android.intent.action.ACTION_SHUTDOWN', 'android.intent.action.PACKAGE_DATA_CLEARED', 'android.intent.action.PACKAGE_CHANGED', 'android.intent.action.NEW_OUTGOING_CALL', 'android.intent.action.SENDTO', 'android.intent.action.CALL', 'android.intent.action.SCREEN_ON', 'android.intent.action.BATTERY_OKAY', 'android.intent.action.PACKAGE_RESTARTED', 'android.intent.action.CALL_BUTTON', 'android.intent.action.SCREEN_OFF', 'intent.action.RUN', 'android.intent.action.SET_WALLPAPER', 'android.intent.action.BATTERY_LOW', 'android.intent.action.ACTION_POWER_CONNECTED']

permissions_to_find = ['SEND_SMS', 'READ_PHONE_STATE', 'GET_ACCOUNTS', 'RECEIVE_SMS', 'READ_SMS', 'USE_CREDENTIALS', 'MANAGE_ACCOUNTS', 'WRITE_SMS', 'READ_SYNC_SETTINGS', 'AUTHENTICATE_ACCOUNTS', 'WRITE_HISTORY_BOOKMARKS', 'INSTALL_PACKAGES', 'CAMERA', 'WRITE_SYNC_SETTINGS', 'READ_HISTORY_BOOKMARKS', 'INTERNET', 'RECORD_AUDIO', 'NFC', 'ACCESS_LOCATION_EXTRA_COMMANDS', 'WRITE_APN_SETTINGS', 'BIND_REMOTEVIEWS', 'READ_PROFILE', 'MODIFY_AUDIO_SETTINGS', 'READ_SYNC_STATS', 'BROADCAST_STICKY', 'WAKE_LOCK', 'RECEIVE_BOOT_COMPLETED', 'RESTART_PACKAGES', 'BLUETOOTH', 'READ_CALENDAR', 'READ_CALL_LOG', 'SUBSCRIBED_FEEDS_WRITE', 'READ_EXTERNAL_STORAGE', 'VIBRATE', 'ACCESS_NETWORK_STATE', 'SUBSCRIBED_FEEDS_READ', 'CHANGE_WIFI_MULTICAST_STATE', 'WRITE_CALENDAR', 'MASTER_CLEAR', 'UPDATE_DEVICE_STATS', 'WRITE_CALL_LOG', 'DELETE_PACKAGES', 'GET_TASKS', 'GLOBAL_SEARCH', 'DELETE_CACHE_FILES', 'WRITE_USER_DICTIONARY', 'REORDER_TASKS', 'WRITE_PROFILE', 'SET_WALLPAPER', 'BIND_INPUT_METHOD', 'READ_SOCIAL_STREAM', 'READ_USER_DICTIONARY', 'PROCESS_OUTGOING_CALLS', 'CALL_PRIVILEGED', 'BIND_WALLPAPER', 'RECEIVE_WAP_PUSH', 'DUMP', 'BATTERY_STATS', 'ACCESS_COARSE_LOCATION', 'SET_TIME', 'WRITE_SOCIAL_STREAM', 'WRITE_SETTINGS', 'REBOOT', 'BLUETOOTH_ADMIN', 'BIND_DEVICE_ADMIN', 'WRITE_GSERVICES', 'KILL_BACKGROUND_PROCESSES', 'STATUS_BAR', 'PERSISTENT_ACTIVITY', 'CHANGE_NETWORK_STATE', 'RECEIVE_MMS', 'SET_TIME_ZONE', 'CONTROL_LOCATION_UPDATES', 'BROADCAST_WAP_PUSH', 'BIND_ACCESSIBILITY_SERVICE', 'ADD_VOICEMAIL', 'CALL_PHONE', 'BIND_APPWIDGET', 'FLASHLIGHT', 'READ_LOGS', 'SET_PROCESS_LIMIT', 'MOUNT_UNMOUNT_FILESYSTEMS', 'BIND_TEXT_SERVICE', 'INSTALL_LOCATION_PROVIDER', 'SYSTEM_ALERT_WINDOW', 'MOUNT_FORMAT_FILESYSTEMS', 'CHANGE_CONFIGURATION', 'CLEAR_APP_USER_DATA', 'CHANGE_WIFI_STATE', 'READ_FRAME_BUFFER', 'ACCESS_SURFACE_FLINGER', 'BROADCAST_SMS', 'EXPAND_STATUS_BAR', 'INTERNAL_SYSTEM_WINDOW', 'SET_ACTIVITY_WATCHER', 'WRITE_CONTACTS', 'BIND_VPN_SERVICE', 'DISABLE_KEYGUARD', 'ACCESS_MOCK_LOCATION', 'GET_PACKAGE_SIZE', 'MODIFY_PHONE_STATE', 'CHANGE_COMPONENT_ENABLED_STATE', 'CLEAR_APP_CACHE', 'SET_ORIENTATION', 'READ_CONTACTS', 'DEVICE_POWER', 'HARDWARE_TEST', 'ACCESS_WIFI_STATE', 'WRITE_EXTERNAL_STORAGE', 'ACCESS_FINE_LOCATION', 'SET_WALLPAPER_HINTS', 'SET_PREFERRED_APPLICATIONS', 'WRITE_SECURE_SETTINGS', 'MALWARE']

manifests_found = set()  # Inicjalizacja zbioru na ścieżki manifestów
results_to_write = []  # Inicjalizacja listy wyników

def find_manifests(root_dir):
    all_manifests = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith('AndroidManifest_benign_') and file.endswith('.apk.xml'):
                manifest_path = os.path.join(root, file)
                if manifest_path not in manifests_found:
                    all_manifests.append(manifest_path)
                    manifests_found.add(manifest_path)
                    print(f"Found AndroidManifest.xml in: {manifest_path}")
    return all_manifests
 

def extract_features(manifest_path):
    with open(manifest_path, 'rb') as f:
        data = f.read()
    dom = parseString(data)
    
    nodes_permissions = dom.getElementsByTagName('uses-permission') + dom.getElementsByTagName('uses-permission-sdk-23')
    permissions = [node.getAttribute("android:name").replace('android.permission.', '') for node in nodes_permissions]

    # Extract intent filters
    nodes_intents = dom.getElementsByTagName('intent-filter')
    intents = []

    for intent_node in nodes_intents:
        intent_actions = [action.getAttribute("android:name") for action in intent_node.getElementsByTagName('action')]
        intent_categories = [category.getAttribute("android:name") for category in intent_node.getElementsByTagName('category')]
        intent_data = [data.getAttribute("android:mimeType") for data in intent_node.getElementsByTagName('data')]

        intent = {
            'actions': intent_actions,
            'categories': intent_categories,
            'data': intent_data
        }
        intents.append(intent)

    return permissions, intents

def append_permissions_and_intents_to_csv(permissions, intents, output_path):
    fieldnames = permissions_to_find + intents_to_find + ['class']

    write_header = not os.path.exists(output_path)

    permissions_row = {feature: 0 for feature in permissions_to_find}
    permissions_row.update({feature: 1 for feature in permissions})

    intents_row = {feature: 0 for feature in intents_to_find}
    for feature in intents_to_find:
        for intent in intents:
            if feature in intent['actions']:
                intents_row[feature] = 1
                break

    malware_value = 'B'

    value_row = {**permissions_row, **intents_row, 'class': malware_value}

    results_to_write.append(value_row)

    if len(results_to_write) >= MAX_ROWS:
        write_to_csv(output_path)

def write_to_csv(output_path):
    fieldnames = permissions_to_find + intents_to_find + ['class']
    write_header = not os.path.exists(output_path)

    with open(output_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        for value_row in results_to_write:
            writer.writerow(value_row)

    results_to_write.clear()

if __name__ == "__main__":
    root_dir = '/home/kali/Desktop/dataset_create_tool/benign_manifests_10k'
    all_paths = find_manifests(root_dir)
    output_path = '/home/kali/Desktop/dataset_create_tool/text_csv_files/found_features_verified_all.csv'

    for manifest_path in all_paths:
        try:
            extracted_permissions, extracted_intents = extract_features(manifest_path)
            append_permissions_and_intents_to_csv(extracted_permissions, extracted_intents, output_path)
        except:
            print(f"Skipping {manifest_path} due to UnicodeDecodeError:")
            continue

