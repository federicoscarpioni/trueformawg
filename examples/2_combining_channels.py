from trueformawg.trueformawg import TrueFormAWG, VISAdevices, import_awg_txt

awgs = VISAdevices()

trueform_address = awgs.list[0]
# Configure channel 1
awg_ch1 = TrueFormAWG(trueform_address,1)
awg_ch1.combine_channels(1,2)

awg_ch1.set_indipendent()
