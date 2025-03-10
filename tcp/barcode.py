# -*- coding: utf-8 -*-
import os
import ctypes

def load_lib():
    '''
    Load barcode library function
    :example:
            lib = load_lib()
    '''

    lib_file = os.environ.get('', '/usr/local/lib/') + 'libbarcode.so'
    if not os.access(lib_file, os.R_OK):
        return None
    return ctypes.cdll.LoadLibrary(lib_file)

class BarCode(object):
  rpc_public_api =['get_socket_port', 'enable_camera']
  def __init__(self, port):
    self._barcode_lib_inst = load_lib()
    if self._barcode_lib_inst is None:
      raise Exception('Load BarCode library failure!')
    config_path = os.path.split(os.path.realpath(__file__))[0]+"/barcode-"+str(port)+".json"
    dev_path = "/dev/video"+str(port)
    ret = self._barcode_lib_inst.Init(bytes(config_path), bytes(dev_path))
    if(1 == ret):
      raise Exception('Init BarCode library failure!')
    
  def get_socket_port(self):
    '''
    Gets the network port that the camera uses to transmit image data.

    Returns:
      int, the port camera used

    Examples:
      barcode.get_socket_port()

    '''
    return self._barcode_lib_inst.get_video_socket_port()
  
  def enable_camera(self, enable):
    '''
    Enable the camera to store pictures to the buffer

    Args:
      enable: int, 0 or 1 only
    
    Examples:
      barcode.enable_camera(1)

    '''
    assert enable==1 or enable==0
    self._barcode_lib_inst.enable_camera(enable)