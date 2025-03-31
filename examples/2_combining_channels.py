from trueformawg import TrueFormAWG, VISAdevices, import_awg_txt

awgs = VISAdevices()

trueform_address = awgs.list[1]
# Configure channel 1
awg_ch1 = TrueFormAWG(trueform_address,1)
awg_ch1.combine_channels()

awg_ch1.set_indipendent()
