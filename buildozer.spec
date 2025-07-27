[app]
title = Web View
package.name = webview
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0
requirements = python3,flask,opencv-python,opencv-python-headless,numpy

# Android settings
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.accept_sdk_license = True

# Architecture
android.arch = arm64-v8a

# Permissions
android.permissions = CAMERA,INTERNET

# Services
services = 

# Icon configuration
icon.filename = %(source.dir)s/icon.png

# Theme
android.theme = Theme.MaterialComponents.Light.NoActionBar

# P4A
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1