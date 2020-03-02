import glob
import json
import logging
import os
import shutil
import subprocess

if not os.path.exists('/mnt/multiply/data'):
    SUCCESS = 0
    MOUNT_FAILURE = 32
    logging.getLogger().setLevel(logging.INFO)
    disk_mounted = False
    devices = ['/dev/vdb', '/dev/vdb1']
    for device in devices:
        if os.path.exists(device):
            logging.info(f'Device found at {device}, trying to mount ...')
            process = subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mount', '-t', 'ext4', device, '/mnt/multiply/'])
            logging.info(f'Mounting process ended with code {process.returncode}')
            if process.returncode == SUCCESS:
                logging.info(f'Device {device} mounted.')
                disk_mounted = True
                break
            elif process.returncode == MOUNT_FAILURE:
                logging.info(f'Device {device} must be formatted.')
                subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkfs.ext4', device])
                process = subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mount', '-t', 'ext4', device, '/mnt/multiply/'])
                logging.info(f'Mounting process ended with code {process.returncode}')
                if process.returncode == SUCCESS:
                    logging.info(f'Device {device} mounted.')
                    disk_mounted = True
                    break
if not os.path.exists('/data/'):
    logging.info('Creating data folder structure ...')
    subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/data/'])
    subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/data/'])
    subprocess.run(['chmod', '777', '/data/'])
    if disk_mounted:
        # create data folders on mount
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/mnt/multiply/data/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/mnt/multiply/data/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chmod', '777', '/mnt/multiply/data/'])
        os.makedirs('/mnt/multiply/data/archive')
        os.makedirs('/mnt/multiply/data/auxiliary')
        os.makedirs('/mnt/multiply/data/temp')
        os.makedirs('/mnt/multiply/data/working_dirs')
        # create link to data folder
        subprocess.run(['ln', '-s', '/mnt/multiply/data/archive', '/data/archive'])
        subprocess.run(['ln', '-s', '/mnt/multiply/data/auxiliary', '/data/auxiliary'])
        subprocess.run(['ln', '-s', '/mnt/multiply/data/temp', '/data/temp'])
        subprocess.run(['ln', '-s', '/mnt/multiply/data/working_dirs', '/data/working_dirs'])
    else:
        # just create data folders
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/data/archive/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/data/auxiliary/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/data/temp/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'mkdir', '/data/working_dirs/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/data/archive/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/data/auxiliary/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/data/temp/'])
        subprocess.run(['echo', 'multiply', '|', 'sudo', '-S', 'chown', 'ubuntu', '/data/working_dirs/'])
    # place bucket info files in folders
    logging.info('Placing bucket placeholders ...')
    bucket_info_files = glob.glob('./bucket_info_files/*json')
    for path_to_bucket_info_file in bucket_info_files:
        with open(path_to_bucket_info_file, "r") as bucket_info_file:
            bucket_info = json.load(bucket_info_file)
            logging.info(f"Creating directory at {bucket_info['location_on_dias']}")
            os.makedirs(bucket_info['location_on_dias'])
            new_file = os.path.join(bucket_info['location_on_dias'], 'bucket_info.json')
            logging.info(f"Copying bucket info file to {new_file}")
            shutil.copyfile(path_to_bucket_info_file, new_file)
