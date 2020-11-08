from subprocess import check_call
from os import rename
check_call(["apache-ant\\bin\\ant.bat", "clean", "release", "install"])
check_call(["android-sdk\\platform-tools\\adb.exe", "push", "main.1.com.Rosehip.myapp.obb", "/mnt/sdcard/main.1.com.Rosehip.myapp.obb"])
rename("main.1.com.Rosehip.myapp.obb", "bin/main.1.com.Rosehip.myapp.obb")
check_call(["android-sdk\\platform-tools\\adb.exe", "shell","am", "start","-W","-a", "android.intent.action.MAIN","com.Rosehip.myapp/org.renpy.android.PythonActivity"])