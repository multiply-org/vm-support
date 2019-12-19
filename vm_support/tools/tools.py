import os
from multiply_core.util import get_time_from_string
from multiply_data_access import DataAccessComponent
import datetime
import glob
from typing import List, Optional
from vm_support.utils import create_config_file, set_permissions
from vm_support.sym_linker import create_sym_links
from multiply_prior_engine import PriorEngine
import yaml
from multiply_inference_engine import inference_engine


#### data_wrappers(): ####################################
def get_static_data(data_access_component: DataAccessComponent, roi: str, roi_grid: str, start_time: str,
                    stop_time: str, emulation_directory: str, dem_directory: str):
    create_dir(emulation_directory)
    create_dir(dem_directory)

    rg = roi_grid
    if roi_grid is 'none':
        rg = None

    print('Retrieving emulators ...')
    emu_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'ISO_MSI_A_EMU,ISO_MSI_B_EMU', rg)
    set_permissions(emu_urls)
    create_sym_links(emu_urls, emulation_directory)
    print('Retrieving DEM ...')
    dem_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'Aster_DEM', rg)
    set_permissions(dem_urls)
    create_sym_links(dem_urls, dem_directory)
    print('Done retrieving static data')


def get_dynamic_data(data_access_component: DataAccessComponent, roi: str, roi_grid: str, start_time: str,
                     stop_time: str, modis_directory: str, cams_tiff_directory: str, s2_l1c_directory: str):
    create_dir(modis_directory)
    create_dir(cams_tiff_directory)
    create_dir(s2_l1c_directory)

    modis_delta = datetime.timedelta(days=16)
    start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    modis_start = start - modis_delta
    modis_start_time = datetime.datetime.strftime(modis_start, '%Y-%m-%d')
    end = datetime.datetime.strptime(stop_time, '%Y-%m-%d')
    modis_end = end + modis_delta
    modis_end_time = datetime.datetime.strftime(modis_end, '%Y-%m-%d')

    rg = roi_grid
    if roi_grid is 'none':
        rg = None

    print('Retrieving MODIS BRDF descriptors ...')
    modis_urls = data_access_component.get_data_urls(roi, modis_start_time, modis_end_time, 'MCD43A1.006', rg)
    set_permissions(modis_urls)
    create_sym_links(modis_urls, modis_directory)
    print('Retrieving CAMS data ...')
    cams_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'CAMS_TIFF', rg)
    set_permissions(cams_urls)
    create_sym_links(cams_urls, cams_tiff_directory)
    print('Retrieving S2 L1C data ...')
    s2_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'AWS_S2_L1C, S2_L1C', rg)
    set_permissions(s2_urls)
    create_sym_links(s2_urls, s2_l1c_directory)
    print('Done retrieving dynamic data')


#### prior_wrappers():###################################
def get_priors(temp_dir: str, roi: str, start_time: str, end_time: str, time_interval: str, priors_directory: str,
               parameter_list: List[str], user_priors: Optional[dict] = None):
    config_file = create_config_file(temp_dir, roi, start_time, end_time, time_interval, priors_directory,
                                     parameter_list=parameter_list, user_prior_data=user_priors)
    get_priors_from_config_file(start_time, end_time, priors_directory, parameter_list, config_file)


def get_priors_from_config_file(start_time: str, end_time: str, priors_directory: str, parameter_list: List[str],
                                config_file: str):
    time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    create_dir(priors_directory)
    while time <= end_time:
        prior_engine = PriorEngine(config=config_file, datestr=time.strftime('%Y-%m-%d'), variables=parameter_list)
        prior_engine.get_priors()
        time = time + datetime.timedelta(days=1)


def get_priors_old(temp_dir: str, roi: str, start_time: str, end_time: str, time_interval: str, priors_directory: str,
                   parameter_list: List[str]):
    config_file = create_config_file(temp_dir, roi, start_time, end_time, time_interval, priors_directory,
                                     parameter_list)
    time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    create_dir(priors_directory)
    while time <= end_time:
        prior_engine = PriorEngine(config=config_file, datestr=time.strftime('%Y-%m-%d'), variables=parameter_list)
        prior_engine.get_priors()
        time = time + datetime.timedelta(days=1)


