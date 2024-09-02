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
        
    # def clear_ch2(self):
    #     self.device.write(':SOURce%d:DATA:VOLatile:CLEar' % (2))
    #     print('Cleared memory of channel 2')
        
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
        '''
        Update the value of AWF sample rate
        
        Parameters
        ----------
        AWFname: string
                 Name of the waveform to load, must contain ".arb" extension.
        '''
        
        self.device.write(':SOURce%d:FUNCtion:ARBitrary:SRATe %G' % (self.channel, sampleRate))


    def set_amplitude(self, amplitude):
        '''Update the value of AWF amplitude (reference from msq not peak to peak)''' #!!! This has to be checked

        self.device.write(':SOURce%d:VOLTage %G' % (self.channel, amplitude)) 
        
     
    def set_offset(self, offset):
        '''Update the value of AWF offset voltage'''

        self.device.write(':SOURce%d:VOLTage:OFFSet %G' % (self.channel, offset))
        
        
    def set_Z_out_infinite(self):
        '''Set the output impedance value of the Truferom AWG to inifinite'''

        self.device.write(':OUTPut%d:LOAD %s' % (self.channel, 'INF'))
        
        
    def turn_on(self):
        
        self.device.write(':OUTPut%d %d' % (self.channel, 1)) 
        
                        
    def turn_off(self):
        self.device.write(':OUTPut%d %d' % (self.channel, 0)) 
        
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
    
#%%
    
if __name__ == '__main__':
    import numpy as np
    multisine_path = 'C:/Users/prolibs/Documents/Users_files/Federico/Python_code/dEIS_waveform_generation/CC003003_5k-10m_8ptd.npy'
    # multisine = np.load(multisine_path)
    # multisine = multisine.astype(np.float32)
    # multisine = multisine.tolist()
    multisine = import_awg_npy(multisine_path)
    trueform_address = 'USB0::0x0957::0x4B07::MY59000581::0::INSTR'
    awg_ch1 = TrueFormAWG(trueform_address,1)
    awg_ch1.avalable_memory()
    awg_ch1.clear_ch_mem()
    awg_ch1.avalable_memory()
    awg_ch1.load_awf('multisine2', multisine)
    awg_ch1.select_awf('multisine2')
    awg_ch1.set_amplitude(0.01)
    awg_ch1.set_offset(0)
    awg_ch1.set_Z_out_infinite()
    # awg_ch1.disconect()