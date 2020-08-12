#!/usr/bin/env python3

"""
Written by Jangari
https://jangari-ntk.github.io/

GitHub: https://github.com/Jangari-nTK
Twitter: https://twitter.com/Jangari_nTK

Instant Clone with pyVmomi

Note: Sample code For testing purposes only

Example:
GOSC_OPTIONS=$(cat << EOS
{
    "guestinfo.ic.hostname": "instant-cloned-esxi",
    "guestinfo.ic.ipaddress": "10.20.30.1",
    "guestinfo.ic.netmask": "255.255.255.0",
    "guestinfo.ic.gateway": "10.20.30.254",
    "guestinfo.ic.dns": "10.20.30.254",
    "guestinfo.ic.networktype": "static",
    "guestinfo.ic.uuid": "c8b2a455-4da0-41cb-a49d-9e18d3b88d06",
    "guestinfo.ic.uuidHex": "0x55 0xa4 0xb2 0xc8 0xa0 0x4d 0xcb 0x41 0xa4 0x9d 0x9e 0x18 0xd3 0xb8 0x8d 0x6"
}
EOS
)

python3 instant_clone.py --host vcsa01.corp.local --user administrator@vsphere.local \
    --password VMware1! --vm-name "New_VM" --parent-vm "Parent_VM" --datacenter-name "Datacenter" \
    --resource-pool "Destination-Pool" --guestinfo-json-string "$GOSC_OPTIONS"
"""

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from pyVim.task import WaitForTask
import ssl, argparse, getpass, atexit, json

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
                        help='vCenter Server TCP port')

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
                        help='Name of the new VM')

    parser.add_argument('--parent-vm',
                        required=True,
                        action='store',
                        help='Name of the parent VM')

    parser.add_argument('--datacenter-name',
                        required=False,
                        action='store',
                        default=None,
                        help='Name of the destination datacenter. \
                            If omitted, the first datacenter will be used.')

    parser.add_argument('--vm-folder',
                        required=False,
                        action='store',
                        default=None,
                        help='Name of the destination VM Folder. \
                            If omitted, the datacenter VM folder \
                            will be used')

    parser.add_argument('--resource-pool',
                        required=True,
                        action='store',
                        help='Name of the destionation resource pool.')

    parser.add_argument('--guestinfo-json-string',
                        action="store",
                        default=None,
                        help="JSON string of guestinfo variables")

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

def dict_to_optionvalues(guestinfo_vars):
    optionvalues = []
    for k, v in guestinfo_vars.items():
        opt = vim.option.OptionValue()
        (opt.key, opt.value) = (k, v)
        optionvalues.append(opt)

    return optionvalues

def instant_clone_vm(content, parent_vm, vm_name, datacenter_name, vm_folder, resource_pool, optionvalues):

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
    instant_clone_spec.config = optionvalues

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

    if args.guestinfo_json_string is None:
        guestinfo_vars = None
    else:
        guestinfo_vars = dict_to_optionvalues(json.loads(args.guestinfo_json_string))

    if parent_vm:
        instant_clone_vm(content, parent_vm, args.vm_name,
            args.datacenter_name, args.vm_folder, args.resource_pool,
            guestinfo_vars)
    else:
        print("parent_vm not found")
        quit()

if __name__ == '__main__':
    main()