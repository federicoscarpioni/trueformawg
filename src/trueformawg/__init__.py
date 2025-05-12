'''
This class create an instrument istance for the Trueform arbitrary wave generator.
The device is controlled using pyvisa protocol ans SCPI language. The SCPI commands
used are some 
'''
import pyvisa
import numpy as np

class VISAdevices():
    def __init__(self):
        self.resource = pyvisa.ResourceManager()
        self.update_list()
        
    def update_list(self):
        self.list = self.resource.list_resources()

class TrueFormAWG():
    '''
    This class is used to control the Trueform arbitrary waveform generator (awg).
    After initialisation (connection to a device specific channel) the device
    can be remotly turned on and off, parameters can be updated and arbitrary
    wavefor (AWF) in  loaded on the device non-volitle memory and loaded on the 
    volatile memory for usage.
    '''
    
    
    def __init__(self, address, channel):
        # Initialize attributes
        self.address = address
        self.channel = channel
        
        # Perform the connection
        self.rm = pyvisa.ResourceManager()
        self.device = self.rm.open_resource(address)
        self.device.timeout = 300000 # Chosen arbitrary
    

    def reset(self):
        '''Reset the instrument and clear the memory'''
        
        # Reset
        self.device.write('*RST;*CLS')
        # Clear volatile memory
        self.device.write(':SOUR1:DATA:VOL:CLE')
        # Clear the internal memory of channel 1
        self.device.write(':SOURce%d:DATA:VOLatile:CLEar' % (1))
        # Clear the internal memory of channel 1
        self.device.write(':SOURce%d:DATA:VOLatile:CLEar' % (2))
        print('Available memory (in samples):' + self.device.query('SOURce1:DATA:VOLatile:FREE?'))
    
    def clear_ch_mem(self):
        self.device.write(f':SOURce{self.channel}:DATA:VOLatile:CLEar')
        print(f'Cleared memory of channel {self.channel}')

        
    def load_awf(self, AWFname, AWF):    
        ''' 
        Load waveform from computer RAM to internal storage of Trueform AWG
        '''
        self.device.write('FORM:BORD NORM') # set the byte order
        print('Loading waveform to awg...')
        bytes_sent = self.device.write_binary_values(f'SOUR{self.channel}:DATA:ARB {AWFname},', AWF, datatype='f', is_big_endian=True)
        print(bytes_sent)
        self.device.write('*WAI') # Wait for the waveform to load
        print('Procedure complete.')
        print(self.device.query('SYSTEM:ERROR?')) 
        
    
    def select_awf(self, AWFname):
        ''' Load waveform from internal storage to volatile memory of Trueform AWG'''
        
        # Turn on arb function
        self.device.write(f':SOUR{self.channel}:FUNC %s' % ('ARB'))
        # Select my arb from the internal memory of the instrument
        self.device.write(f':SOUR{self.channel}:FUNC:ARB "%s"' % (AWFname))
    
    def avalable_memory(self):
        print('Available memory (in samples): ', self.device.query(f'SOURce{self.channel}:DATA:VOLatile:FREE?'))
    
    def print_errors(self):
        print(self.device.query('SYSTEM:ERROR?')) 

    
    def set_sample_rate(self, sampleRate):
        self.device.write(':SOURce%d:FUNCtion:ARBitrary:SRATe %G' % (self.channel, sampleRate))


    def set_amplitude(self, amplitude):
        self.device.write(':SOURce%d:VOLTage %G' % (self.channel, amplitude)) 
        
     
    def set_offset(self, offset):
        self.device.write(':SOURce%d:VOLTage:OFFSet %G' % (self.channel, offset))
        
        
    def set_Z_out_infinite(self):
        self.device.write(':OUTPut%d:LOAD %s' % (self.channel, 'INF'))

    def set_Z_out(self, z_out):
        self.device.write(':OUTPut%d:LOAD %s' % (self.channel, z_out))

    def combine_channels(self, source_channel = 'CH2'):
        '''
        Combine the signals digitally before sending to the DAC. Source channel
        must a be a string 'CH1' or 'CH2' (or 'NONE')
        '''
        if self.channel == 1:
            pass
        elif self.channel == 2:
            source_channel = 'CH1'
        self.device.write(':SOURce%d:COMBine:FEED %s' % (self.channel, source_channel))


    def set_indipendent(self):
        self.device.write(':SOURce%d:COMBine:FEED %s' % (self.channel, 'NONE'))

    def turn_on(self):
        self.device.write(':OUTPut%d %d' % (self.channel, 1)) 
        print('Awg turned on')
                        
    def turn_off(self):
        self.device.write(':OUTPut%d %d' % (self.channel, 0)) 
        print('Awg turned off')
        
    def disconnect(self):
        self.device.close()
        self.rm.close()
        

def import_awg_npy(multisine_path):
    ''' 
    Load awg in memory from npy file and convert to proper type and to list to 
    be accepted by the waveform generator.
    '''
    multisine = np.load(multisine_path)
    multisine = multisine.astype(np.float32)
    multisine = multisine.tolist()
    return multisine

def import_awg_txt(multisine_path):
    ''' 
    Load awg in memory from npy file and convert to proper type and to list to 
    be accepted by the waveform generator.
    '''
    multisine = np.loadtxt(multisine_path)
    multisine = multisine.astype(np.float32)
    multisine = multisine.tolist()
    return multisine
