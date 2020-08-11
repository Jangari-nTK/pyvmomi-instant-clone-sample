# pyVmomi Instant Clone sample code

This repository offers an example code for Instant Clone using pyVmomi.

2020-08-12:
Added a parameter (--guestinfo-json-string) for guestinfo variables for user defined script. I tested with a Nested ESXi 7.0 and [the GOSC script authored by @lamw](https://github.com/lamw/instantclone-community-customization-scripts/blob/master/esxi65-67/customize.sh).

# References

- [Leveraging Instant Clone in vSphere 6.7 for extremely fast Nested ESXi provisioning](https://www.virtuallyghetto.com/2018/05/leveraging-instant-clone-in-vsphere-6-7-for-extremely-fast-nested-esxi-provisioning.html)
- [vSphere Web Services API - VMware API Explorer - VMware {code}](https://code.vmware.com/apis/968/vsphere)
- [vmware/pyvmomi: VMware vSphere API Python Bindings](https://github.com/vmware/pyvmomi)
- [vmware/pyvmomi-community-samples: A place for community contributed samples for the pyVmomi library.](https://github.com/vmware/pyvmomi-community-samples)
- [pyvmomi-community-samples/clone_vm.py at master · vmware/pyvmomi-community-samples](https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/clone_vm.py)
- [instantclone-community-customization-scripts/customize.sh at master · lamw/instantclone-community-customization-scripts](https://github.com/lamw/instantclone-community-customization-scripts/blob/master/esxi65-67/customize.sh)