#!/usr/bin/env python 

import os, sys, subprocess, argparse
from androguard.core.bytecodes import apk

#APIMONITOR_CONFIG           = r'/home/santoku/work/APIMonitor-beta/config/default_api_collection'
APIMONITOR_CONFIG           = r'/home/santoku/share/lab11/APIMonitor-beta/config/default_api_collection'
APIMONITOR_CONFIG_COMMENT   = '# added by me'
APIMONITOR_PATH             = r'/home/santoku/share/lab11/APIMonitor-beta/apimonitor.py'
JDBRC_PATH                  = r'/home/santoku/share/lab11/brk.jdbrc'
WORK_DIR                    = r'/home/santoku/host'

APIMONITOR_APIS = [
    '# http request related',
	'Lorg/apache/http/client/methods/HttpPost;-><init>',
	'Lorg/apache/http/message/BasicNameValuePair;-><init>',
	'Lorg/apache/http/client/HttpClient;->execute',
	'Lorg/apache/http/client/methods/HttpGet;-><init>',
    '# phone related',
    	'Landroid/telephony/TelephonyManager;->getNetworkOperatorName',
	'Landroid/telephony/TelephonyManager;->getLine1Number',
	'Landroid/telephony/TelephonyManager;->getNetworkType',
	'Landroid/telephony/TelephonyManager;->getCellLocation',
	'Landroid/telephony/TelephonyManager;->listen',
	'Landroid/telephony/PhoneStateListener;-><init>',
	'Landroid/telephony/gsm/GsmCellLocation;->getCid',
	'Landroid/telephony/gsm/GsmCellLocation;->getLac',
	'Landroid/telephony/cdma/CdmaCellLocation;->getSystemId',
	'Landroid/telephony/cdma/CdmaCellLocation;->getNetworkId',
	'Landroid/telephony/cdma/CdmaCellLocation;->getBaseStationId',
	'Landroid/telephony/TelephonyManager;->getDeviceId',
    '# sms related',
    	'Landroid/telephony/gsm/SmsManager;->sendTextMessage',
    '#shared preferences',
	'Landroid/content/SharedPreferences$Editor;->putString',
	'Landroid/content/SharedPreferences;->getString',
	'Landroid/content/SharedPreferences$Editor;->putInt',
	'Landroid/content/SharedPreferences$Editor;->putBoolean',
	'Landroid/content/SharedPreferences;->getInt',
	'Landroid/content/SharedPreferences;->getBoolean',
    '# reflection related',
    	'Ljava/lang/Class;->forName',
    	'Ljava/lang/Class;->getMethods',
    	'Landroid/location/LocationManager;->getBestProvider',
	'Landroid/location/LocationManager;->requestLocationUpdates',
	'Landroid/location/LocationManager;->getLastKnownLocation',
	'Landroid/location/Location;->getLongitude',
	'Landroid/location/Location;->getLatitude',
    '# methods of Context class',
    	'Landroid/content/Context;->sendBroadcast',
    	'Landroid/content/Context;->startActivity',
    	'Landroid/content/Context;->sendBroadcast',
	'Landroid/content/Context;->sendOrderedBroadcast',
	'Landroid/content/Context;->sendStickyBroadcast',
	'Landroid/content/Context;->sendStickyOrderedBroadcast',
	'Landroid/content/Context;->startService',
	'Landroid/content/Context;->getSystemService',
	'Landroid/content/Context;->getSharedPreferences',
    '# process related',
    	'Landroid/os/Process;->killProcess',
    '# FileIO related',
    	'Ljava/io/File;-><init>',
   	 'Ljava/io/File;->exists',
    	'Ljava/io/File;->mkdirs',
    	'Ljava/io/File;->delete',
    	'Ljava/io/File;->listFiles',
	'Ljava/io/File;->getName',
    '# external storage related',
    	'Landroid/os/Environment;->getExternalStorageState',
]

def runcmd(cmdline):
    print 'Running [%s]...' % cmdline
    proc = subprocess.Popen(cmdline, close_fds=True, shell=True)
    proc.wait()

