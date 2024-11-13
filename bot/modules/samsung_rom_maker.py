import io
import os
import shutil
import pickle
import subprocess
from functools import wraps

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop, DRIVE_FOLDER_ID
from bot.helper.telegram_helper.filters import CustomFilters

DOWNLOAD_DIR = "work"
shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
os.makedirs(DOWNLOAD_DIR)



######################
import os
import sys
import shutil

rom_location = f"{DOWNLOAD_DIR}/data/local/UnpackerSystem"
system_app_location = f"{rom_location}/system/system/app"
system_priv_app_location = f"{rom_location}/system/system/priv-app"
debloat_location = "debloat"
unnecessary_folders = ["hidden", "preload"]
lib_folders = [f"{rom_location}/system/system/lib", f"{rom_location}/system/system/lib64"]
full_camera_fix = "fixes/camera"
stock_media = "fixes/boot_animation"
esim_fp_file_location = "{rom_location}/system/system/etc/permissions/privapp-permissions-com.samsung.euicc.xml"
build_prop_location = f"{rom_location}/system/system/build.prop"
selinux_file_location = f"{rom_location}/system/system/system_ext/etc/selinux/mapping/31.0.cil"


if not os.path.exists(debloat_location):
    os.makedirs(debloat_location)

app_dir = os.path.join(debloat_location, "app")
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

priv_app_dir = os.path.join(debloat_location, "priv-app")
if not os.path.exists(priv_app_dir):
    os.makedirs(priv_app_dir)

    
def delete_line(target_line, target_file):
    with open(target_file, "r") as f:
        lines = f.readlines()
    with open(target_file, "w") as f:
        for line in lines:
            if target_line not in line:
                f.write(line)


def add_line(new_line, target_file):
    with open(target_file, 'r') as file:
        lines = file.readlines()

    new_line = f"{new_line}\n"
    lines.insert(-1, new_line)

    with open(target_file, 'w') as file:
        file.writelines(lines)


