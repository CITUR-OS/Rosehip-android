echo key.alias=android>local.properties
echo key.store.password=android>>local.properties
echo key.alias.password=android>>local.properties
echo key.store=android.keystore>>local.properties
set sdk=sdk.dir=android-sdk
echo %sdk:\=\\%>>local.properties
apache-ant\\bin\\ant.bat clean release install
android-sdk\\platform-tools\\adb.exe push main.1.com.Rosehip.myapp.obb /mnt/sdcard/main.1.com.Rosehip.myapp.obb
move main.1.com.Rosehip.myapp.obb bin/
android-sdk\\platform-tools\\adb.exe shell am start -W -a android.intent.action.MAIN com.Rosehip.myapp/org.renpy.android.PythonActivity