##############################################################
def preprocess_s2(s2_l1c_dir: str, modis_dir: str, emus_dir: str, cams_dir: str, dem_dir: str, output_root_dir: str,
               roi: str):
    vrt_dem_file = glob.glob(dem_dir + '/' + '*.vrt')[0]
    processor_dir = '/software/atmospheric_correction/SIAC'
    create_dir(output_root_dir)
    dirs = glob.glob(s2_l1c_dir + "/*")
    for directory in dirs:
        directory_parts = directory.split('/')
        product_name = f"{directory_parts[-1]}-ac"
        print(f'Start pre-processing S2 L1 data from {directory_parts[-2]}')
        output_dir = output_root_dir + '/' + product_name + '/'
        command = "PYTHONPATH=$PYTHONPATH:" + processor_dir + "/util python " + processor_dir + "/SIAC_S2.py -f " \
                  + directory + "/ -m " + modis_dir + " -e " + emus_dir + " -c " + cams_dir + " -d " \
                  + vrt_dem_file + " -o False" + " -a \'" + roi + "\'"
        os.system(command)

        create_dir(output_dir)
        cmd2 = "mv $(find " + directory + '/ -type f) ' + output_dir + '/'
        os.system(cmd2)

        cmd3 = "cp `readlink " + directory + "/metadata.xml` " + output_dir + "/metadata.xml"
        os.system(cmd3)
        cmd3 = "cp `readlink " + directory + "/MTD_MSIL1C.xml` " + output_dir + "/MTD_MSIL1C.xml"
        os.system(cmd3)
        paths_to_mtd_tl = glob.glob(os.path.join(directory, 'GRANULE/*/MTD_TL.xml'))
        if len(paths_to_mtd_tl) > 0:
            cmd3 = "cp `readlink " + paths_to_mtd_tl[0] + "` " + output_dir + "/MTD_TL.xml"
        os.system(cmd3)
        print(f'Finished pre-processing S2 L1 data from {directory_parts[-2]}')


def preprocess(s2_l1c_dir: str, modis_dir: str, emus_dir: str, cams_dir: str, dem_dir: str, output_root_dir: str,
               roi: str):
    vrt_dem_file = glob.glob(dem_dir + '/' + '*.vrt')[0]
    processor_dir = '/software/atmospheric_correction_2.0.9/SIAC'
    create_dir(output_root_dir)
    dirs = glob.glob(s2_l1c_dir + "/*/*/*/*/*/*/*")
    for dir in dirs:
        input_dir = dir[len(s2_l1c_dir) + 1:]
        input_parts = input_dir.split('/')
        product_name = "S2-" + input_parts[-7] + input_parts[-6] + input_parts[-5] + input_parts[-4] + "-" + \
                       input_parts[-3] + "-" + input_parts[-2]
        print('Start pre-processing S2 L1 data from {1}-{2}-{0}'.format(input_parts[-4], input_parts[-3],
                                                                        input_parts[-2]))
        output_dir = output_root_dir + '/' + product_name + '/'
        command = "PYTHONPATH=$PYTHONPATH:" + processor_dir + "/util python " + processor_dir + "/SIAC_S2.py -f " \
                  + s2_l1c_dir + '/' + input_dir + "/ -m " + modis_dir + " -e " + emus_dir + " -c " + cams_dir + " -d " \
                  + vrt_dem_file + " -o False" + " -a \'" + roi + "\'"
        os.system(command)

        create_dir(output_dir)
        cmd2 = "mv $(find " + s2_l1c_dir + '/' + input_dir + '/ -type f) ' + output_dir + '/'
        os.system(cmd2)

        cmd3 = "cp `readlink " + s2_l1c_dir + '/' + input_dir + "/metadata.xml` " + output_dir + "/metadata.xml"
        os.system(cmd3)

        print('Finished pre-processing S2 L1 data from {1}-{2}-{0}'.format(input_parts[-4], input_parts[-3],
                                                                           input_parts[-2]))


