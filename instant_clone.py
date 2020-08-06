#!/usr/bin/env python3

"""
Written by Jangari
https://jangari-ntk.github.io/

GitHub: https://github.com/Jangari-nTK
Twitter: https://twitter.com/Jangari_nTK

Instant Clone with pyVmomi

Example:
$ python3 instant_clone.py --host vcsa01a.corp.local --user administrator@vsphere.local \
    --password VMware1! --vm-name "New_VM" --parent-vm "Parent_VM" --resource-pool "Destination-Pool"

Note: Sample code For testing purposes only
"""

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from pyVim.task import WaitForTask
import ssl, argparse, getpass, atexit

def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for talking to vCenter')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vCenter Server FQDN or IP address')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='Username to login to vCenter Server')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to login to vCenter Server')

    parser.add_argument('-v', '--vm-name',
                        required=True,
                        action='store',
                        help='Name of the VM you wish to make')

    parser.add_argument('--parent-vm',
                        required=True,
                        action='store',
                        help='Name of the parent VM \
                            you are cloning from')

    parser.add_argument('--datacenter-name',
                        required=False,
                        action='store',
                        default=None,
                        help='Name of the Datacenter you\
                            wish to use. If omitted, the first\
                            datacenter will be used.')

    parser.add_argument('--vm-folder',
                        required=False,
                        action='store',
                        default=None,
                        help='Name of the VMFolder you wish\
                            the VM to be dumped in. If left blank\
                            The datacenter VM folder will be used')

    parser.add_argument('--resource-pool',
                        required=True,
                        action='store',
                        help='Resource Pool to use.')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(prompt='Enter password:')

    return args

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)

    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    
    return obj

def instant_clone_vm(content, parent_vm, vm_name, datacenter_name, vm_folder, resource_pool):

    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    if vm_folder:
        dst_folder = get_obj(content, [vim.Folder], vm_folder)
    else:
        dst_folder = datacenter.vmFolder

    resource_pool = get_obj(content, [vim.ResourcePool], resource_pool)

    vm_relocate_spec = vim.vm.RelocateSpec()
    vm_relocate_spec.folder = dst_folder
    vm_relocate_spec.pool = resource_pool

    instant_clone_spec = vim.vm.InstantCloneSpec()
    instant_clone_spec.name = vm_name
    instant_clone_spec.location = vm_relocate_spec

    WaitForTask(parent_vm.InstantClone_Task(spec=instant_clone_spec))

def main():
    args = get_args()

    context = None
    if hasattr(ssl, "_create_unverified_context"):
        context = ssl._create_unverified_context()

    si = SmartConnect(
                    host=args.host,
                    user=args.user,
                    pwd=args.password,
                    port=args.port,
                    sslContext=context)

    atexit.register(Disconnect, si)
    content = si.content

    parent_vm = get_obj(content, [vim.VirtualMachine], args.parent_vm)

    if parent_vm:
        instant_clone_vm(content, parent_vm, args.vm_name,
            args.datacenter_name, args.vm_folder, args.resource_pool)
    else:
        print("parent_vm not found")
        quit()

if __name__ == '__main__':
    main()