def createJDBRC(apkobj, apkbn):
	h = open(JDBRC_PATH, 'wb')
	#apkpath = "/home/santoku/share/lab11/sample4.apk"
	#apkobj = apk.APK(apkpath)
    # create breakpoints for each activity, broadcast receiver and service

	#parser = argparse.ArgumentParser(description='Decompiler for APKs')
	#parser.add_argument('apkpath', help='path to apk')
	#args = parser.parse_args()
	#apkpath = args.apkpath
	#apkobj = apk.APK(apkpath)

	if apkobj.get_activities():
		print "APK activities:"
		for actv in apkobj.get_activities():
			print actv
			h.write('stop in ')
			h.write(actv)
			h.write(".onCreate\n")
			h.write("stop in ")
			h.write(actv)
			h.write(".onResume\n")
			h.write("stop in ")
			h.write(actv)
			h.write(".onPause\n")
			h.write("stop in ")
			h.write(actv)
			h.write(".onStop\n")
	else:
		print "Can't find Activities"

	if apkobj.get_services():
		print "APK services:"
		for serv in apkobj.get_services():
			print serv
			h.write("stop in ")
			h.write(serv)
			h.write(".onReceive\n")
				
	else:
		print "Can't find Services"
		
	if apkobj.get_receivers():
		print "APK receivers:"
		for recv in apkobj.get_receivers():
			print recv
			h.write("stop in ")
			h.write(recv)
			h.write(".OnCreate\n")
			
	else:
		print "Can't find BroadcastReceivers"
			
    # create other breakpoints ex. android.telephony.SmsManager.sendTextMessage
	h.write('stop in android.telephony.SmsManager.sendTextMessage\n')
	h.write('use %s/%s-apktool-d/smali/\n' % (WORK_DIR, apkbn))
	h.close()   
    
def createAPIMonitorConfig():
    configContent = open(APIMONITOR_CONFIG, 'rb').read()
    pos = configContent.find(APIMONITOR_CONFIG_COMMENT)
    if pos != -1:
        configContent = configContent[:pos]
    configContent += APIMONITOR_CONFIG_COMMENT + '\n' + '\n'.join(APIMONITOR_APIS)
    open(APIMONITOR_CONFIG, 'wb').write(configContent)
    
parser = argparse.ArgumentParser(description='Prepare APKs for debug')

parser.add_argument('apkpath', help='path to apk')
parser.add_argument('-jdb', action='store_true', help='create .jdbrc file')
parser.add_argument('-apimon', action='store_true', help='create apimonitor config file')

args = parser.parse_args()

apkpath = args.apkpath
apkbn = os.path.splitext(apkpath)[0]
print 'Preparing for debug [%s]' % apkpath

apkobj = apk.APK(apkpath) 

if args.apimon:
    createAPIMonitorConfig()
    # run apimonitor
    cmdline = r'%s -o %s-apimonitor %s' % (APIMONITOR_PATH, apkbn, apkpath)
    runcmd(cmdline)

    apkpath = '%s-apimonitor/%s_new.apk' % (apkbn, apkbn)

if args.jdb:
    # run apktool to decode in debug mode (-d option)
    cmdline = 'apktool d -d -f -o %s-apktool-d %s' % (apkbn, apkpath)
    runcmd(cmdline)
    print 'CREATED: %s_apktool-d' % apkbn
    
    # build for debug
    cmdline = 'apktool b -d -f -o %s_unalgn_dbg.apk %s-apktool-d' % (apkbn, apkbn)
    runcmd(cmdline)

    # generate key
    if not os.path.isfile('mykeystore.keystore'):
        cmdline = r'keytool -genkey -v -keystore mykeystore.keystore -alias my_key -keyalg RSA -keysize 2048 -validity 10000'
        runcmd(cmdline)
    # sign apk
    cmdline = r'jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore mykeystore.keystore %s_unalgn_dbg.apk my_key' % apkbn
    runcmd(cmdline)
    # align apk
    cmdline = r'zipalign -f -v 4 %s_unalgn_dbg.apk %s_dbg.apk' % (apkbn, apkbn)
    runcmd(cmdline)

    #os.remove('%s_unalgn_dbg.apk' % apkbn)
    print 'CREATED: %s_dbg.apk' % apkbn
    createJDBRC(apkobj, apkbn)
    
