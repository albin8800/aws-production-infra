#!/usr/bin/env python3                                                                                                                                                                                                                
"""
AWS Resource Sweeper & Cost Auditor
Scans the configured AWS region for orphaned EBS volumes and unattached Elastic IPs.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
                                                                                                                                                                                                                                      
REGION = "us-east-1"                                                                                                                                                                                                                  
                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                      
def get_ec2_client():                                                                                                                                                                                                                 
    """Initializes and returns the Boto3 EC2 client."""                                                                                                                                                                               
    return boto3.client("ec2", region_name=REGION)                                                                                                                                                                                    
                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                      
def sweep_unattached_volumes(ec2):                                                                                                                                                                                                    
    """Finds EBS storage volumes that are 'available' (not attached to any server)."""                                                                                                                                                
    print(f"\n🔍 [1/2] Scanning for Orphaned Storage Volumes (EBS) in {REGION}...")                                                                                                                                                   
    try:                                                                                                                                                                                                                              
        response = ec2.describe_volumes(                                                                                                                                                                                              
            Filters=[{"Name": "status", "Values": ["available"]}]                                                                                                                                                                     
        )                                                                                                                                                                                                                             
        volumes = response.get("Volumes", [])                                                                                                                                                                                         
                                                                                                                                                                                                                                      
        if not volumes:                                                                                                                                                                                                               
            print("   ✅ No orphaned volumes found. Your storage is clean!")                                                                                                                                                          
            return 0                                                                                                                                                                                                                  
                                                                                                                                                                                                                                      
        print(f"   ⚠️ FOUND {len(volumes)} UNATTACHED VOLUME(S) EATING CREDITS:")                                                                                                                                                     
        for vol in volumes:                                                                                                                                                                                                           
            vol_id = vol["VolumeId"]                                                                                                                                                                                                  
            size_gb = vol["Size"]                                                                                                                                                                                                     
            vol_type = vol["VolumeType"]                                                                                                                                                                                              
            print(f"      - Volume ID: {vol_id} | Size: {size_gb}GB | Type: {vol_type}")                                                                                                                                              
        return len(volumes)                                                                                                                                                                                                           
                                                                                                                                                                                                                                      
    except ClientError as e:                                                                                                                                                                                                          
        print(f"   ❌ AWS API Error: {e}")                                                                                                                                                                                            
        return 0                                                                                                                                                                                                                      
                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                      
def sweep_unattached_ips(ec2):                                                                                                                                                                                                        
    """Finds Elastic IP addresses that are not attached to any running instance."""                                                                                                                                                   
    print(f"\n🔍 [2/2] Scanning for Unattached Elastic IPs in {REGION}...")                                                                                                                                                           
    try:                                                                                                                                                                                                                              
        response = ec2.describe_addresses()                                                                                                                                                                                           
        addresses = response.get("Addresses", [])                                                                                                                                                                                     
                                                                                                                                                                                                                                      
        unattached_ips = [                                                                                                                                                                                                            
            addr for addr in addresses if "InstanceId" not in addr and "NetworkInterfaceId" not in addr                                                                                                                               
        ]                                                                                                                                                                                                                             
                                                                                                                                                                                                                                      
        if not unattached_ips:                                                                                                                                                                                                        
            print("   ✅ No unattached Elastic IPs found. Zero idle IP fees!")                                                                                                                                                        
            return 0                                                                                                                                                                                                                  
                                                                                                                                                                                                                                      
        print(f"   ⚠️ FOUND {len(unattached_ips)} UNATTACHED ELASTIC IP(S) EATING CREDITS:")                                                                                                                                          
        for ip in unattached_ips:                                                                                                                                                                                                     
            alloc_id = ip.get("AllocationId", "N/A")                                                                                                                                                                                  
            public_ip = ip.get("PublicIp", "N/A")                                                                                                                                                                                     
            print(f"      - Allocation ID: {alloc_id} | Public IP: {public_ip}")                                                                                                                                                      
        return len(unattached_ips)                                                                                                                                                                                                    
                                                                                                                                                                                                                                      
    except ClientError as e:                                                                                                                                                                                                          
        print(f"   ❌ AWS API Error: {e}")                                                                                                                                                                                            
        return 0                                                                                                                                                                                                                      
                                                                                                                                                                                                                                      

def main():
    print("=" * 60)
    print("🛡️  AWS PRODUCTION INFRASTRUCTURE COST SWEEPER")                                                                                                                                                                           
    print("=" * 60)

    try:
        ec2 = get_ec2_client()
        total_wasted_volumes = sweep_unattached_volumes(ec2)
        total_wasted_ips = sweep_unattached_ips(ec2)

        print("\n" + "=" * 60)
        if total_wasted_volumes == 0 and total_wasted_ips == 0:
            print("🎉 ACCOUNT STATUS: 100% HEALTHY (No wasted resources detected)")                                                                                                                                                   
        else:
            print("🚨 ACTION REQUIRED: Consider deleting the unattached resources above!")                                                                                                                                            
        print("=" * 60)

    except NoCredentialsError:
        print("❌ Error: AWS credentials not found. Run 'aws configure' first.")                                                                                                                                                      

if __name__ == "__main__":
    main()