##### auxiliary():###############################################
def create_dir(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except:
        print(dir)
    return


def put_data(data_access_component: DataAccessComponent, sdrs_directory: str):
    for sdr in os.listdir(sdrs_directory):
        data_access_component.put(sdrs_directory + '/' + sdr, 'S2L2')
    return


def InvTransformation(varname, data):
    if varname == 'cab':
        data = -100. * np.log(data);
    elif varname == 'car':
        data = -100. * np.log(data);
    elif varname == 'cw':
        data = (-1. / 50.) * np.log(data);
    elif varname == 'cdm':
        data = (-1. / 100.) * np.log(data);
    elif varname == 'lai':
        data = -2. * np.log(data);
    elif varname == 'ala':
        data = 90. * data;
    return data


def infer(roi: str, start_date: str, end_date: str, previous_state: str, priors_directory: str, sdrs_directory: str,
          next_state: str, biophys_dir: str, parameter_list: List[str], state_mask: Optional[str],
          spatial_resolution: Optional[int], roi_grid: Optional[str], destination_grid: Optional[str]):
    processor_dir = '/software/inference-engine-0.4/multiply_inference_engine'
    s2_emulators_dir = '/data/archive/emulators/s2_prosail'
    inference_type = 'high'

    create_dir(next_state)
    create_dir(biophys_dir)
    print('Start Inference of S2 data')
    cmd = "python " + processor_dir + "/inference_engine.py -s " + start_date + " -e " + end_date \
          + " -i " + inference_type + " -em " + s2_emulators_dir + " -p " + ','.join(parameter_list) \
          + ((" -ps " + previous_state) if previous_state != 'none' else "") + " -pd " + priors_directory \
          + " -d " + sdrs_directory + " -o " + biophys_dir \
          + ((" -sm " + state_mask) if state_mask != 'none' else "") \
          + " -res " + str(spatial_resolution) + " -ns " + next_state \
          + " -roi \'" + roi + "\'" + ((" -rg " + roi_grid) if roi_grid != 'none' else "") \
          + ((" -dg " + destination_grid) if destination_grid != 'none' else "")
    #     !{cmd}
    os.system(cmd)
    print('Finished Inference of S2 data')


def infer3(roi: str, start_date: str, end_date: str, previous_state: str, priors_directory: str, sdrs_directory: str,
           next_state: str, biophys_dir: str, parameter_list: List[str], state_mask: Optional[str],
           spatial_resolution: Optional[int], roi_grid: Optional[str], destination_grid: Optional[str]):
    processor_dir = '/software/inference-engine-0.4/multiply_inference_engine'
    s2_emulators_dir = '/data/archive/emulators/s2_prosail'
    inference_type = 'high'

    create_dir(next_state)
    create_dir(biophys_dir)

    print('Start Inference of S2 data')

    inference_engine.infer(start_date, end_date, previous_state, parameter_list, priors_directory, sdrs_directory, \
                           previous_state, next_state, s2_emulators_dir, biophys_dir, state_mask, roi,
                           spatial_resolution, \
                           roi_grid, destination_grid, False)

    print('Finished Inference of S2 data')

    infer(start_date,
          end_date,
          parameter_list,
          priors_directory,
          datasets_dir,
          previous_state,
          next_state,
          forward_models,
          biophys_dir,
          state_mask,
          roi,
          spatial_resolution,
          roi_grid,
          destination_grid,
          False)


def infer_new(config_file: str, start_date: str, end_date: str, previous_state: str, priors_directory: str,
              sdrs_directory: str,
              next_state: str, biophys_dir: str, variables: List[str], state_mask: Optional[str],
              spatial_resolution: Optional[int], roi_grid: Optional[str], destination_grid: Optional[str]):
    s2_emulators_dir = '/data/auxiliary/models/s2_prosail'

    # setup parameters
    with open(config_file) as f:
        parameters = yaml.load(f)

    roi = parameters['General']['roi']
    ###############################################################
    # not implemented yet in the 'python notebook configuraiton files, therefore defined as input
    # spatial_resolution = parameters['General']['spatial_resolution'] # in m
    ###############################################################

    ###############################################################
    # Additional Parameters
    forward_model_list = ['s2_prosail']
    inference_type = 'high'
    ###############################################################
    parameter_list = variables

    if not os.path.exists(next_state):
        os.makedirs(next_state)
    if not os.path.exists(biophys_dir):
        os.makedirs(biophys_dir)

    inference_engine.infer(start_time=start_date,
                           end_time=end_date,
                           parameter_list=parameter_list,
                           prior_directory=priors_directory,
                           datasets_dir=sdrs_directory,
                           previous_state_dir=previous_state,
                           next_state_dir=next_state,
                           emulators_directory=s2_emulators_dir,
                           forward_models=forward_model_list,
                           output_directory=biophys_dir,
                           state_mask=state_mask,
                           roi=roi,
                           spatial_resolution=spatial_resolution,
                           roi_grid=roi_grid,
                           destination_grid=destination_grid,
                           with_profiling=False)
    print('Finished Inference of S2 data')


import gdal
import numpy as np
import matplotlib.pyplot as plt


#### visualize(): #####################################################
def Plot_SRDS(sdrs_directory, prodnr=0):
    try:
        band_of_interest = '*sur'
        subdir = glob.glob(sdrs_directory + '/*')[0]
        subdir = glob.glob(subdir + '/*')[prodnr]
        data_files = set(glob.glob(subdir + '/' + band_of_interest + '*')) - \
                     set(glob.glob(subdir + '/' + band_of_interest + '*unc*'))
        Nc = 4
        Nr = len(data_files) / Nc + 1
        plt.figure(figsize=[20, 10])
        avg = []
        for i in range(12):
            bandnr = 'B%02.0f*' % (i + 1)
            data_file = set(glob.glob(subdir + '/' + '*' + bandnr + band_of_interest + '*')) - \
                        set(glob.glob(subdir + '/' + '*' + bandnr + band_of_interest + '*unc*'))
            data_file = list(data_file)[0]
            data_set = gdal.Open(data_file)
            data = data_set.ReadAsArray(0) * 0.01
            data[data < 0] = np.NaN
            plt.subplot(Nc, Nr, (i + 1))
            plt.imshow(data, cmap='Greys', vmin=0)
            avg.append(np.nanmean(data))
            plt.colorbar()
            plt.savefig('Surface Reflectance.png')
    except:
        print('No observations were found')


import gdal
import numpy as np
import matplotlib.pyplot as plt


def Plot_PRIORS(roi_centroid, priors_directory_for_date, variables, iband=1):
    # doystr = '125_*'
    tilestr_lat = '[%02.0f' % (np.floor(roi_centroid[1] / 10.) * 10.)
    tilestr_lon = '%03.0f' % (np.floor(roi_centroid[0] / 10.) * 10.)
    tilestr = tilestr_lat + '*_[' + tilestr_lon + '*'

    Nc = 3
    Nr = len(variables) / Nc + 1
    plt.figure(figsize=[20, 10])
    for i, varname in enumerate(variables):
        data = 0
        try:
            data_file = glob.glob(priors_directory_for_date + '/../user/Priors/*' + varname + '*.tiff')[0]
            data_set = gdal.Open(data_file)
            data = data_set.GetRasterBand(iband).ReadAsArray()[::100, ::100]
            source = 'UserDef'

        except:
            try:
                data_file = glob.glob('/data/auxiliary/priors/Static/Vegetation/Priors/*' + varname + '*' + tilestr)[0]
                data_set = gdal.Open(data_file)
                data = data_set.GetRasterBand(iband).ReadAsArray()[::100, ::100]
                source = 'DefaultDatabase'

            except:
                source = 'Not showing'

        try:
            plt.subplot(Nc, Nr, (i + 1))
            plt.title(source + ' (Transf)-' + varname)
            plt.imshow(data, cmap='Greys')

            plt.colorbar()
        except:
            source = 'Not showing'


def Plot_TRAITS(biophys_output, date: str, variables_subset):
    # plot the variables,
    Nc = 2
    Nr = len(variables_subset) / Nc + 1
    plt.figure(figsize=[20, 20])
    date = get_time_from_string(date)
    for i, variable_of_interest in enumerate(variables_subset):
        file_name = "%s_%s.tif" % (variable_of_interest, date.strftime("A%Y%j"))
        unc_file_name = "%s_%s_unc.tif" % (variable_of_interest, date.strftime("A%Y%j"))
        data_file = set(glob.glob(biophys_output + '/' + file_name)) - \
                    set(glob.glob(biophys_output + '/' + unc_file_name))
        # read data
        data = -99
        for filename in data_file:
            data_set = gdal.Open(filename)
            data = data_set.ReadAsArray(0)

        # post process data
        data = InvTransformation(variable_of_interest, data)
        data[data < 1e-5] = np.NaN
        data[data > 1e9] = np.NaN

        # plot data
        plt.subplot(Nr, Nc, i + 1)
        plt.imshow(data)
        plt.colorbar()
        plt.title(variable_of_interest + ' [%2.2e' % np.nanmean(data) + ' - %2.2e]' % np.nanstd(data))
    plt.savefig('Traits-retrieved.png')


def Plot_Transformation(Data, Data_t):
    plt.figure(figsize=[20, 10])
    plt.subplot(1, 2, 1)
    plt.imshow(Data[0], vmin=0)
    plt.title('Transformed')
    plt.colorbar(orientation="horizontal")

    plt.subplot(1, 2, 2)
    plt.imshow(Data_t[0], vmin=0)
    plt.colorbar(orientation="horizontal")
    plt.title('Real')
    plt.savefig('Effect of the Transformation.png')


def Plot_TRAIT_evolution(Data_t, variable_of_interest):
    Nc = 4
    Nr = int(np.ceil(Nc / len(Data_t))) + 1

    plt.figure(figsize=[20, len(Data_t) * Nr])
    for i in range(len(Data_t)):
        plt.subplot(Nr, Nc, i + 1)
        plt.imshow(Data_t[i], vmin=0, vmax=np.nanmax(np.array(Data_t)))
        plt.title(variable_of_interest)
        plt.colorbar(orientation='horizontal', fraction=.1)
    plt.savefig('Temporal Evolution of Retrieved ' + variable_of_interest + '.png')
