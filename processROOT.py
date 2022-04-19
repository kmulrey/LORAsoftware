import numpy as np
import ROOT, glob, os, sys
#import read_root_files as read
#import matplotlib.pyplot as plt
import datetime
from datetime import datetime, timedelta
from datetime import date
from optparse import OptionParser
import pickle as pickle
#from sklearn.externals import joblib
#sys.path.insert(1, '../LORA_software_V2/')
#import LORAparameters
#import process_functions
#import read_functions
#import detector
#import event
#import imp
#import process_V2





# path to raw lora output
path='/vol/astro5/lofar/vhecr/lora_triggered/LORAraw/'
# path to where root converted to npz file should go
outputdir='/vol/astro7/lofar/kmulrey/LORAsoftware/lora_files/'


parser = OptionParser()
# if i has a value >=0, read filename from index of "event_list.txt"
parser.add_option('-i', '--index',type='int',help='filename_index',default=-1)
parser.add_option('-f', '--file_name',type='str',help='filename',default='20220415_0040')

(options, args) = parser.parse_args()
ind=int(options.index)
file_name=str(options.file_name)


if ind>=0:
    fp = open('event_list.txt','r')
    for i, line in enumerate(fp):
        if i == ind:
            file_name=line.strip()
            break
    fp.close()


#file_name='20200302_0051'
file=outputdir+file_name+'.p'

tfile=path+file_name+'.root'
print(file)
print(tfile)


data={}

outfile = open(tfile,"wb")
pickle.dump(data,outfile)












#  create all holders for raw root data
branches={}
branches['Tree_Event'] =['Station','Detector','Channel_Passed_Threshold','Trigg_Threshold','Charge_Corrected','Peak_Height_Corrected','Peak_Height_Raw','Waveform_Raw','Event_Id','Run_Id','GPS_Time_Stamp','CTD','nsec_Online','HiSparc_Trigg_Pattern','HiSparc_Trigg_Condition']
branches['Tree_Detector_Config'] =['sigma_ovr_thresh','lasa1_is_active','lasa1_version','lasa2_is_active','lasa2_version','lasa3_is_active','lasa3_version','lasa4_is_active','lasa4_version','lasa5_is_active','lasa5_version','lofar_trig_mode','lofar_trig_cond','lora_trig_cond','lora_trig_mode','calibration_mode','log_interval','check_coinc_interval','reset_thresh_interval','init_reset_thresh_interval','coin_window','wvfm_process_offtwlen','wvfm_process_wpost','wvfm_process_wpre','diagnostics_interval','output_save_hour','tbb_dump_wait_min','osm_store_interval']

branches['Tree_Log']=['Station','Detector','Channel_Thres_Low','Mean_Baseline','Mean_Sigma']


branches['Tree_OSM_HiSparc']=['Station','Master_Or_Slave','GPS_Time_Stamp','Sync_Error','Quant_Error','CTP']
branches['Tree_OSM_AERA']=['Station','GPS_Time_Stamp','Sync_Error','Quant_Error','CTP','UTC_offset','trigger_rate']

branches['Tree_Event_Header']=['GPS_Time_Stamp_FirstHit','nsec_Online_FirstHit','Event_Id','Run_Id','LOFAR_Trigg','Event_Tree_Index','Event_Size']

def get_entry(br,key,n):
    br.GetEntry(n)
    if key!='Waveform_Raw':
        return br.GetLeaf(key).GetValue()

    if key=='Waveform_Raw':
        nTrace=4000
        return np.array([br.GetLeaf(key).GetValue(k) for k in range(nTrace)])



# read root data and save .p file
def process_and_save(tfile):
    print (tfile)
    pklfile='new_files/'+ os.path.basename(tfile).split('.root')[0]+'.npz'
    if os.path.exists(pklfile):
        print ("file exits. skip")
        return
    rtfile = ROOT.TFile.Open(tfile)

    data_new={}
    data_new_config={}
    data_new_log={}
    data_new_event={}
    data_new_osm_hisparc={}
    data_new_osm_aera={}

    data_new_header={}

    for tree_name in ['Tree_Event_Header']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_header[branch]=np.array([get_entry(br,branch,i) for i in range(n)])

    for tree_name in ['Tree_Detector_Config']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_config[branch]=np.array([get_entry(br,branch,i) for i in range(n)])

    for tree_name in ['Tree_Log']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_log[branch]=np.array([get_entry(br,branch,i) for i in range(n)])

    for tree_name in ['Tree_Event']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_event[branch]=np.array([get_entry(br,branch,i) for i in range(n)])

    for tree_name in ['Tree_OSM_HiSparc']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_osm_hisparc[branch]=np.array([get_entry(br,branch,i) for i in range(n)])

    for tree_name in ['Tree_OSM_AERA']:
        tree=rtfile.Get(tree_name)
        for branch in branches[tree_name]:
            print (tree_name,branch)
            br= tree.GetBranch(branch)
            n=br.GetEntries()
            data_new_osm_aera[branch]=np.array([get_entry(br,branch,i) for i in range(n)])


    #print (len(data_new['Waveform_Raw']), len(data_new['Charge_Corrected']))

    all_data={'data_config':data_new_config,'data_log':data_new_log,'data_event':data_new_event,'data_osm_hisparc':data_new_osm_hisparc,'data_header':data_new_header,'data_osm_aera':data_new_osm_aera}
