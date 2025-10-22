'''.
           @@@@@@@@@@
       @@@@..........@@@@
    @@@         .        @@@
  @@.           .         . @@
 @  .     _     .         .   @
@........| |...................@    *********************************************
@      . | |   _____  .        @
@      . | |  |  __ \ .        @    La Data Web
@      . | |__| |  | |.   ***  @
@........|____| |  | |...*   *.@    Copyright © 2022 Ignacio Barrau
@   .       . | |__| |. *     *@
@   .       . |_____/ . *     *@    *********************************************
@   .       .         . *     *@
@   .       .         . *******@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
'''

import json
import requests
from simplepbi import utils
import pandas as pd

class Pipelines():
    """Simple library to use the Power BI api and obtain pipelines from it. The user must have administrator rights or assign permissions on the pipeline.
    """

    def __init__(self, token):
        """Create a simplePBI object to request pipelines API. The user must have administrator rights or assign permissions on the pipeline.
        *** THIS OBJECT IS IN PREVIEW IN SIMPLEPBI ***
        Args:
            token: String
                Bearer Token to use the Power Bi Rest API
        """
        self.token = token
            
    def get_pipeline(self, pipeline_id):
        """Returns the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Returns
        ----
        Dict:
            A dictionary containing all the pipelines in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}".format(pipeline_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_pipelines(self):
        """Returns a list of deployment pipelines that the user has access to.
        ### Parameters
        ----
        None
        ### Returns
        ----
        Dict:
            A dictionary containing all the pipelines in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_pipeline_operation(self, pipeline_id, operation_id):
        """Returns the details of the specified deploy operation performed on the specified deployment pipeline, including the deployment execution plan.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        operation_id: str uuid
            The operation ID
        ### Returns
        ----
        Dict:
            A dictionary containing an operation of the pipeline in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/operations/{}".format(pipeline_id, operation_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_pipeline_operations(self, pipeline_id):
        """Returns a list of the up-to-20 most recent deploy operations performed on the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Returns
        ----
        Dict:
            A dictionary containing most recent operations of the deploy pipelines in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/operations".format(pipeline_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def get_pipeline_stage_artifacts(self, pipeline_id, stageOrder):
        """Returns the supported items from the workspace assigned to the specified stage of the specified deployment pipeline. To learn about items that aren't supported in deployment pipelines, see Unsupported items.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        stageOrder: int32
            The deployment pipeline stage order. Development (0), Test (1), Production (2).
        ### Returns
        ----
        Dict:
            A dictionary containing items from the workspace assigned to the specified stage of the specified deployment pipeline.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/stages/{}/artifacts".format(pipeline_id, stageOrder)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_pipeline_stages(self, pipeline_id):
        """Returns the stages of the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Returns
        ----
        Dict:
            A dictionary containing stages of a deploy pipeline.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/stages".format(pipeline_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def get_pipeline_users(self, pipeline_id):
        """Returns a list of users that have access to the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Returns
        ----
        Dict:
            A dictionary containing a list of users with access to the deploy pipeline.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/users".format(pipeline_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)            
            
    def assign_workspace_to_pipeline_preview(self, pipeline_id, stageOrder, workspace_id):
        """Assigns the specified workspace to the specified deployment pipeline stage.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        stageOrder: int32
            The deployment pipeline stage order. Development (0), Test (1), Production (2).
        ### Request Body
        ----
        workspace_id: str uuid
            The workspace ID
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        The specified deployment pipeline stage isn't already assigned.
        You must be an admin of the specified workspace.
        The specified workspace isn't assigned to any other deployment pipeline.
        This operation will fail if there's an active deployment operation.        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}/stages/{}/assignWorkspace".format(pipeline_id, stageOrder)
            body ={
                "workspaceId": workspace_id
            }                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
            
    def create_pipeline_preview(self, displayName, description=None):
        """Creates a new deployment pipeline.
        ### Parameters
        ----
        None
        ### Request Body
        ----
        displayName: str uuid
            The display name for the new deployment pipeline
        description: str
            The description for the new deployment pipeline
        ### Returns
        ----
        Response object from requests library. 201 Created OK     
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines"
            body ={
                "displayName": displayName
            }                
            if description != None:
                body["value"]["description"]=description
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_pipeline_preview(self, pipeline_id):
        """Deletes the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Returns
        ----
        Response object from requests library. 200 OK     
        
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}".format(pipeline_id)
            res = requests.delete(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_pipeline_user_preview(self, pipeline_id, identifier):
        """Removes user permissions from the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        identifier: str
            To delete user pipeline permissions, provide the user principal name (UPN) of the user. To delete a service principal or a security group's pipeline permissions, provide the Object ID of the service principal or security group.
        ### Returns
        ----
        Response object from requests library. 200 OK     
        
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/pipelines/{}/users/{}".format(pipeline_id, identifier)
            res = requests.delete(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def unassign_workspace_preview(self, pipeline_id, stageOrder):
        """Unassigns the workspace from the specified stage in the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        stageOrder: int32
            The deployment pipeline stage order. Development (0), Test (1), Production (2).
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}/stages/{}/unassignWorkspace".format(pipeline_id, stageOrder)
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def deploy_all_preview(self, pipeline_id, sourceStageOrder, isBackwardDeployment=None, newWorkspace=None, options=None, updateAppSettings=None):
        """Deploys all supported items from the source stage of the specified deployment pipeline. To learn about items that aren't supported in deployment pipelines, see Unsupported items.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Request Body
        ----
        sourceStageOrder: integer
            The numeric identifier of the pipeline deployment stage that the content should be deployed from. Development (0), Test (1), Production (2).
        isBackwardDeployment: boolean
            Whether the deployment will be from a later stage in the deployment pipeline, to an earlier one. The default value is false.
        newWorkspace: PipelineNewWorkspaceRequest (Read more at Microsoft Docs to learn how to build the dict {})
            The configuration details for creating a new workspace. Required when deploying to a stage that has no assigned workspaces. The deployment will fail if the new workspace configuration details aren't provided when required.
        options: DeploymentOptions (Read more at Microsoft Docs to learn how to build the dict {})
            Options that control the behavior of the entire deployment
        updateAppSettings: PipelineUpdateAppSettings (Read more at Microsoft Docs to learn how to build the dict {})
            Update org app in the target workspace settings
        ### Returns
        ----
        Response object from requests library. 202 Accepted OK     
        ### Limitations
        ----
        Maximum 300 deployed items per request.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}/deployAll".format(pipeline_id)
            body ={
                "sourceStageOrder": sourceStageOrder
            }                
            if isBackwardDeployment != None:
                body["value"]["isBackwardDeployment"]=isBackwardDeployment
            if newWorkspace != None:
                body["value"]["newWorkspace"]=newWorkspace
            if options != None:
                body["value"]["options"]=options
            if updateAppSettings != None:
                body["value"]["updateAppSettings"]=updateAppSettings
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def selective_deploy_preview(self, pipeline_id, sourceStageOrder, dashboards, dataflows, datamarts, datasets, isBackwardDeployment=None, newWorkspace=None, options=None, updateAppSettings=None):
        """Deploys the specified items from the source stage of the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Request Body
        ----
        sourceStageOrder: integer
            The numeric identifier of the pipeline deployment stage that the content should be deployed from. Development (0), Test (1), Production (2).
        dashboards: DeployArtifactRequest[]
            A list of dashboards to be deployed (Read more at Microsoft Docs to learn how to build the list [])
        dataflows: DeployArtifactRequest[]
            A list of dataflows to be deployed (Read more at Microsoft Docs to learn how to build the list [])
        datamarts: DeployArtifactRequest[]
            A list of datamarts to be deployed (Read more at Microsoft Docs to learn how to build the list [])
        datasets: DeployArtifactRequest[]
            A list of datasets to be deployed (Read more at Microsoft Docs to learn how to build the list [])
        isBackwardDeployment: boolean
            Whether the deployment will be from a later stage in the deployment pipeline, to an earlier one. The default value is false.
        newWorkspace: PipelineNewWorkspaceRequest (Read more at Microsoft Docs to learn how to build the dict {})
            The configuration details for creating a new workspace. Required when deploying to a stage that has no assigned workspaces. The deployment will fail if the new workspace configuration details aren't provided when required.
        options: DeploymentOptions (Read more at Microsoft Docs to learn how to build the dict {})
            Options that control the behavior of the entire deployment
        updateAppSettings: PipelineUpdateAppSettings (Read more at Microsoft Docs to learn how to build the dict {})
            Update org app in the target workspace settings
        ### Returns
        ----
        Response object from requests library. 202 Accepted OK     
        ### Limitations
        ----
        Maximum 300 deployed items per request.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}/deploy".format(pipeline_id)
            body ={
                "sourceStageOrder": sourceStageOrder
            }
            if dashboards != None:
                body["value"]["dashboards"]=dashboards
            if dataflows != None:
                body["value"]["dataflows"]=dataflows
            if datamarts != None:
                body["value"]["datamarts"]=datamarts
            if datasets != None:
                body["value"]["datasets"]=datasets
            if isBackwardDeployment != None:
                body["value"]["isBackwardDeployment"]=isBackwardDeployment
            if newWorkspace != None:
                body["value"]["newWorkspace"]=newWorkspace
            if options != None:
                body["value"]["options"]=options
            if updateAppSettings != None:
                body["value"]["updateAppSettings"]=updateAppSettings
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_pipeline_preview(self, pipeline_id, displayName, description=None):
        """Updates the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Request Body
        ----
        displayName: str uuid
            The display name for the new deployment pipeline
        description: str
            The description for the new deployment pipeline
        ### Returns
        ----
        Response object from requests library. 200 OK     
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}".format(pipeline_id)
            body ={
                "displayName": displayName
            }                
            if description != None:
                body["value"]["description"]=description
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.patch(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_pipeline_user_preview(self, pipeline_id, identifier, principalType, accessRight):
        """Updates the specified deployment pipeline.
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        ### Request Body
        ----
        identifier: str
            For principal type User, provide the UPN. Otherwise provide the object ID of the principal.
        principalType: str
            The principal type. E.g { "App", "Group", "None", "User" }
        accessRight: str
            Required. The access right a user has for the deployment pipeline. E.g "Admin"
        ### Returns
        ----
        Response object from requests library. 200 OK     
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/pipelines/{}/users".format(pipeline_id)
            body ={
                "identifier": identifier,
                "accessRight": accessRight,
                "principalType": principalType
            }
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)