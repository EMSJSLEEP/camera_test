#/bin/bash
rm -r build dist Camera\ v1.spec
# pyinstaller --windowed --onefile --clean --noconfirm --debug all -w -i camera.icns  ../Camera\ V1.2.py
pyinstaller --windowed --onefile --clean --noconfirm --debug all --icon=./camera.icns --add-binary=/usr/local/bin/uvc-util:. ../Camera\ V1.2.py --name=Camera_light