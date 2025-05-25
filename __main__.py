import pulumi
import pulumi_azure_native as azure_native
import base64
import time
import random
from pulumi import Config, export, ResourceOptions

# === Helper function for unique naming ===
def get_random_suffix():
    """Generate a random suffix for resource names"""
    random_id = random.randint(10000, 99999)
    return f"{random_id}"

# === Load configuration ===
config = Config()
env = pulumi.get_stack()
appname = pulumi.get_project()

location = config.require("location")
key_vault_name = config.require("key_vault_name")
subscription_id = config.require("subscription_id")
resource_group_name = config.require("resource_group_name")

# Get your SSH public key from config
public_key = config.require("publicKey")

# Resource group - use the provided name as a resource name parameter, not as a keyword arg
resource_group = azure_native.resources.ResourceGroup(
    resource_group_name if resource_group_name else f"rg-{appname}-{env}",
    location=location
)

# Virtual Network
vnet_name = f"vnet-{env}"
vnet = azure_native.network.VirtualNetwork(vnet_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    address_space=azure_native.network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ))

# Network Security Group with rules for SSH (22) and Jenkins (8080)
nsg_name = f"nsg-{env}"
nsg = azure_native.network.NetworkSecurityGroup(nsg_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    security_rules=[
        azure_native.network.SecurityRuleArgs(
            name="Allow-SSH",
            priority=1000,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="*",
            destination_address_prefix="*",
        ),
        azure_native.network.SecurityRuleArgs(
            name="Allow-Jenkins",
            priority=1001,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="8080",
            source_address_prefix="*",
            destination_address_prefix="*",
        ),
        azure_native.network.SecurityRuleArgs(
            name="Allow-OpenShift-API",
            priority=1002,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="6443",
            source_address_prefix="*",
            destination_address_prefix="*",
        )
    ])

#dckr_pat_RWzLCJZThsG7YzEQxbDB2CZ_hVU


#1fa57e4cbe0a4bfd992258296e5d0ead
# Subnet with NSG associated
subnet_name = f"subnet-{env}"
subnet = azure_native.network.Subnet(subnet_name,
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24",
    network_security_group=azure_native.network.SubResourceArgs(
        id=nsg.id
    ))

# Generate a random suffix for all resources that need to be globally unique
unique_suffix = get_random_suffix()

# Public IP for VM - use logical name with unique suffix
public_ip_name = f"publicIp-{env}"  # e.g., publicIp-dev-12345
public_ip = azure_native.network.PublicIPAddress(public_ip_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_allocation_method="Dynamic",
    dns_settings=azure_native.network.PublicIPAddressDnsSettingsArgs(
        domain_name_label=f"{appname}-{env}".lower().replace("_", "-"),
    ))

# Network Interface - use logical name as the resource name
nic_name = f"nic-{env}"  # e.g., nic-dev-12345
nic = azure_native.network.NetworkInterface(nic_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    ip_configurations=[azure_native.network.NetworkInterfaceIPConfigurationArgs(
        name="ipconfig1",
        subnet=azure_native.network.SubnetArgs(id=subnet.id),
        private_ip_allocation_method="Dynamic",
        public_ip_address=azure_native.network.PublicIPAddressArgs(id=public_ip.id),
    )],
    opts=ResourceOptions(
        depends_on=[subnet, public_ip]
    ))

