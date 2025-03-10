import subprocess
import re
import os
from Foundation import NSArray, NSAutoreleasePool
from AVFoundation import AVCaptureDevice
from pathlib import Path


class Tools(object):
    def __init__(self, camera_num=None):
        self.current_directory = str(Path(__file__).parent.resolve())
        if camera_num!=None:
            self.support_settings = self.get_camera_support_settings(camera_num)
            self._camera = camera_num
            self.ex_minimum, self.ex_maximum = self.get_camera_settings('exposure-time-abs')
            self.fo_minimum, self.fo_maximum = self.get_camera_settings('focus-abs')
        else:
            self.ex_minimum, self.ex_maximum = False, False
            self.fo_minimum, self.fo_maximum = False, False
        
    def get_camera_support_settings(self, camera_num):
        command = self.current_directory + '/uvc-util -I {} -c'.format(camera_num)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        return result.stdout.splitlines()
        
    def configure_settings(self, _config, value):
        r_config = '  '+ _config 
        try:
            assert r_config in self.support_settings 
            if _config ==  'focus_abs':
                value = min(self.fo_maximum, max(self.fo_minimum, value))
            else:
                value = min(self.ex_maximum, max(self.ex_minimum, value))
            command =  self.current_directory + '/uvc-util -I {} -s {}={}'.format(self._camera, r_config, value)
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                return True
            else:
                return False
        except AssertionError as e:
            return "error paramters"    
        
    def get_camera_settings(self, _config):
        r_config = '  '+ _config 
        try:
            assert r_config in self.support_settings
            command =  self.current_directory + '/uvc-util -I {} -S {}'.format(self._camera, r_config)
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True).stdout.splitlines()
            key1, min  = map(str.strip, result[4].split(':'))
            key2, max  = map(str.strip, result[5].split(':'))
            return int(min), int(max)
        except AssertionError as e:
            return False, False
    
    def set_ex_auto_mode(self, auto):
        assert auto in [True, False]
        auto = 8 if auto else 1
        r_config = "auto-exposure-mode"
        command =  self.current_directory + '/uvc-util -I {} -s {}={}'.format(self._camera, r_config, auto)
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            return True
        else:
            return False 
    
    def set_fo_auto_mode(self, auto):
        assert auto in [True, False]
        auto = 1 if auto else 0
        r_config = "auto-focus"
        command =  self.current_directory + '/uvc-util -I {} -s {}={}'.format(self._camera, r_config, auto)
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            return True
        else:
            return False
    
    def get_devices(self):
        command =  self.current_directory + '/uvc-util --list-devices'
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True).stdout.splitlines()
        result = {}
        for s in output:
            match = re.search(r'(\d+)\s+0x(\w+):\w+\s+0x(\w+)\s+\S+\s+(.+)$', s)
            if match:
                index = match.group(1)
                id_value = match.group(2)
                extracted_value = match.group(3)
                key = match.group(4).strip()
                result[key] = {'vendor_id': id_value, 'index': index, 'position_id': extracted_value}
        sorted_result = dict(sorted(result.items(), key=lambda x: int(x[1]['index'])))
        return sorted_result
    
    def get_mac_cameras(self):
        try:
            result = subprocess.run(['system_profiler', 'SPCameraDataType'], capture_output=True, text=True)
            devices = re.findall(r'^(.*?):(.*)', result.stdout, re.MULTILINE)
            camera_devices = [line.strip() for _, line in devices if 'Camera' in line]
            return camera_devices
        except Exception as e:
            return []
    
    def get_camera_uuid_and_name(self):
        pool = NSAutoreleasePool.alloc().init()
        devices = AVCaptureDevice.devicesWithMediaType_("vide")
        camera_uuid_name = [[device.uniqueID(), device.localizedName(), device.modelID()] for device in devices]
        return camera_uuid_name

    def get_camera_id(self):
        info_dict = {}
        camera_all_info_list = self.get_camera_uuid_and_name()
        vendor_id_pattern = re.compile(r'VendorID_(\d+)')
        product_id_pattern = re.compile(r'ProductID_(\d+)')
        # print(f"\n{camera_all_info_list}\n")

        for index, camera_info in enumerate(camera_all_info_list):
            vendor_match = vendor_id_pattern.search(camera_info[2])
            product_match = product_id_pattern.search(camera_info[2])

            if vendor_match and product_match:
                vendor_id = vendor_match.group(1)
                product_id = product_match.group(1)
                info_dict[f"CAMERA{index}"] = {
                    "vendor_id": vendor_id,
                    "product_id": product_id,
                    "position_id": camera_info[0],
                    #新增参数
                    "camera_name": camera_info[1]
                }
            else:
                info_dict[f"CAMERA{index}"] = {
                    "vendor_id": None,
                    "product_id": None,
                    "position_id": camera_info[0],
                    #新增参数
                    "camera_name": camera_info[1]
                }
        sorted_camera_dict = dict(sorted(info_dict.items(), key=lambda x: [ord(c) for c in x[1]['position_id']]))
        renamed_camera_dict = {f'CAMERA{i}': value for i, (_, value) in enumerate(sorted_camera_dict.items(), start=0)}        
        return renamed_camera_dict

    def is_hex_stings(self, s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False  

if __name__ == '__main__':
    x = Tools()
    # print(x.get_devices())
    print(x.get_camera_id())
    # print(x.get_mac_cameras())
    # print(x.get_camera_uuid_and_name())
