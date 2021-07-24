
import json
import boto3
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('ec2')
    all_regions = client.describe_regions()
    RegionList = []
    for r in all_regions['Regions']:
        RegionList.append(r['RegionName'])
    print(RegionList)
    runninginstances=[]
    instancetime=[]
    message = ""
    rds_message = ""
    # rdsclient = boto3.client('rds')
    # rds_all_regions = rdsclient.describe_regions()
    # RDS_RegionList = []
    # for r in rds_all_regions['Regions']:
    #     RDS_RegionList.append(r['RegionName'])
    # print(RDS_RegionList)
    client = boto3.client("sns")
    for r in RegionList: 
        rds = boto3.client('rds', region_name = r)
        rdsresponse = rds.describe_db_instances()
        for i in rdsresponse['DBInstances']:
            if i['DBInstanceStatus'] == 'available':
                rds_time = i['InstanceCreateTime']
                current_time = dt.now(rds_time.tzinfo)
                diff =   relativedelta(current_time, rds_time)
                #print(diff)
                print(i['DBInstanceIdentifier'],i['DBInstanceStatus'], diff.days, diff.hours)
                if diff.days == 0:
                        if diff.hours >= 8:
                             rds_message = rds_message + "The RDS Instance with ID " +str(i['DBInstanceIdentifier'])+" is running for "+str(diff.hours)+" hours at region "+str(r)+".\n"
   
            
            
        
    for r in RegionList:  
        ec2 = boto3.client('ec2', region_name = r)
        response = ec2.describe_instances()
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                #print(instance['State']['Name'],instance['LaunchTime'],instance['InstanceId'])
                if instance['State']['Name'] == 'running':
                    #print(instance['InstanceId'])
                    runninginstances.append(instance['InstanceId'])
                    instancetime.append(str(instance['LaunchTime']))
                    launch_time = instance['LaunchTime']
                    current_time = dt.now(launch_time.tzinfo)
                    diff =   relativedelta(current_time, launch_time)
                    #print(launch_time, current_time, diff)
                    if diff.days == 0:
                        if diff.hours >= 8:
                            message = message + "The instance with ID " + str(instance['InstanceId']) + " has been running for " +str(diff.hours)+ " hours at region "+str(r)+".\n"
                            #print(message)
                            #print("should be notified")
    print(runninginstances) 
    print(instancetime)
    print(rds_message)
    print(message)
    response =client.publish(TopicArn = "arn:aws:sns:ap-south-1:079859149351:benjamin-topic",Subject = "AWS Resources Alert",Message=rds_message+message)

    print(response)
   
