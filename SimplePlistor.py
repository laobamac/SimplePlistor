# Copyright 2024 laobamac
import os
import xml.etree.ElementTree as ET
import argparse
import json
import shutil
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='EFI Config Reader and Generator')
    parser.add_argument('-g', '--generate', metavar='CONFIG_PLIST', help='Generate EFI folder from config.plist')
    parser.add_argument('-r', '--read', metavar='CONFIG_PLIST', help='Read config.plist and output to temp.json')
    return parser.parse_args()

def read_config(config_path):
    if not os.path.exists(config_path):
        print(f"Error: config.plist file not found at {config_path}")
        return None
    return ET.parse(config_path).getroot()

def generate_efi_folder(config_root, output_dir):
    # Copy BOOTx64.efi and OpenCore.efi
    shutil.copy('database/OC/BOOTx64.efi', os.path.join(output_dir, 'BOOT/BOOTx64.efi'))
    shutil.copy('database/OC/OpenCore.efi', os.path.join(output_dir, 'OpenCore.efi'))
    
    # Copy SSDT, Tools, Kexts, Drivers, and Resources
    copy_array(config_root.find('ACPI/Add'), 'SSDT', os.path.join(output_dir, 'ACPI'))
    copy_array(config_root.find('Kernel/Add'), 'Kexts', os.path.join(output_dir, 'Kexts'))
    copy_array(config_root.find('UEFI/Drivers'), 'Drivers', os.path.join(output_dir, 'Drivers'))
    copy_array(config_root.find('Misc/Tools'), 'Tools', os.path.join(output_dir, 'Tools'))
    copy_resources('database/Resources', output_dir)

def copy_array(array_element, folder_name, output_folder):
    if array_element is not None:
        for item in array_element:
            filename = item.find('Path').text
            src_path = os.path.join('database', folder_name, filename)
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, os.path.join(output_folder, filename), dirs_exist_ok=True)
                else:
                    shutil.copy(src_path, os.path.join(output_folder, filename))

def copy_resources(src, output_dir):
    shutil.copytree(src, os.path.join(output_dir, 'Resources'), dirs_exist_ok=True)

def write_to_json(config_root):
    data = {
        'SSDT': [],
        'Kexts': [],
        'Drivers': [],
        'Tools': []
    }
    
    def add_to_data(array_path, data_key):
        array_element = config_root.find(array_path)
        if array_element is not None:
            for item in array_element:
                enabled = item.find('Enabled').text == 'true'
                data[data_key].append({
                    'Path': item.find('Path').text,
                    'Enabled': enabled
                })
    
    add_to_data('ACPI/Add', 'SSDT')
    add_to_data('Kernel/Add', 'Kexts')
    add_to_data('UEFI/Drivers', 'Drivers')
    add_to_data('Misc/Tools', 'Tools')
    
    with open('temp.json', 'w') as f:
        json.dump(data, f, indent=4)

def main():
    args = parse_args()
    if args.generate:
        config_root = read_config(args.generate)
        if config_root is not None:
            output_dir = f"SimplePlistor_{read_oc_version()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_EFI"
            os.makedirs(output_dir, exist_ok=True)
            generate_efi_folder(config_root, output_dir)
            print(f"EFI folder generated at: {output_dir}")
    elif args.read:
        config_root = read_config(args.read)
        if config_root is not None:
            write_to_json(config_root)

def read_oc_version():
    with open('database/ocver.shp', 'r') as f:
        return f.read().strip()

if __name__ == "__main__":
    main()