def delete_folders(path, folders):
    print("Deleting unnecessary files and folders.")
    for folder in folders:
        folder_path = os.path.join(path, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        else:
            pass


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().splitlines()


def delete_files(file_path):
    for file_path in file_path:
        if os.path.exists(file_path):
            os.remove(file_path)


def edit_floating_feature():
    file_path = f"{rom_location}/system/system/etc/floating_feature.xml"
    print(f"Fixing refresh rate.")
    
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_MODE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_MODE>1</SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_MODE>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_SUB_HFR_MODE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_SUB_HFR_MODE>0</SEC_FLOATING_FEATURE_LCD_CONFIG_SUB_HFR_MODE>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_DEFAULT_REFRESH_RATE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_DEFAULT_REFRESH_RATE>90</SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_DEFAULT_REFRESH_RATE>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE>60,90</SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE_NS>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE_NS>60</SEC_FLOATING_FEATURE_LCD_CONFIG_HFR_SUPPORTED_REFRESH_RATE_NS>", file_path)

    print(f"Fixing ssrm Warning.")
    delete_line("    <SEC_FLOATING_FEATURE_SYSTEM_CONFIG_SIOP_POLICY_FILENAME>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SYSTEM_CONFIG_SIOP_POLICY_FILENAME>siop_a22_mt6769t</SEC_FLOATING_FEATURE_SYSTEM_CONFIG_SIOP_POLICY_FILENAME>", file_path)
    
    print(f"Fixing AUDIO_CONFIG_VOLUMEMONITOR_GAIN.")
    delete_line("    <SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_GAIN>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_GAIN>3</SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_GAIN>", file_path)
    
    print(f"Fixing AUDIO_CONFIG_VOLUMEMONITOR_STAGE.")
    delete_line("    <SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_STAGE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_STAGE>1</SEC_FLOATING_FEATURE_AUDIO_CONFIG_VOLUMEMONITOR_STAGE>", file_path)
    
    print(f"Changing AUTO_BRIGHTNESS.")
    delete_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_CONTROL_AUTO_BRIGHTNESS>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_CONFIG_CONTROL_AUTO_BRIGHTNESS>2</SEC_FLOATING_FEATURE_LCD_CONFIG_CONTROL_AUTO_BRIGHTNESS>", file_path)

    print(f"Changing ELECTRIC_RATED_VALUE.")
    delete_line("    <SEC_FLOATING_FEATURE_SETTINGS_CONFIG_ELECTRIC_RATED_VALUE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SETTINGS_CONFIG_ELECTRIC_RATED_VALUE>DC 9 V; 1.67 A</SEC_FLOATING_FEATURE_SETTINGS_CONFIG_ELECTRIC_RATED_VALUE>", file_path)
    
    print(f"Fixing apps open lag.")
    delete_line("    <SEC_FLOATING_FEATURE_LAUNCHER_CONFIG_ANIMATION_TYPE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LAUNCHER_CONFIG_ANIMATION_TYPE>LowEnd</SEC_FLOATING_FEATURE_LAUNCHER_CONFIG_ANIMATION_TYPE>", file_path)
    
    print(f"Adding NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT.")
    delete_line("    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT>50</SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT>", file_path)
    
    print(f"Adding Edge features.")
    delete_line("    <SEC_FLOATING_FEATURE_SYSTEMUI_CONFIG_EDGELIGHTING_FRAME_EFFECT>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SYSTEMUI_CONFIG_EDGELIGHTING_FRAME_EFFECT>frame_effect</SEC_FLOATING_FEATURE_SYSTEMUI_CONFIG_EDGELIGHTING_FRAME_EFFECT>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_EDGE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_EDGE>people,task,circle,panel,-edgefeeds,edgelighting_v2,debug,cornerR:6.2,search,phonecolor,q2,devicescale:1.064,landscape,dot_bottom</SEC_FLOATING_FEATURE_COMMON_CONFIG_EDGE>", file_path)
    
    print(f"Adding Screen Recorder.")
    delete_line("    <SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_SCREEN_RECORDER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_SCREEN_RECORDER>TRUE</SEC_FLOATING_FEATURE_FRAMEWORK_SUPPORT_SCREEN_RECORDER>", file_path)

    print(f"Adding VOICERECORDER_CONFIG_DEF_MODE.")
    delete_line("    <SEC_FLOATING_FEATURE_VOICERECORDER_CONFIG_DEF_MODE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_VOICERECORDER_CONFIG_DEF_MODE>normal,interview,voicememo</SEC_FLOATING_FEATURE_VOICERECORDER_CONFIG_DEF_MODE>", file_path)

    print(f"Adding cpu responsiveness and process speed toggle.")
    delete_line("    <SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_CPU_RESPONSIVENESS>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_CPU_RESPONSIVENESS>TRUE</SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_CPU_RESPONSIVENESS>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_PROCESSING>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_PROCESSING>TRUE</SEC_FLOATING_FEATURE_SYSTEM_SUPPORT_ENHANCED_PROCESSING>", file_path)

    print(f"Enable Keyboard Size, Extract Text, Text Edit on Samsung Keyboard.")
    delete_line("    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>V2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>V2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>", file_path)

    print(f"Enable camera privacy toggle.")
    delete_line("    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_PRIVACY_TOGGLE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_PRIVACY_TOGGLE>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_PRIVACY_TOGGLE>", file_path)

    print(f"Adding battery health and battery cycles in Settings.")
    delete_line("    <SEC_FLOATING_FEATURE_BATTERY_SUPPORT_BSOH_SETTINGS>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_BATTERY_SUPPORT_BSOH_SETTINGS>TRUE</SEC_FLOATING_FEATURE_BATTERY_SUPPORT_BSOH_SETTINGS>", file_path)

    print(f"Fixing video editor.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_MULTIMEDIA_EDITOR_PLUGIN_PACKAGES>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_MULTIMEDIA_EDITOR_PLUGIN_PACKAGES>videotrimmer</SEC_FLOATING_FEATURE_COMMON_CONFIG_MULTIMEDIA_EDITOR_PLUGIN_PACKAGES>", file_path)

    print(f"Fixing photo remaster.")
    delete_line("    <SEC_FLOATING_FEATURE_SAIV_CONFIG_MIDAS>", file_path)
    
    print(f"Samsung Z fold type taskbar.")
    delete_line("    <SEC_FLOATING_FEATURE_LAUNCHER_SUPPORT_TASKBAR>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LAUNCHER_SUPPORT_TASKBAR>TRUE</SEC_FLOATING_FEATURE_LAUNCHER_SUPPORT_TASKBAR>", file_path)
    
    print(f"Adding china SMARTMANAGER.")
    delete_line("    <SEC_FLOATING_FEATURE_SMARTMANAGER_CONFIG_PACKAGE_NAME>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SMARTMANAGER_CONFIG_PACKAGE_NAME>com.samsung.android.sm_cn</SEC_FLOATING_FEATURE_SMARTMANAGER_CONFIG_PACKAGE_NAME>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_SECURITY_CONFIG_DEVICEMONITOR_PACKAGE_NAME>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SECURITY_CONFIG_DEVICEMONITOR_PACKAGE_NAME>com.samsung.android.sm.devicesecurity.tcm</SEC_FLOATING_FEATURE_SECURITY_CONFIG_DEVICEMONITOR_PACKAGE_NAME>", file_path)
    
    print(f"Enable Samsung AI.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_DISABLE_NATIVE_AI>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_SUPPORT_NATIVE_AI>TRUE</SEC_FLOATING_FEATURE_COMMON_SUPPORT_NATIVE_AI>", file_path)
    
    print(f"Enable full One Ui version.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_SEP_CATEGORY>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_SEP_CATEGORY>sep_basic</SEC_FLOATING_FEATURE_COMMON_CONFIG_SEP_CATEGORY>", file_path)
    
    print(f"Enable audio record via Bluetooth.")
    delete_line("    <SEC_FLOATING_FEATURE_AUDIO_SUPPORT_BT_RECORDING>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_AUDIO_SUPPORT_BT_RECORDING>TRUE</SEC_FLOATING_FEATURE_AUDIO_SUPPORT_BT_RECORDING>", file_path)

    print(f"Enable camera document scan.")
    delete_line("    <SEC_FLOATING_FEATURE_CAMERA_DOCUMENTSCAN_SOLUTIONS>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_CAMERA_DOCUMENTSCAN_SOLUTIONS>CV_DEWARPING</SEC_FLOATING_FEATURE_CAMERA_DOCUMENTSCAN_SOLUTIONS>", file_path)
    
    print(f"Enable Camera display flash.")
    delete_line("    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_NIGHT_FRONT_DISPLAY_FLASH>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_NIGHT_FRONT_DISPLAY_FLASH>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_NIGHT_FRONT_DISPLAY_FLASH>", file_path)
    
    print(f"Make device fully official.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_DEVICE_MANUFACTURING_TYPE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_DEVICE_MANUFACTURING_TYPE>in_house</SEC_FLOATING_FEATURE_COMMON_CONFIG_DEVICE_MANUFACTURING_TYPE>", file_path)
    
    print(f"Add gallery location support.")
    delete_line("    <SEC_FLOATING_FEATURE_GALLERY_SUPPORT_LOCATION_POI>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GALLERY_SUPPORT_LOCATION_POI>TRUE</SEC_FLOATING_FEATURE_GALLERY_SUPPORT_LOCATION_POI>", file_path)

    print(f"Enable some gallery and photo editor features.")
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_IMAGE_CLIPPER>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_OBJECT_ERASER>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_REFLECTION_ERASER>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SHADOW_ERASER>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SMART_LASSO>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SPOT_FIXER>", file_path)
    delete_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_STYLE_TRANSFER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_IMAGE_CLIPPER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_IMAGE_CLIPPER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_OBJECT_ERASER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_OBJECT_ERASER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_REFLECTION_ERASER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_REFLECTION_ERASER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SHADOW_ERASER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_SHADOW_ERASER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SMART_LASSO>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_SMART_LASSO>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_SPOT_FIXER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_SPOT_FIXER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_GENAI_SUPPORT_STYLE_TRANSFER>TRUE</SEC_FLOATING_FEATURE_GENAI_SUPPORT_STYLE_TRANSFER>", file_path)

    print(f"Removing esim option.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_CONFIG_EMBEDDED_SIM_SLOTSWITCH>", file_path)
    
    print(f"Enable amoled display features.")
    delete_line("    <SEC_FLOATING_FEATURE_LCD_SUPPORT_AMOLED_DISPLAY>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_SUPPORT_AMOLED_DISPLAY>TRUE</SEC_FLOATING_FEATURE_LCD_SUPPORT_AMOLED_DISPLAY>", file_path)
    
    print(f"Enable lcd natural screen mode.")
    delete_line("    <SEC_FLOATING_FEATURE_LCD_SUPPORT_NATURAL_SCREEN_MODE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_LCD_SUPPORT_NATURAL_SCREEN_MODE>TRUE</SEC_FLOATING_FEATURE_LCD_SUPPORT_NATURAL_SCREEN_MODE>", file_path)
    
    print(f"Enable AI UPSCALER.")
    delete_line("    <SEC_FLOATING_FEATURE_MMFW_SUPPORT_AI_UPSCALER>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_MMFW_SUPPORT_AI_UPSCALER>TRUE</SEC_FLOATING_FEATURE_MMFW_SUPPORT_AI_UPSCALER>", file_path)
    
    print(f"Enable double tap to wake.")
    delete_line("    <SEC_FLOATING_FEATURE_SETTINGS_SUPPORT_DEFAULT_DOUBLE_TAP_TO_WAKE>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_SETTINGS_SUPPORT_DEFAULT_DOUBLE_TAP_TO_WAKE>TRUE</SEC_FLOATING_FEATURE_SETTINGS_SUPPORT_DEFAULT_DOUBLE_TAP_TO_WAKE>", file_path)
    
    print(f"Enable google AI search.")
    delete_line("    <SEC_FLOATING_FEATURE_COMMON_GOOGLE_AI_SEARCH>", file_path)
    add_line("    <SEC_FLOATING_FEATURE_COMMON_GOOGLE_AI_SEARCH>TRUE</SEC_FLOATING_FEATURE_COMMON_GOOGLE_AI_SEARCH>", file_path)
    
    

if os.path.exists(esim_fp_file_location):
    os.remove(esim_fp_file_location)
    print(f"Esim Support Removed")


def build_prop_tweak():
    print("Changing default language to en-US.")
    delete_line("ro.product.locale=", build_prop_location)
    add_line("ro.product.locale=en-US", build_prop_location)
    delete_line("ro.surface_flinger.protected_contents=", build_prop_location)
    add_line("ro.surface_flinger.protected_contents=true", build_prop_location)
    add_line("ril.support.dynamic_imei=true", build_prop_location)
    delete_line("fw.max_users=", build_prop_location)
    delete_line("fw.show_multiuserui=", build_prop_location)
    add_line("fw.max_users=5", build_prop_location)
    add_line("fw.show_multiuserui=1", build_prop_location)


system_app = [
    "ARCore",
    "ARDrawing",
    "ARZone",
    "BGMProvider",
    "BixbyWakeup",
    "BlockchainBasicKit",
    "BluetoothTest",
    "Cameralyzer",
    "DictDiotekForSec",
    "EasymodeContactsWidget81",
    "Fast",
    "FactoryAPP_O8",
    "FBAppManager_NS",
    "FunModeSDK",
    "GearManagerStub",
    "HpsAgreement",
    "KidsHome_Installer",
    "LinkSharing_v11",
    "LiveDrawing",
    "MAPSAgent",
    "MdecService",
    "MinusOnePage",
    "Netflix_stub",
    "ParentalCare",
    "PhotoTable",
    "SamSungStickerSource",
    "SamsungPassAutofill_v1",
    "SamsungTTSVoice_de_DE_f00",
    "SamsungTTSVoice_en_GB_f00",
    "SamsungTTSVoice_en_US_f00",
    "SamsungTTSVoice_en_US_l03",
    "SamsungTTSVoice_es_ES_f00",
    "SamsungTTSVoice_es_US_f00",
    "SamsungTTSVoice_fr_FR_f00",
    "SamsungTTSVoice_hi_IN_f00",
    "SamsungTTSVoice_it_IT_f00",
    "SamsungTTSVoice_pl_PL_f00",
    "SamsungTTSVoice_ru_RU_f00",
    "SamsungTTSVoice_th_TH_f00",
    "SamsungTTSVoice_vi_VN_f00",
    "SamsungWeather",
    "SCPMClient",
    "SEIOAgent",
    "SmartReminder",
    "SmartSwitchStub",
    "UnifiedWFC",
    "UniversalMDMClient",
    "VideoEditorLite_Dream_N",
    "VisionIntelligence3.7",
    "VoiceAccess",
    "VTCameraSetting",
    "WebManual",
    "WifiGuider",
    "SamsungTTSVoice_el_GR_f00",
    "SamsungTTSVoice_es_MX_f00",
    "SamsungTTSVoice_pt_BR_f00"
]



system_priv_app = [
    "AppLinker",
    "AppUpdateCenter",
    "AREmoji",
    "AREmojiEditor",
    "AuthFramework",
    "AutoDoodle",
    "AvatarEmojiSticker",
    "AvatarEmojiSticker_S",
    "Bixby",
    "BixbyInterpreter",
    "BixbyVisionFramework3.5",
    "ContainerAgent3",
    "DecoPic",
    "DevGPUDriver-EX2200",
    "DigitalKey",
    "DigitalWellbeing",
    "Discover",
    "DiscoverSEP",
    "EarphoneTypeC",
    "EasySetup",
    "EsimClient",
    "EsimKeyString",
    "EuiccService",
    "FBInstaller_NS",
    "FBServices",
    "FotaAgent",
    "GalleryWidget",
    "GameDriver-EX2100",
    "GameDriver-EX2200",
    "GameDriver-SM8150",
    "GameHome",
    "GameOptimizingService",
    "GameTools_Dream",
    "HashTagService",
    "HealthPlatform",
    "HPSClient",
    "MemorySaver_O_Refresh",
    "KnoxAIFrameworkApp",
    "knoxanalyticsagent",
    "KnoxCore",
    "KnoxMposAgent",
    "KnoxPushManager",
    "knoxvpnproxyhandler",
    "KnoxZtFramework",
    "LedCoverService",
    "LinkToWindowsService",
    "LiveStickers",
    "MateAgent",
    "MultiControl",
    "OMCAgent5",
    "OneDrive_Samsung_v3",
    "OneStoreService",
    "SamsungBilling",
    "SamsungCarKeyFw",
    "SamsungPass",
    "SamsungSmartSuggestions",
    "SCPMAgent",
    "SettingsBixby",
    "SetupIndiaServicesTnC",
    "SingleTakeService",
    "SKTFindLostPhone",
    "SKTHiddenMenu",
    "SKTMemberShip",
    "SKTOneStore",
    "SktUsimService",
    "SmartPush",
    "SmartThingsKit",
    "SmartTouchCall",
    "SOAgent7",
    "SolarAudio-service",
    "SPPPushClient",
    "StatementService",
    "sticker",
    "StickerFaceARAvatar",
    "StoryService",
    "SumeNNService",
    "SVoiceIME",
    "SwiftkeyIme",
    "SwiftkeySetting",
    "SystemUpdate",
    "TADownloader",
    "Tag",
    "TalkbackSE",
    "TaPackAuthFw",
    "TPhoneOnePackage",
    "TPhoneSetup",
    "TWorld",
    "UltraDataSaving_O",
    "Upday",
    "UsimRegistrationKOR",
    "YourPhone_P1_5"
]


def debloat_system_app():
    print(f"Debloating system app.")
    debloat_app_location = f"{debloat_location}/app"
    for folder in system_app:
        source_path = os.path.join(system_app_location, folder)
        target_path = os.path.join(debloat_app_location, folder)

        if os.path.exists(source_path):
            if os.path.exists(target_path):
                try:
                    shutil.rmtree(target_path)
                except Exception as e:
                    continue
        
            try:
                shutil.move(source_path, target_path)
            except Exception as e:
                print(f"{e}")


def debloat_system_priv_app():
    print(f"Debloating system priv app.")
    debloat_priv_app_location = f"{debloat_location}/priv-app"
    for folder in system_priv_app:
        source_path = os.path.join(system_priv_app_location, folder)
        target_path = os.path.join(debloat_priv_app_location, folder)

        if os.path.exists(source_path):
            if os.path.exists(target_path):
                try:
                    shutil.rmtree(target_path)
                except Exception as e:
                    continue
        
            try:
                shutil.move(source_path, target_path)
            except Exception as e:
                print(f"{e}")


def delete_stock_camera_files():
    print("Deleting unnecessary camera files.")
    arcsoft_files = read_file(f"{rom_location}/system/system/etc/public.libraries-arcsoft.txt")
    camera_files = read_file(f"{rom_location}/system/system/etc/public.libraries-camera.samsung.txt")
    all_files = arcsoft_files + camera_files

    for folder in lib_folders:
        file_path = [os.path.join(folder, file_name) for file_name in all_files]
        try:
            delete_files(file_path)
        except Exception as e:
            print(f"Error deleting files: {e}")

    unnecessary_camera_related_folders = ["cameradata", "saiv"]
    delete_folders(f"{rom_location}/system/system", unnecessary_camera_related_folders)


def fix_camera():
    print(f"Fixing camera.")
    delete_stock_camera_files()
    source = "fixes/camera"
    destination = f"{rom_location}/system/system/"
    file_path = f"{rom_location}/system/system/etc/floating_feature.xml"
    print(f"Copying camera fixes.")
    
    for folder in os.listdir(source):
        src_folder_path = os.path.join(source, folder)
        dest_folder_path = os.path.join(destination, folder)
        if os.path.isdir(src_folder_path):
            shutil.copytree(src_folder_path, dest_folder_path, dirs_exist_ok=True)

    try:
        with open(file_path, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if not line.startswith("    <SEC_FLOATING_FEATURE_CAMERA"):
                    file.write(line)
            file.truncate()

    except Exception as e:
        print(f"Error deleting lines in 'floating_feature.xml': {e}")
        return

    lines_to_add = [
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_AI_HIGH_RESOLUTION_MAX_CAPTURE>1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_AI_HIGH_RESOLUTION_MAX_CAPTURE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_ARDOODLE_PEN_TYPE>3d,Pattern,Regular,Highlighter,Glass_lite,Text,Organic_lite</SEC_FLOATING_FEATURE_CAMERA_CONFIG_ARDOODLE_PEN_TYPE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_AVATAR_MAX_FACE_NUM>1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_AVATAR_MAX_FACE_NUM>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_BOKEH>-1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_BOKEH>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_MACRO>-1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_MACRO>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE2>-1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE2>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE_BINNING>-1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE_BINNING>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE_STANDARD_CROP>-1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_TELE_STANDARD_CROP>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_UW>2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_UW>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_WIDE>0</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CAMID_WIDE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_CORE_VERSION>v2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_CORE_VERSION>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_HIGH_RESOLUTION_MAX_CAPTURE>3</SEC_FLOATING_FEATURE_CAMERA_CONFIG_HIGH_RESOLUTION_MAX_CAPTURE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_LLHDR_PROCESSING_TIMEOUT>2000</SEC_FLOATING_FEATURE_CAMERA_CONFIG_LLHDR_PROCESSING_TIMEOUT>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_MEMORY_USAGE_LEVEL>2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_MEMORY_USAGE_LEVEL>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_MYFILTER>1,1,0</SEC_FLOATING_FEATURE_CAMERA_CONFIG_MYFILTER>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_BEAUTY_LEVEL>2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_BEAUTY_LEVEL>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT>80</SEC_FLOATING_FEATURE_CAMERA_CONFIG_NIGHT_FRONT_DISPLAY_FLASH_TRANSPARENT>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_QRCODE_INTERVAL>500</SEC_FLOATING_FEATURE_CAMERA_CONFIG_QRCODE_INTERVAL>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>V1</SEC_FLOATING_FEATURE_CAMERA_CONFIG_STRIDE_OCR_VERSION>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_UW_DISTORTION_CORRECTION>0,109,2,20230131,3264,2448,0,0,0,0</SEC_FLOATING_FEATURE_CAMERA_CONFIG_UW_DISTORTION_CORRECTION>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_VENDOR_LIB_INFO>beauty.samsung.v4,swuwdc.arcsoft.v1,face_landmark.arcsoft.v2_1,facial_attribute.samsung.v1,food.samsung.v1,mfhdr.arcsoft.v1,llhdr.arcsoft.v1,super_night.arcsoft.v3,single_bokeh.samsung.v2,scene_detection.samsung.v1,dual_bokeh.samsung.v1,selfie_correction.samsung.v1,event_detection.samsung.v2,human_tracking_face.arcsoft.v2_1,localtm.samsung.v1_1,facial_restoration.arcsoft.v1,smart_scan.samsung.v2</SEC_FLOATING_FEATURE_CAMERA_CONFIG_VENDOR_LIB_INFO>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_VERSION_FILTER_PROVIDER>6</SEC_FLOATING_FEATURE_CAMERA_CONFIG_VERSION_FILTER_PROVIDER>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_CONFIG_WIDE_DISTORTION_CORRECTION>0,0,0,0,0,0,0,0,0,0</SEC_FLOATING_FEATURE_CAMERA_CONFIG_WIDE_DISTORTION_CORRECTION>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_DOCUMENTSCAN_SOLUTIONS>CV_DEWARPING</SEC_FLOATING_FEATURE_CAMERA_DOCUMENTSCAN_SOLUTIONS>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_GRAW_CONFIG_MFP_PIPELINE_MODE>V1</SEC_FLOATING_FEATURE_CAMERA_GRAW_CONFIG_MFP_PIPELINE_MODE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_AVATAR>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_AVATAR>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_DOWNLOAD_EFFECT>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_DOWNLOAD_EFFECT>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_NIGHT_FRONT_DISPLAY_FLASH>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_NIGHT_FRONT_DISPLAY_FLASH>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_QRCODE>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_QRCODE>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_TORCH_BRIGHTNESS_LEVEL>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_TORCH_BRIGHTNESS_LEVEL>\n",
        "    <SEC_FLOATING_FEATURE_CAMERA_SUPPORT_VIDEO_PALM>TRUE</SEC_FLOATING_FEATURE_CAMERA_SUPPORT_VIDEO_PALM>\n"
    ]

    try:
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.writelines(lines[:-1])
            file.writelines(lines_to_add)
            file.write(lines[-1])

    except Exception as e:
        print(f"Error updating 'floating_feature.xml': {e}")


def fix_selinux():
    print(f"Fixing selinux issue.")
    keywords_to_remove = ['audiomirroring', 'fabriccrypto', 'hal_dsms', 'qb_id_prop', 'uwb_regulation_skip_prop', 'proc_compaction', 'sec_diag', 'sbauth']
    try:
        with open(selinux_file_location, 'r') as file:
            lines = file.readlines()

        filtered_lines = [line for line in lines if not any(keyword in line for keyword in keywords_to_remove)]

        with open(selinux_file_location, 'w') as file:
            file.writelines(filtered_lines)
    except FileNotFoundError:
        print(f"Error: File '{selinux_file_location}' not found.")


def add_stock_boot_animation():
    print(f"Adding stock boot animation.")
    folders = [f for f in os.listdir(stock_media) if os.path.isdir(os.path.join(stock_media, f))]
    for folder in folders:
        source_path = os.path.join(stock_media, folder)
        destination_path = os.path.join(f"{rom_location}/system/system", folder)
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)


def fix_system_ext():
    system_ext_folder_location = f"{rom_location}/system/system_ext"
    system_ext_symlink_location = f"{rom_location}/system/system/system_ext"
    print(f"Fixing system_ext.")
    if os.path.exists(system_ext_symlink_location) and os.path.isfile(system_ext_symlink_location):

        ## system_ext_file_contexts
        delete_line("/system_ext u:object_r:system_file:s0", "Config/system_ext_file_contexts.txt")
        delete_line("/system_ext/ u:object_r:system_file:s0", "Config/system_ext_file_contexts.txt")
        
        ## system_ext_filesystem_config
        delete_line("/ 0 0 0755", "Config/system_ext_filesystem_config.txt")
        delete_line("system_ext/ 0 0 0755", "Config/system_ext_filesystem_config.txt")

        ## system_file_contexts
        delete_line("/system/system_ext u:object_r:system_file:s0", "Config/system_file_contexts.txt")
        delete_line("/system_ext u:object_r:system_file:s0", "Config/system_file_contexts.txt")
        
        ## system_filesystem_config
        delete_line("system/system_ext 0 0 0644", "Config/system_filesystem_config.txt")
        delete_line("system_ext 0 0 0755", "Config/system_filesystem_config.txt")

    ## Remove system/system_ext symlink file
    if os.path.exists(system_ext_symlink_location) and os.path.isfile(system_ext_symlink_location):
        try:
            os.remove(system_ext_symlink_location)
        except Exception as e:
            print(f"An error occurred while trying to delete the file: {e}")

    ## Remove system/system_ext folder
    if os.path.exists(system_ext_folder_location) and os.path.isdir(system_ext_folder_location):
        try:
            shutil.rmtree(system_ext_folder_location)
        except Exception as e:
            print(f"An error occurred while deleting the directory: {e}")
    
    ## Update system_ext_file_contexts (1)
    with open("Config/system_ext_file_contexts.txt", 'r') as file:
        lines = file.readlines()

    line_starts_with_system = any(line.startswith('/system/system/system_ext/') for line in lines)

    if not line_starts_with_system:
        updated_lines = [f'/system{line}' if line.startswith('/system_ext/') else line for line in lines]
    else:
        updated_lines = lines

    with open("Config/system_ext_file_contexts.txt", 'w') as file:
        file.writelines(updated_lines)
        
    ## Update system_ext_filesystem_config (1)
    with open("Config/system_ext_filesystem_config.txt", 'r') as file:
        lines = file.readlines()

    line_starts_with_system = any(line.startswith('system/system_ext/') for line in lines)

    if not line_starts_with_system:
        updated_lines = [f'system/{line}' if line.startswith('system_ext/') else line for line in lines]
    else:
        updated_lines = lines

    with open("Config/system_ext_filesystem_config.txt", 'w') as file:
        file.writelines(updated_lines)
        
    ## Update system_ext_file_contexts (1)
    add_line("/system/system_ext u:object_r:system_file:s0", "Config/system_ext_file_contexts.txt")
    add_line("/system_ext u:object_r:system_file:s0", "Config/system_ext_file_contexts.txt")
    
    ## Update system_ext_filesystem_config (2)
    add_line("system/system_ext 0 0 755", "Config/system_ext_filesystem_config.txt")
    add_line("system_ext 0 0 644", "Config/system_ext_filesystem_config.txt")
    
    ## system_ext_file_contexts.txt final update
    with open("Config/system_ext_file_contexts.txt", 'r') as ext_file:
        ext_content = ext_file.read()

    with open("Config/system_file_contexts.txt", 'a') as file_contexts_file:
        file_contexts_file.write(ext_content)

    ## system_filesystem_config.txt final update
    with open("Config/system_ext_filesystem_config.txt", 'r') as ext_file:
        ext_content = ext_file.read()

    with open("Config/system_filesystem_config.txt", 'a') as file_contexts_file:
        file_contexts_file.write(ext_content)

    ## Moving system_ext to system/system
    if os.path.exists(f"{rom_location}/system_ext"):
        if not os.path.exists(f"{rom_location}/system/system/system_ext"):
            shutil.move(f"{rom_location}/system_ext", f"{rom_location}/system/system")
    



async def sendMessage(message, text):
    return await message.reply(text=text, quote=True)


async def editMessage(message, text):
    try:
        await message.edit(text=text)
    except:
        pass


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))

    return wrapper


