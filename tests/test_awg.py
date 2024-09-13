# -*- coding: utf-8 -*-
from trueformawg.trueformawg import TrueFormAWG, VISAdevices, import_awg_txt

awgs = VISAdevices()

trueform_address = awgs.list[0]
# Configure channel 1
awg_ch1 = TrueFormAWG(trueform_address,1)
awg_ch1.clear_ch_mem()
multisine_potentio_path = 'E:/multisine_collection/2409131232multisine_1kHz-100mHz_8ptd_fgen10kHz_random_phases_flat_normalized/waveform.txt'
multisine_potentio = import_awg_txt(multisine_potentio_path)
awg_ch1.load_awf('ms_galvano', multisine_potentio) # Keep the name short or it gives an error
awg_ch1.avalable_memory()
awg_ch1.select_awf('ms_galvano')
awg_ch1.set_Z_out_infinite()
awg_ch1.set_sample_rate(10000) # !!! Softcode this!
awg_ch1.set_amplitude(0.050) 
# awg_ch1.set_offset(0)
awg_ch1.turn_on()

awg_ch1.turn_off()
