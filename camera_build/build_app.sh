#/bin/bash
rm -r build dist Camera\ v1.spec
# pyinstaller --windowed --onefile --clean --noconfirm --debug all -w -i camera.icns  ../Camera\ V1.2.py
pyinstaller.exe --windowed --onefile --clean --noconfirm --debug all --add-binary="C:\Users\lin\AppData\Local\Programs\Python\Python39\Lib\site-packages\pyzbar\libiconv.dll":"pyzbar" "../Windows_VideoStreamApp.py" --name="Camera v1"