async def create_drive_folder(drive_service, folder_name, parent_folder_id):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


@new_task
async def upload_in_drive(file_path, drive_folder_id):
    file_name = os.path.basename(file_path)
    
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("No valid credentials available. You need to obtain new OAuth tokens.")

    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
    
    with open(file_path, 'rb') as f:
        media_body = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype='application/octet-stream', resumable=True)
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media_body,
        supportsAllDrives=True,
        fields='id'
    ).execute()
    return file


@new_task
async def samsung_fw_extract(client, message):
    args = message.text.split()
    folder_name = args[1] if len(args) > 1 else ''
    link = args[2] if len(args) > 2 else ''

    if not folder_name or not link:
        return await message.reply("Please provide a folder_name and link. Usage: /fw S24 www.sm_fw.com")

    banner = f"<b>Samsung FW Extractor By Al Noman</b>\n"
    status = await sendMessage(message, banner)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    banner = f"\n{banner}\nFirmware downloading."
    await editMessage(status, banner)

    try:
        subprocess.run(['wget', '-O', 'fw.zip', '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"', f'{link}'], cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\nFirmware download complete.\n"
    await editMessage(status, banner)
    
    banner = f"\n{banner}\n<b>Step 1:</b> Extracting firmware zip."
    await editMessage(status, banner)
    try:
        subprocess.run('7z x fw.zip && rm -rf firmware.zip && rm -rf *.txt && for file in *.md5; do mv -- "$file" "${file%.md5}"; done', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 2:</b> Extracting tar files."
    await editMessage(status, banner)
    try:
        subprocess.run('for file in *.tar; do tar -xvf "$file"; done', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("find . -type f ! -name 'super.img.lz4' ! -name 'optics.img.lz4' ! -name 'prism.img.lz4' ! -name 'boot.img.lz4' -delete", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf *.tar', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf meta-data', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 3:</b> Extracting lz4 files."
    await editMessage(status, banner)
    try:
        subprocess.run('for file in *.lz4; do lz4 -d "$file" "${file%.lz4}"; done', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 4:</b> Converting sparse super.img to raw super.img."
    await editMessage(status, banner)
    try:
        subprocess.run("simg2img super.img super_raw.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("rm -rf super.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("mv super_raw.img super.img", shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
            banner = f"\n{banner}\n{e}."
            await editMessage(status, banner)
            return

    banner = f"\n{banner}\n<b>Step 5:</b> Extracting all partitions from super.img"
    await editMessage(status, banner)
    try:
        subprocess.run('lpunpack super.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf super.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 6:</b> Compressing all img to xz level 9."
    await editMessage(status, banner)
    try:
        subprocess.run('for i in *.img; do 7z a -mx9 "${i%.*}.img.xz" "$i"; done && rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        subprocess.run('rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 7:</b> Creating folder in Google Drive."
    await editMessage(status, banner)

    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("No valid credentials available. You need to obtain new OAuth tokens.")

    drive_service = build('drive', 'v3', credentials=credentials)
    drive_folder_id = await create_drive_folder(drive_service, folder_name, DRIVE_FOLDER_ID)

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading all files in google drive."
    await editMessage(status, banner)
    for file_name in os.listdir(DOWNLOAD_DIR):
        if file_name.endswith('.xz'):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            await upload_in_drive(file_path, drive_folder_id)

    banner = f"\n{banner}\n\n<b>Upload Completed.</b>\nFolder link: https://drive.google.com/drive/folders/{drive_folder_id}"
    await editMessage(status, banner)
    subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("fw") & CustomFilters.owner))