# Cloud-init script to install Jenkins and OpenShift CLI
cloud_init = """#cloud-config
package_update: true
package_upgrade: true
packages:
  - git
  - curl
  - docker.io
  - openjdk-17-jdk

runcmd:
  # Start and enable Docker
  - systemctl start docker
  - systemctl enable docker
 
  # Install Java (required by Jenkins)
  - apt update && apt upgrade -y
  - apt-get install -y openjdk-17-jdk curl gnupg2

  # Add the Jenkins Debian package repository key
  - curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | gpg --dearmor | tee /usr/share/keyrings/jenkins-keyring.gpg > /dev/null

  # Add the Jenkins repository to the system
  - echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.gpg] https://pkg.jenkins.io/debian-stable binary/" | tee /etc/apt/sources.list.d/jenkins.list > /dev/null

  # Update the package list again with the new Jenkins repo
  - apt update

  # Install Jenkins
  - apt install -y jenkins

  # Enable and start Jenkins service
  - systemctl enable jenkins
  - systemctl start jenkins

  # Check Jenkins status
  - systemctl status jenkins

  # Install OpenShift CLI
  - curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz
  - tar -xvf oc.tar.gz
  - mv oc /usr/local/bin/
  - chmod +x /usr/local/bin/oc

  # Add Microsoft's official repository
  - curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

  # Install Azure CLI
  - sudo apt-get update
  - sudo apt-get install -y azure-cli

  # Verify installation
  - az --version


  # Set subscription (replace <subscription-id>)
  az account set --subscription <subscription-id>

  az quota update \
  --resource-name StandardDSv3Family \
  --scope /subscriptions/subscription_id/providers/Microsoft.Compute/locations/centralus \
  --limit '{"value": 36}'

  # Request quota increase
  az quota update \
    --resource-name StandardDasv4Family \
    --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/centralus \
    --limit '{"value": 36}'

 az network vnet create \
  --resource-group python-app \
  --name aro-vnet \
  --address-prefixes 10.0.0.0/22 \
  --location centralus

 az network vnet subnet create \
  --resource-group python-app \
  --vnet-name aro-vnet \
  --name master-subnet \
  --address-prefixes 10.0.0.0/23 \
  --service-endpoints Microsoft.ContainerRegistry \
  --disable-private-link-service-network-policies true

 az network vnet subnet create \
  --resource-group python-app \
  --vnet-name aro-vnet \
  --name worker-subnet \
  --address-prefixes 10.0.2.0/23 \
  --service-endpoints Microsoft.ContainerRegistry \
  --disable-private-link-service-network-policies true

 az role assignment create \
  --assignee 19157807-b148-4e12-a7b5-ba2abeb1a9ed \
  --role Contributor \
  --scope /subscriptions/<subscription_id>/resourceGroups/python-app 


  # Verify resources
az group show --name python-app  --output table
az network vnet show --resource-group python-app  --name aro-vnet --output table
az network vnet subnet list --resource-group python-app --vnet-name aro-vnet --output table
az role assignment list --assignee  --scope /subscriptions/<subscription-id>/resourceGroups/openshift --output table


az aro create \
  --resource-group python-app \
  --name openshift \
  --vnet aro-vnet \
  --master-subnet master-subnet \
  --worker-subnet worker-subnet \
  --master-vm-size Standard_D8s_v3 \
  --worker-vm-size Standard_D4as_v4 \
  --worker-count 3 \
  --location centralus \
  --pull-secret /opt/nginx/pull-secrets.txt


  # GET URL 
  az aro show --resource-group  python-app --name openshift --query consoleProfile.url -o tsv

  az aro list-credentials \
  --resource-group python-app \
  --name openshift

  az aro show --resource-group python-app --name openshift --query consoleProfile.url -o tsv

  az aro list-credentials --resource-group python-app --name openshift

  az aro show --resource-group python-app --name openshift --query apiserverProfile.url -o tsv


  #https://grok.com/chat/13940b48-7a6d-4c12-afe0-7518ecc45b74


  oc create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=username \
  --docker-password=token \
  --docker-email=igeadetokunbo@gmail.com \
  --namespace=jenkins-agents

  
  # Login first then to grant access to openshift

  # Create Jenkins Project on oc
  oc new-project jenkins-agents


  # Create a service account "jenkins-agent"
  oc create sa jenkins-agent -n jenkins-agents


  # Grant permission
  oc policy add-role-to-user edit system:serviceaccount:jenkins-agents:jenkins-agent -n jenkins-agents

  
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-results-pvc
  namespace: jenkins-agents
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 30Gi


  # Optional: reboot to apply kernel updates
  # - reboot
"""

# Encode cloud-init in base64 (Azure expects this)
custom_data = base64.b64encode(cloud_init.encode("utf-8")).decode("utf-8")

# VM - use logical name as the resource name
vm_name = f"vm-{env}"
vm = azure_native.compute.VirtualMachine(vm_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    hardware_profile=azure_native.compute.HardwareProfileArgs(
        vm_size="Standard_D8s_v3"
    ),
    os_profile=azure_native.compute.OSProfileArgs(
        computer_name="myvm",
        admin_username="azureuser",
        linux_configuration=azure_native.compute.LinuxConfigurationArgs(
            disable_password_authentication=True,
            ssh=azure_native.compute.SshConfigurationArgs(
                public_keys=[
                    azure_native.compute.SshPublicKeyArgs(
                        path="/home/azureuser/.ssh/authorized_keys",
                        key_data=public_key,
                    )
                ]
            )
        ),
        custom_data=custom_data,
    ),
    network_profile=azure_native.compute.NetworkProfileArgs(
        network_interfaces=[azure_native.compute.NetworkInterfaceReferenceArgs(
            id=nic.id,
            primary=True
        )]
    ),
    storage_profile=azure_native.compute.StorageProfileArgs(
        image_reference=azure_native.compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="0001-com-ubuntu-server-jammy",  # Ubuntu 22.04 LTS
            sku="22_04-lts",
            version="latest"
        ),
        os_disk=azure_native.compute.OSDiskArgs(
            name=f"osdisk-{env}",  # Add unique suffix here
            caching="ReadWrite",
            managed_disk=azure_native.compute.ManagedDiskParametersArgs(
                storage_account_type="Standard_LRS"
            ),
            create_option="FromImage"
        )
    ),
    opts=ResourceOptions(
        depends_on=[nic],
        # Don't use replace_on_changes for customData since it requires replacing the VM
        # which would create a new OS disk with a different name
        protect=False,
        delete_before_replace=True
    )
)

# Export outputs
export("resource_group_name", resource_group.name)

# Export the public IP address
pulumi.export("public_ip", public_ip.ip_address)

def make_ssh_cmd(ip):
    if ip:
        return f"ssh azureuser@{ip} -i ~/.ssh/azure"
    else:
        return "Public IP not available yet"

pulumi.export("ssh_command", public_ip.ip_address.apply(make_ssh_cmd))

# Create a consistent DNS label
dns_label = f"{appname}-{env}-{unique_suffix}".lower().replace("_", "-")
if len(dns_label) > 63:
    dns_label = dns_label[:58] + f"-{unique_suffix}"  # Truncate and append new suffix

pulumi.export("jenkins_url", public_ip.ip_address.apply(lambda ip: f"http://{ip}:8080"))
# NOTE: To SSH into your VM, ensure port 22 is allowed and the public IP is reachable.
# To access Jenkins, navigate to http://<public_ip>:8080


# extent report - Save reports, PVC or Jenkins workspace 
# HPA config 
# Node Auto scaling 
