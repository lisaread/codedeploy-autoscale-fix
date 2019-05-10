import boto3
import json
import time
import sys
from botocore.exceptions import ClientError

asObj = boto3.client('autoscaling')
codedeployObj = boto3.client('codedeploy')

PROCESSES_TO_SUSPEND = [ 'AZRebalance' , 'ReplaceUnhealthy' , 'ScheduledActions' , 'AlarmNotification' ]

# check deployment group and app exist
def codedeploy_check(MY_APP, MY_DG):
  try:
    codedeploy_app = codedeployObj.get_deployment_group(applicationName = MY_APP, deploymentGroupName = MY_DG )
  except ClientError as e:
    if e.response['Error']['Code'] == 'ApplicationDoesNotExistException':
      sys.exit("The Application does not exist")
    elif e.response['Error']['Code'] == 'DeploymentGroupDoesNotExistException':
      sys.exit("The Deployment Group does not exist")
  else:
    return codedeploy_app

#check if deployment group has asgs and append them to a list
def ASG(codedeploy):
  autoscaling_groups = []
  try:
    for i in codedeploy['deploymentGroupInfo']['autoScalingGroups']:
      autoscaling_groups.append(i['name'])
  except IndexError as err:
    sys.exit("The Deployment Group does not have a ASG")
  else:
    return autoscaling_groups

# check if procs are suspended
#tosuspendornottosuspend = boolean supply True for suspend & False for resume
def suspend_processes(asg, tosuspendornottosuspend):
  try:
    asg_d = asObj.describe_auto_scaling_groups( AutoScalingGroupNames = asg )

    for i in range(len(asg_d['AutoScalingGroups'])):
      if tosuspendornottosuspend == True:
        asObj.suspend_processes(AutoScalingGroupName = asg[i], ScalingProcesses = PROCESSES_TO_SUSPEND)
        print("Auto Scaling processes suspended for Auto Scaling Groups, %s") % asg[i]
      else:
        asObj.resume_processes(AutoScalingGroupName = asg[i], ScalingProcesses = PROCESSES_TO_SUSPEND)
        print("Auto Scaling processes resumed for Auto Scaling Groups, %s ") %asg[i]
 
  except IndexError as err:
    print("there are no procs suspended")

def lambda_handler(event, context):
  MY_APP = event['detail']['application']
  MY_DG = event['detail']['deploymentGroup']
  Deployment = event['detail']['deploymentId']
  status = event['detail']['state']
  print("State change for deployment id %s") % Deployment
  print("Deployment entered state %s") % status
  print("Deployment Group is  %s and Application is  %s") % (MY_DG, MY_APP)
  asg_list = ASG(codedeploy_check(MY_APP, MY_DG))
  if status == 'START'
    suspend_processes(asg_list, True)
  else:
    suspend_processes(asg_list, False)
