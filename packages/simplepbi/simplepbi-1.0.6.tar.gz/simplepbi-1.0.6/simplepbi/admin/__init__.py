r'''.
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
from datetime import date, timedelta
import io
import pandas as pd

class Admin():
    """Simple library to use the Power BI api and obtain datasets from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request admin API
        Args:
            token: String
                Bearer Token to use the Power Bi Rest API
        """
        self.token = token
    
    def get_datasets(self, filter=None, skip=None, top=None):
        """Returns a list of datasets for the organization..
        ### Parameters
        ----
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasets in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/datasets?"
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip) 
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasets_in_group(self, workspace_id, expand=None, filter=None, skip=None, top=None):
        """Returns a list of datasets from the specified workspace.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, dashboards, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasets in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/datasets?".format(workspace_id)
            if expand != None:
                url = url + "$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if skip != None:
                url = url + "&$skip={}".format(skip)   
            if top != None:
                url = url + "&$top={}".format(top)
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataset_users(self, dataset_id):
        """Returns a list of users that have access to the specified dataset (Preview).
        ### Parameters
        ----
        dataset_id:
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the dataset.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/datasets/{}/users".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasources(self, dataset_id):
        """Returns a list of datasources for the specified dataset.
        ### Parameters
        ----
        dataset_id:
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasources in the dataset.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/datasets/{}/datasources".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataset_to_dataflows_links_in_group(self, workspace_id):
        """Returns a list of upstream dataflows for datasets from the specified workspace.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the upstream dataflows in the dataset from a workspace
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/datasets/upstreamDataflows".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def get_reports(self, filter=None, skip=None, top=None):
        """Returns a list of reports for the organization.
        ### Parameters
        ----
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the reports in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/reports?"
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_reports_in_group(self, workspace_id, filter=None, skip=None, top=None):
        """Returns a list of reports from the specified workspace.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the reports in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/reports?".format(workspace_id)
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip) 
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_reports_users(self, report_id):
        """Returns a list of users that have access to the specified report (Preview).
        ### Parameters
        ----
        report_id:
            The Power Bi Report id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the report.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/reports/{}/users".format(report_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_groups(self, top, expand=None, filter=None, skip=None):
        """Returns a workspace for the organization.
        ### Parameters
        ----
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, dashboards, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the workspaces in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups?$top={}".format(top)
            if expand != None:
                url = url + "&$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if skip != None:
                url = url + "&$skip={}".format(skip)                
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_group(self, group_id, expand=None):
        """Returns a workspace for the organization.
        ### Parameters
        ----
        group_id: str
            The Power Bi Workspace id. You can take it from PBI Service URL
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, dashboards, datasets, dataflows, workbooks
        ### Returns
        ----
        Dict:
            A dictionary containing all the workspaces in the organization.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}".format(group_id)
            if expand != None:
                url = url + "?$expand={}".format(expand)              
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_groups_users(self, group_id):
        """Returns a list of users that have access to the specified workspace. This is a preview API call.
        ### Parameters
        ----
        group_id: str
            The Power Bi Workspace id. You can take it from PBI Service URL.
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/users".format(group_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def restore_deleted_group(self, workspace_id, emailAddress, name=None):
        """Restores a deleted workspace.
        This API call only supports restoring workspaces in the new workspace experience.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Request Body
        ----
        groupUserAccessRight: GroupUserAccessRight
            Access rights user has for the workspace (Permission level: Admin, Contributor, Member, Viewer or None). This is mandatory
        emailAddress: str
            Email address of the user. This is mandatory.
        name: str
            The name of the group to be restored.
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/restore".format(workspace_id)
            body = {
                "emailAddress": emailAddress 
            }
            if name != None:
                body["name"]=name            
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def get_dashboards(self, expand=None, filter=None, skip=None, top=None):
        """Returns a list of dashboards for the organization.
        ### Parameters
        ----
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, dashboards, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. 
        ### Returns
        ----
        Dict:
            A dictionary containing all the dashboards in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dashboards?"
            if expand != None:
                url = url + "$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dashboards_in_group(self, workspace_id, filter=None, skip=None, top=None):
        """Returns a list of dashboards from the specified workspace.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the dashboards in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/dashboards?".format(workspace_id)
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip) 
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dashboards_users(self, dashboard_id):
        """Returns a list of users that have access to the specified dashboard (Preview).
        ### Parameters
        ----
        dashboard_id:
            The Power Bi dashboard id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the dashboard.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dashboards/{}/users".format(dashboard_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
           
    def get_tiles(self, dashboard_id):
        """Returns a list of tiles within the specified dashboard.
        ### Parameters
        ----
        dashboard_id:
            The Power Bi dashboard id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the tiles in the dashboard.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dashboards/{}/tiles".format(dashboard_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
    
    def get_dataflows(self, filter=None, skip=None, top=None):
        """Returns a list of dataflows for the organization.
        ### Parameters
        ----
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the dataflows in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dataflows?"
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataflows_in_group(self, workspace_id, filter=None, skip=None, top=None):
        """Returns a list of dataflows from the specified workspace.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the dataflows in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/dataflows?".format(workspace_id)
            if filter != None:
                url = url + "$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip) 
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataflows_users(self, dataflow_id):
        """Returns a list of users that have access to the specified dataflow (Preview).
        ### Parameters
        ----
        dataflow_id:
            The Power Bi dataflow id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the dataflow.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dataflows/{}/users".format(dataflow_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def get_dataflow_datasources(self, dataflow_id):
        """Returns a list of datasources for the specified dataflow.
        ### Parameters
        ----
        dataflow_id:
            The Power Bi Dataflow id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasources in the dataflow.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dataflows/{}/datasources".format(dataflow_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_upstream_dataflows_in_group(self, workspace_id, dataflow_id):
        """Returns a list of upstream dataflows for the specified dataflow.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        dataflow_id:
            The Power Bi Dataflow id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the dataflows in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/dataflows/{}/upstreamDataflows".format(workspace_id, dataflow_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)    
            
    def export_dataflow(self, dataflow_id):
        """Exports the definition for the specified dataflow to a JSON file.
        ### Parameters
        ----
        dataflow_id:
            The Power Bi Dataflow id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the metadata built in the dataflow.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dataflows/{}/export".format(dataflow_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_apps(self, top):
        """Returns a list of apps for the organization.
        ### Parameters
        ----
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the apps in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/apps?$top={}".format(top)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_apps_users(self, app_id):
        """Returns a list of users that have access to the specified app (Preview).
        ### Parameters
        ----
        app_id:
            The Power Bi app id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the app.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/apps/{}/users".format(app_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_capacities(self, expand=None):
        """Returns a list of capacities for the organization.
        ### Parameters
        ----
        expand: int
            Expands related entities inline
        ### Returns
        ----
        Dict:
            A dictionary containing all the capacities in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/capacities?"
            if expand != None:
                url = url + "$expand={}".format(expand)
            res = requests.get(url, headers={'Content-Type': 'capacitielication/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_capacities_users(self, capacity_id):
        """Returns a list of users that have access to the specified capacitie (Preview).
        ### Parameters
        ----
        capacity_id:
            The Power Bi capacity id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the capacity.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/capacities/{}/users".format(capacity_id)
            res = requests.get(url, headers={'Content-Type': 'capacitielication/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_refreshable_capacity(self, capacity_id, refreshable_id, expand=None):
        """Returns the specified refreshable for the specified capacity that the user has access to.
        Power BI retains a seven-day refresh history for each dataset, up to a maximum of sixty refreshes.
        ### Parameters
        ----
        capacity_id:
            The Power Bi capacity id. You can take it from PBI Service URL
        refreshable_id
            The Power Bi refreshable id in the capacity.
        expand: int
            Expands related entities inline, receives a comma-separated list of data types. Supported: capacities and groups
        ### Returns
        ----
        Dict:
            A dictionary containing all the refreshables in the capacity.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/capacities/{}/refreshables/{}?".format(capacity_id, refreshable_id)
            if expand != None:
                url = url + "$expand={}".format(expand)
            res = requests.get(url, headers={'Content-Type': 'capacitielication/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_refreshables_capacity(self, capacity_id, top, expand=None, filter=None, skip=None):
        """Returns a list of refreshables for the specified capacity that the user has access to.
        Power BI retains a seven-day refresh history for each dataset, up to a maximum of sixty refreshes.
        ### Parameters
        ----
        capacity_id:
            The Power Bi capacitie id. You can take it from PBI Service URL
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, dashboards, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the capacity.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/capacities/{}/refreshables?$top={}".format(capacity_id, top) 
            if expand != None:
                url = url + "&$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if skip != None:
                url = url + "&$skip={}".format(skip) 
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'capacitielication/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
           
    def get_user_artifact_access_preview(self, userGraphId, return_pandas=False):
        '''Returns a list of artifacts that the given user have access to (Preview).
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        
        ### Parameters
        ----
        userGraphId: str uuid
            The graph ID of user
        return_pandas: bool
            Flag to specify if you want to return a dict response or a pandas dataframe of events. By default pandas
        ### Returns
        ----
        If return_pandas = True returns a Pandas dataframe concatenating iterations otherwise it returns a dict of the response
        ### Limitations
        ----
        Maximum 200 requests per hour.
        '''        
        columnas = ['artifactId', 'displayName', 'artifactType', 'accessRight']
        df_total = pd.DataFrame(columns=columnas)
        dict_total = {}
        list_total = []
        url = "https://api.powerbi.com/v1.0/myorg/admin/users/{}/artifactAccess".format(userGraphId)
        headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        ban = True   
        contar = 0    
        try:
            while(ban):        
                res = requests.get(url, headers=headers)
                if return_pandas:
                    js = json.dumps(res.json()["ArtifactAccessEntities"])
                    df = pd.read_json(js)
                    df_total = pd.concat([df_total, df], sort=True, ignore_index=True)
                    print("Building dataframe iteration: ", str(contar))
                else:
                    if res.json()["ArtifactAccessEntities"]:
                        list_total.extend(res.json()["ArtifactAccessEntities"])
                        #append_value(dict_total, "ArtifactAccessEntities", res.json()["ArtifactAccessEntities"])
                        print("Building dict iteration: ", str(contar))
                print(res.status_code)
                contar = contar +1    
                if "continuationUri" not in res.json():
                    ban=False
                else:
                    url = res.json()["continuationUri"]                   
                    print(res.json()["continuationUri"])    
            if return_pandas:
                print(df_total.tail())
                return df_total
            else:
                dict_total = {'ArtifactAccessEntities': list_total }
                return dict_total
        except requests.exceptions.Timeout:
            print("ERROR: The request method has exceeded the Timeout")
        except requests.exceptions.TooManyRedirects:
            print("ERROR: Bad URL try a different one")
        except requests.exceptions.RequestException as e:
            print("Catastrophic error.")
            raise SystemExit(e)
        except Exception as ex:
            print("ERROR: ", ex)
            
    def get_unused_artifacts(self, workspace_id):
        """Returns a list of artifacts from the specified workspace with last used date.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the artifacts in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/unused".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)        
            
    def get_pipelines(self, expand=None, filter=None, skip=None, top=None):
        """Returns a list of pipelines for the organization.
        ### Parameters
        ----
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, pipelines, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the pipelines in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/pipelines?"
            if expand != None:
                url = url + "$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
			
    def get_pipelines_users(self, pipeline_id):
        """Returns a list of users that have access to the specified pipeline (Preview).
        ### Parameters
        ----
        pipeline_id:
            The Power Bi pipeline id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the users in the pipeline.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/pipelines/{}/users".format(pipeline_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)    
        
    def get_imports(self, expand=None, filter=None, skip=None, top=None):
        """Returns a list of imports for the organization.
        ### Parameters
        ----
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, imports, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the imports in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/imports?"
            if expand != None:
                url = url + "$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)
            if top != None:
                url = url + "&$top={}".format(top)
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
    
    def get_refreshables(self, expand=None, filter=None, skip=None, top=None):
        """Returns a list of refreshables for the organization.
        ### Parameters
        ----
        top: int
            Returns only the first n results. This parameter is mandatory and must be in the range of 1-5000.
        expand: string
            Expands related entities inline, receives a comma-separated list of data types. Supported: users, reports, refreshables, datasets, dataflows, workbooks
        filter: string
            Filters the results based on a boolean condition
        skip: int 
            Skips the first n results. Use with top to fetch results beyond the first 5000.
        ### Returns
        ----
        Dict:
            A dictionary containing all the refreshables in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/capacities/refreshables?$top={}".format(top)
            if expand != None:
                url = url + "&$expand={}".format(expand)
            if filter != None:
                url = url + "&$filter={}".format(filter)            
            if skip != None:
                url = url + "&$skip={}".format(skip)  
            res = requests.get(url.replace("?&", "?"), headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def get_encryption_keys(self, expand=None, filter=None, skip=None, top=None):
        """Returns the encryption keys for the tenant.
        ### Parameters
        ----
        ### Returns
        ----
        Dict:
            A dictionary containing all the refreshables in the tenant.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/tenantKeys"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def add_encryption_key_preview(self, activate, isDefault, keyVaultKeyIdentifier, name):
        """Adds an encryption key for Power BI workspaces assigned to a capacity.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        ### Request Body
        ----
        All the keys are requested for the body
        activate: bool
            Indicates to activate any inactivated capacities to use this key for its encryption.
        isDefault: bool
            Whether an encryption key is the default key for the entire tenant. Any newly created capacity inherits the default key.
        keyVaultKeyIdentifier: str
            The URI that uniquely specifies an encryption key in Azure Key Vault.
        name:
            The name of the encryption key        
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/tenantKeys"
            body = {
                "activate": activate, 
                "isDefault": isDefault,
                "keyVaultKeyIdentifier":keyVaultKeyIdentifier,
                "name":name
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def rotate_encryption_key_preview(self, tenantKeyId, keyVaultKeyIdentifier):
        """Adds an encryption key for Power BI workspaces assigned to a capacity.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        tenantKeyId: str uuid
            The tenant key ID
        ### Request Body
        ----        
        keyVaultKeyIdentifier: str
            The URI that uniquely specifies an encryption key in Azure Key Vault.
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/tenantKeys/{}/Default.Rotate".format(tenantKeyId)
            body = {
                "keyVaultKeyIdentifier":keyVaultKeyIdentifier
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
    
    def add_user_to_group(self, workspace_id, groupUserAccessRight, emailAddress, displayName=None, graphId=None, identifier=None, principalType=None):
        """Grants user permissions to the specified workspace.
        This API call only supports updating workspaces in the new workspace experience and adding a user principle.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Request Body
        ----
        groupUserAccessRight: GroupUserAccessRight
            Access rights user has for the workspace (Permission level: Admin, Contributor, Member, Viewer or None). This is mandatory
        emailAddress: str
            Email address of the user. This is mandatory.
        displayName: str
            Display name of the principal
        graphId: str
            Identifier of the principal in Microsoft Graph. Only available for admin APIs
        identifier: str
            Object ID of the principal
        principalType: principalType
            The principal type (App, Group, User or None)
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/users".format(workspace_id)
            body = {
                "groupUserAccessRight": groupUserAccessRight, 
                "emailAddress": emailAddress 
            }
            if displayName != None:
                body["diplayName"]=displayName
            if graphId != None:
                body["graphId"] = graphId
            if identifier != None:
                body["identifier"] = identifier
            if principalType != None:
                body["principalType"] = principalType
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_user_from_group(self, workspace_id, user):
        """Removes user permissions from the specified workspace.
        This API call only supports updating workspaces in the new workspace experience and adding a user principle.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        user: str
            The user principal name (UPN) of the user to remove (usually the user's email).
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/users/{}".format(workspace_id, user)   
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.delete(url, headers=headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_group_preview(self, workspace_id, capacityId=None, dashboards=None, dataflowStorageId=None, dataflows=None, datasets=None, description=None, isOnDedicatedCapacity=None, isReadOnly=None, name=None, pipelineId=None, reports=None, state=None, typee=None, users=None, workbooks=None):    
        """Updates the properties of the specified workspace.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        This API call call only updates workspaces in the new workspace experience. Only the name and description can be updated. The name must be unique inside an organization.
        ### Parameters
        ----
        workspace_id:
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Request Body
        ----
        id: string
            The workspace ID
        capacityId: string
            The capacity ID
        dashboards: str[]
            List of the dashboards ids that belong to the group. Available only for admin API calls.
        dataflowStorageId: string
            The Power BI dataflow storage account ID
        dataflows: str[]
            List of the dataflows ids that belong to the group. Available only for admin API calls.
        datasets: str[]
            List of the datasets ids that belong to the group. Available only for admin API calls.
        description: string
            The group description. Available only for admin API calls.
        isOnDedicatedCapacity: bool
            Is the group on dedicated capacity
        isReadOnly: bool
            Is the group read only
        name: string
            The group name
        pipelineId: string
            The deployment pipeline ID that the workspace is assigned to. Available only for workspaces in the new workspace experience and only for admin API calls.
        reports: str[]
            List of the reports ids that belong to the group. Available only for admin API calls.
        state: string
            The group state. Available only for admin API calls.
        typee: string
            The type of group. Available only for admin API calls.
        users: GroupUser[]
            List of the users that belong to the group, and their access rights. This value will be empty. It will be removed from the payload response in an upcoming release. To retrieve user information on an artifact, please consider using the Get Group User APIs, or the PostWorkspaceInfo API with the getArtifactUser parameter.
        workbooks: str[]
            List of the workbooks ids that belong to the group. Available only for admin API calls.
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/groups/{}".format(workspace_id)
            body = {
                "id": workspace_id
            }
            
            if capacityId != None:
                body["capacityId"]=capacityId
            if dashboards != None:
                body["dashboards"] = dashboards
            if dataflowStorageId != None:
                body["dataflowStorageId"] = dataflowStorageId
            if dataflows != None:
                body["dataflows"] = dataflows
            if datasets != None:
                body["datasets"]=datasets
            if description != None:
                body["description"] = description
            if isOnDedicatedCapacity != None:
                body["isOnDedicatedCapacity"] = isOnDedicatedCapacity
            if isReadOnly != None:
                body["isReadOnly"] = isReadOnly
            if name != None:
                body["name"]=name
            if pipelineId != None:
                body["pipelineId"] = pipelineId
            if reports != None:
                body["reports"] = reports
            if state != None:
                body["state"] = state
            if typee != None:
                body["type"] = typee
            if users != None:
                body["users"] = users
            if workbooks != None:
                body["workbooks"] = workbooks
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.patch(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_user_in_pipeline(self, pipeline_id, identifier, principalType, accessRight):
        """Grants user permissions to a specified deployment pipeline.
        
        ### Parameters
        ----
        pipeline_id:
            The Power Bi Deployment Pipeline id. You can take it from PBI Service URL
        ### Request Body
        ----
        identifier: str
            For Principal type 'User' provide UPN , otherwise provide Object ID of the principal. This is mandatory
        principalType: principalType
            The principal type (App, Group, User or None). This is mandatory.
        accessRight: GroupUserAccessRight
            accessRequired - Access rights a user has for the deployment pipeline. (Permission level: Admin). This is mandatory
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/pipelines/{}/users".format(pipeline_id)
            body = {
                "identifier": identifier ,
                "principalType": principalType ,
                "accessRight": accessRight
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_user_from_pipeline(self, pipeline_id, identifier):
        """Removes user permissions from a specified deployment pipeline.
        
        ### Parameters
        ----
        pipeline_id: str uuid
            The deployment pipeline ID
        identifier: str
            For Principal type 'User' provide UPN , otherwise provide Object ID of the principal
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/pipelines/{}/users/{}".format(pipeline_id, identifier)   
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.delete(url, headers=headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def assign_workspaces_to_capacity_preview(self, tagetCapacityObjectId, workspacesToAssign):
        """Assigns the specified workspaces to the specified Premium capacity.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        ### Request Body
        ----
        capacityMigrationAssignments: Assignment contract for migrating workspaces to premium capacity as tenant admin
        
        targetCapacityObjectId: str
            The premium capacity ID
        workspacesToAssign: str[]
            List of the workspace IDs to be migrated to premium capacity
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/capacities/AssignWorkspaces"
            body ={
                "tagetCapacityObjectId":tagetCapacityObjectId,
                "workspacesToAssign":workspacesToAssign
            }
            body_option2 ={
                "capacityMigrationAssignments":[{
                    "tagetCapacityObjectId":tagetCapacityObjectId,
                    "workspacesToAssign":workspacesToAssign
                }]
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def unassign_workspaces_from_capacity_preview(self, workspacesToAssign):
        """Unassigns the specified workspaces from capacity.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        ### Request Body
        ----        
        workspacesToAssign: str[]
            List of the workspace IDs to be migrated to premium capacity
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/capacities/UnassignWorkspaces"
            body ={
                "workspacesToAssign":workspacesToAssign
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
                                                                                         
    def get_activity_events_preview(self, activity_date=None, return_pandas=False, filter_event=None):
        '''Returns a dict of pandas dataframe of audit activity events for a tenant.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        The continuation token is automtaically used to get all the results in the date.
        ### Parameters
        ----
        activity_date: str "yyyy-mm-dd"
            The Single date to get events from the whole day.
            If the date is not specify it will return yesterday events by default.
        return_pandas: bool
            Flag to specify if you want to return a dict response or a pandas dataframe of events.
        filter_event: query str
            Filters the results based on a boolean condition, using 'Activity', 'UserId', or both properties. Supports only 'eq' and 'and' operators.
            Ej: filter_event = "UserId eq 'ibarrau@ladataweb.com.ar' and Activity eq 'GetRefreshHistory'"
        ### Returns
        ----
        If return_pandas = True returns a Pandas dataframe concatenating iterations otherwise it returns a dict of the response
        ### Limitations
        ----
        Maximum 200 requests per hour.
        '''        
        columnas = ['Activity', 'ActivityId', 'AppId', 'AppName', 'AppReportId',
       'ArtifactId', 'ArtifactKind', 'ArtifactName', 'CapacityId',
       'CapacityName', 'ClientIP', 'ConsumptionMethod', 'CreationTime',
       'DataConnectivityMode', 'DatasetId', 'DatasetName',
       'DistributionMethod', 'FolderAccessRequests', 'FolderDisplayName',
       'FolderObjectId', 'GatewayClusters', 'HasFullReportAttachment', 'Id',
       'ImportDisplayName', 'ImportId', 'ImportSource', 'ImportType',
       'IsSuccess', 'IsTenantAdminApi', 'ItemName', 'LastRefreshTime',
       'ModelsSnapshots', 'ObjectId', 'Operation', 'OrganizationId',
       'RecordType', 'RefreshType', 'ReportId', 'ReportName', 'ReportType',
       'RequestId', 'TableName', 'UserAgent', 'UserId', 'UserKey', 'UserType',
       'WorkSpaceName', 'Workload', 'WorkspaceId']
        df_total = pd.DataFrame(columns=columnas)
        dict_total = {'activityEventEntities': [] }
        list_total = []
        if activity_date == None:
            activity_date = date.today()- timedelta(days=1)
        else:
            activity_date = date(int(activity_date.split("-")[0]),int(activity_date.split("-")[1]),int(activity_date.split("-")[2]))
        start = activity_date.strftime("'%Y-%m-%dT%H:%M:00.000Z'")
        end = activity_date.strftime("'%Y-%m-%dT23:59:59.000Z'")
        url = "https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime={}&endDateTime={}".format(start, end)
        if filter_event != None:
            url = url + "&$filter={}".format(filter_event)
        ban = True   
        contar = 0    
        try:
            print("Getting activity events for date: ", activity_date, "... running iterations...")
            while(ban):
                res = requests.get(url,
                    headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
                    )
                res.raise_for_status()
                if return_pandas:
                    js = json.dumps(res.json()["activityEventEntities"])
                    df = pd.read_json(io.StringIO(js))
                    if not df.empty and not df.isna().all(axis=None):
                        if not df_total.empty:
                            df_total = pd.concat([df_total, df], sort=True, ignore_index=True)
                        else:
                            df_total = df.copy()
                    #print("Building dataframe iteration: ", str(contar))
                else:
                    if res.json()["activityEventEntities"]:                
                        #append_value(dict_total, "activityEventEntities", res.json()["activityEventEntities"][0])
                        list_total.extend(res.json()["activityEventEntities"])
                        #print("Building dict iteration: ", str(contar))
                    
                #print(res.status_code)
                contar = contar +1
                #print(res.json()["continuationUri"])
                
                if res.json()["lastResultSet"] == True or res.json()["continuationUri"] == None:
                    ban=False
                url = res.json()["continuationUri"]
                #print("last result set: ", res.json()["lastResultSet"])
            print("Total iterations: ", contar)
            if return_pandas:
                return df_total
            else:
                dict_total = {'activityEventEntities': list_total }
                return dict_total
        except requests.exceptions.Timeout:
            print("ERROR: The request method has exceeded the Timeout")
        except requests.exceptions.TooManyRedirects:
            print("ERROR: Bad URL try a different one")
        except requests.exceptions.RequestException as e:
            print("Catastrophic error:", e)
            raise SystemExit(e)
        except Exception as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.text)
            
    def get_activity_events_last_28_days_preview(self, filter_event=None):
        '''Returns a pandas dataframe of audit activity events for the last 28 days at the tenant.
        *** THIS can take a several minutes because it loops 28 days and pagination ***
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        The continuation token is automtaically used to get all the results in the last 28 days starting yesterday.
        ### Parameter
        ----
        filter_event: query str
            Filters the results based on a boolean condition, using 'Activity', 'UserId', or both properties. Supports only 'eq' and 'and' operators.
            Ej: filter_event = "UserId eq 'ibarrau@ladataweb.com.ar' and Activity eq 'GetRefreshHistory'"        
        ### Returns
        ----
        Returns a Pandas dataframe concatenating iterations
        ### Limitations
        ----
        Maximum 200 requests per hour.
        '''

        # Getting last 30 days
        today = date.today() - timedelta(days=1)
        last_30_days = []
        for i in range(27):
            last_30_days.append((today - timedelta(days=i)).strftime("%Y-%m-%d"))

        # Creating an empty DataFrame with the structure needed    
        df = pd.DataFrame(['Activity', 'ActivityId', 'AppId', 'AppName', 'AppReportId',
           'ArtifactId', 'ArtifactKind', 'ArtifactName', 'CapacityId',
           'CapacityName', 'ClientIP', 'ConsumptionMethod', 'CreationTime',
           'DataConnectivityMode', 'DatasetId', 'DatasetName',
           'DistributionMethod', 'FolderAccessRequests', 'FolderDisplayName',
           'FolderObjectId', 'GatewayClusters', 'HasFullReportAttachment', 'Id',
           'ImportDisplayName', 'ImportId', 'ImportSource', 'ImportType',
           'IsSuccess', 'IsTenantAdminApi', 'ItemName', 'LastRefreshTime',
           'ModelsSnapshots', 'ObjectId', 'Operation', 'OrganizationId',
           'RecordType', 'RefreshType', 'ReportId', 'ReportName', 'ReportType',
           'RequestId', 'TableName', 'UserAgent', 'UserId', 'UserKey', 'UserType',
           'WorkSpaceName', 'Workload', 'WorkspaceId'])
        # Loop last 30 days appending the result in a single dataframe
        for i in last_30_days:
            if filter_event == None:    
                df_temp = self.get_activity_events_preview(i, return_pandas=True)
            else:
                df_temp = self.get_activity_events_preview(i, return_pandas=True, filter_event=filter_event)
            df = pd.concat([df, df_temp])
        if 0 in df.columns:
            # Drop 0 column of activities auto generated
            df = df.drop(columns=[0])
        # Remove NaN empty values of each type of activities auto generated
        df = df.dropna(subset=['Activity'])
        return df
            
    def get_modified_workspaces_preview(self, excludePersonalWorkspaces=True, modifiedSince=None):
        """Gets a list of workspace IDs in the organization. This is a preview API call.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        excludePersonalWorkspaces: bool
            Whether to exclude personal workspaces
        modifiedSince: str-datetime
            format %Y-%m-%dT%H:%M:00.000Z
            
        ### Returns
        ----
        Dict:
            Returns a list of list that contains groups of maximum 100 workspaces.
        """
        lista_total = []
        contador = 100
        #datetime.strptime("2021-01-01 01:55:19", "%Y-%m-%d %H:%M:%S")
        #modify_date = modifiedSince.strftime("'%Y-%m-%dT%H:%M:00.000Z'")
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/workspaces/modified?excludePersonalWorkspaces={}".format(excludePersonalWorkspaces)
            if modifiedSince != None:
                url = url + "&modifiedSince={}".format(modifiedSince)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res = res.json()
            lista = [res[i]['id'] for i in range(len(res))]
            for item in range(len(lista)):
                if lista[item*100:item*100+100] != []:
                    lista_total.append(lista[item*100:item*100+100])
                else:
                    break
            return lista_total 
        
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        
    def post_workspace_info(self, workspaces, lineage=True, datasourceDetails=True, datasetSchema=True, datasetExpressions=True, getArtifactUsers=True):
        """Initiates a call to receive metadata for the requested list of workspaces. This is a preview API call.
        *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        ### Request Body
        ----        
        workspaces: str[]
            List of the workspace IDs to ask for scan (it can't contain more than 100 workspaces)
        ### Returns
        ----
        Scan id in uuid format. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/admin/workspaces/getInfo?lineage={}&datasourceDetails={}&datasetSchema={}&datasetExpressions={}&getArtifactUsers={}".format(lineage, datasourceDetails, datasetSchema, datasetExpressions, getArtifactUsers)
            body ={
                "workspaces":workspaces
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res.json()["id"]
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)            
            
    def get_scan_status_preview(self, scan_id):
        """Gets the scan status for the specified scan. This is a preview API call.
            *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        scan_id: str uui
            The scan id obtained from posting workspaces info        
        ### Returns
        ----
        str:
            Returns the status of the scan. Succeeded means you are ready to request scans.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanStatus/{}".format(scan_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()["status"]
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)            
            
    def get_scan_result_preview(self, scan_id):
        """Gets the scan result for the specified scan. This is a preview API call.
            *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Parameters
        ----
        scan_id: str uui
            The scan id obtained from posting workspaces info        
        ### Returns
        ----
        str:
            Returns the status of the scan. Succeeded means you are ready to request scans.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanResult/{}".format(scan_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_available_features(self):
        """
        Returns a list of available features for the user.
        ### Returns
        -------
        200 ok. A dict with the features.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/availableFeatures"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)  
            
    def get_orphan_dataflows_preview(self):
        """Returns a list of all dataflows that are not used by a dataset.
            *** THIS REQUEST IS IN PREVIEW IN SIMPLEPBI ***
        ### Limitations
        ----
        It can only be used for organizations with less than 200 workspaces that contains dataflows. The PBI Rest API won't allow more than 200 requests in an hour.
        ### Returns
        ----
        List:
            A list containing all the dataflows without a dataset connected.
        """
        try:
            res_wp = self.get_groups(top=5000, expand="dataflows")
            workspaces = [res_wp["value"][i]["id"] for i in range(len(res_wp["value"])) if res_wp["value"][i]["dataflows"] != []]
            
            if len(workspaces) > 200:            
                return "You can't use this request because you have more than 200 workspaces (limitation)."
        
            #url_df = "https://api.powerbi.com/v1.0/myorg/admin/dataflows"
            #res_df = requests.get(url_df, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            #res_df.raise_for_status()
            res_df = self.get_dataflows()
            dataflows = [res_df["value"][i]["objectId"] for i in range(len(res_df["value"]))]
            
            actives = []
            orphans = []
            
            for wp in workspaces:
                url = "https://api.powerbi.com/v1.0/myorg/admin/groups/{}/datasets/upstreamDataflows".format(wp)
                res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
                if res.text != '' or res.status_code != 200:
                    actives.extend( [res.json()["value"][i]["dataflowObjectId"] for i in range(len(res.json()["value"])) ] )
                
            for df in dataflows:
                if df not in actives:
                    orphans.append(df)
            
            return orphans
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dashboard_subscriptions_preview(self, dashboard_id):
        """Returns a list of subscriptions along with subscribees that the dashboard subscribed to. This is a preview API call.
        ### Parameters
        ----
        dashboard_id: str uui
            The dashboard id
        ### Returns
        ----
        Dict:
            Returns detailed subscriptions of the dashboard.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/dashboards/{}/subscriptions".format(dashboard_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_report_subscriptions_preview(self, report_id):
        """Returns a list of subscriptions along with subscribees that the report subscribed to. This is a preview API call.
        ### Parameters
        ----
        report_id: str uui
            The report id
        ### Returns
        ----
        Dict:
            Returns detailed subscriptions of the report.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/admin/reports/{}/subscriptions".format(report_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_user_subscriptions_preview(self, user_id):
        """Returns a list of subscriptions that the given user has subscribed to (preview).
        ### Parameters
        ----
        user_id: str uui
            The graph ID or UPN of user
        ### Returns
        ----
        Dict:
            Returns  detailed subscriptions of the user.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        ban = True 
        url = "https://api.powerbi.com/v1.0/myorg/admin/users/{}/subscriptions".format(user_id)
        contar = 0
        list_total = []
        dict_total = {'SubscriptionEntities':[]}
        try:
            while(ban):                
                res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
                res.raise_for_status()
                
                if res.json()["SubscriptionEntities"]:
                    list_total.extend(res.json()["SubscriptionEntities"])
                    print("Building dict iteration: ", str(contar))
                    
                contar = contar +1
                print("Pagination: ", str(contar))
                
                if res.json()["continuationUri"] == None or res.json()["SubscriptionEntities"]==[]:
                    ban=False
                url = res.json()["continuationUri"]   
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_widely_shared_artifacts_links_shared_to_whole_organization(self):
        """Returns a list of artifacts shared to the whole organization through links.
        ### Returns
        ----
        Dict:
            Returns artifacts shared to the whole organization.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        ban = True 
        url = "https://api.powerbi.com/v1.0/myorg/admin/widelySharedArtifacts/linksSharedToWholeOrganization"
        contar = 0
        list_total = []
        dict_total = {'ArtifactAccessEntities':[]}
        try:
            while(ban):                
                res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
                res.raise_for_status()
                
                if res.json()["ArtifactAccessEntities"]:
                    list_total.extend(res.json()["ArtifactAccessEntities"])
                    print("Building dict iteration: ", str(contar))
                    
                contar = contar +1
                print("Pagination: ", str(contar))
                
                try:
                    res.json()["continuationUri"]                    
                except Exception as ex:
                    break
                    
                if res.json()["continuationUri"] == None or res.json()["ArtifactAccessEntities"]==[]:
                    ban=False        
                url = res.json()["continuationUri"]   
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_widely_shared_artifacts_published_to_web(self):
        """Returns a list of artifacts shared through published to web.
        ### Returns
        ----
        Dict:
            Returns artifacts published to web.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        ban = True 
        url = "https://api.powerbi.com/v1.0/myorg/admin/widelySharedArtifacts/publishedToWeb"
        contar = 0
        list_total = []
        dict_total = {'ArtifactAccessEntities':[]}
        try:
            while(ban):                
                res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
                res.raise_for_status()
                
                if res.json()["ArtifactAccessEntities"]:
                    list_total.extend(res.json()["ArtifactAccessEntities"])
                    print("Building dict iteration: ", str(contar))
                    
                contar = contar +1
                print("Pagination: ", str(contar))
                
                try:
                    res.json()["continuationUri"]                    
                except Exception as ex:
                    break
                    
                if res.json()["continuationUri"] == None or res.json()["ArtifactAccessEntities"]==[]:
                    ban=False        
                url = res.json()["continuationUri"]   
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_tenant_settings(self):
        """Returns a list of the tenant settings.
        ### Returns
        ----
        Dict:
            Response 200. A dict with tenant settings.
        ### Limitations
        ----
        Maximum 200 requests per hour.
        """
        try:
            url = "https://api.powerbi.com/v1/admin/tenantsettings"                     
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasets_roles_in_groups(self, workspace_id_list):
        """Returns a list of workspaces and datasets with their roles (RLS). It uses Scanner API
        ### Parameters
        ----
        workspace_id_list: uuid str[]
            The Power Bi Workspace id. You can take it from PBI Service URL like ['xxx-xxx-xxx-xxx', 'yyy-yyy-yyy-yyy']
        ### Limitations
        ----
        The list of workspaces can't contain more than 100 workspaces.        
        ### Returns
        ----
        Dict:
            A dictionary containing all the roles in datasets in workspaces.
        """
        lista_workspaces=[]
        lista_datasets=[]
        
        try:
            scan_id = self.post_workspace_info(workspace_id_list, datasetSchema=True)
            ssta = self.get_scan_status_preview(scan_id)
            res = self.get_scan_result_preview(scan_id)
                
            for w in range(len(res['workspaces'])):
                for d in range(len(res['workspaces'][w]['datasets'])):
                    if "roles" in res['workspaces'][w]['datasets'][d].keys():
                        item = [{ 
                            "id": res['workspaces'][w]['datasets'][d]['id'],
                            "name": res['workspaces'][w]['datasets'][d]['name'],
                            "roles": res['workspaces'][w]['datasets'][d]['roles'] 
                            }]
                        lista_datasets.extend(item)
                datasets = [{
                    "id": res['workspaces'][w]['id'],
                    "name": res['workspaces'][w]['name'],
                    "datasets": lista_datasets 
                    }]
                lista_workspaces.extend(datasets)
                lista_datasets=[]
            workspaces = {"workspaces": lista_workspaces}
            
            return workspaces
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataset_roles_in_group(self, workspace_id, dataset_id):
        """Return a list of roles (RLS) at a dataset from a workspace. It uses Scanner API
        ### Parameters
        ----
        workspace_id: uuid 
            The Power Bi Workspace id. You can take it from PBI Service URL
        dataset_id: uuid
            The Power Bi Semantic model id. You can take it from PBI Service URL
        ### Limitations
        ----
        The list of workspaces can't contain more than 100 workspaces.        
        ### Returns
        ----
        Dict:
            A dictionary containing all the roles in datasets in workspaces.
        """
        lista_workspaces=[]
        lista_datasets=[]
        workspace_id_list = [workspace_id]
        
        try:
            scan_id = self.post_workspace_info(workspace_id_list, datasetSchema=True)
            ssta = self.get_scan_status_preview(scan_id)
            res = self.get_scan_result_preview(scan_id)
            
            dataset = [ item for item in res['workspaces'][0]['datasets'] if item['id']==dataset_id ][0]
                
            if "roles" in dataset.keys():
                item = [{ 
                    "id": dataset['id'],
                    "name": dataset['name'],
                    "roles": dataset['roles'] 
                    }]
                lista_datasets.extend(item)
                datasets = [{
                    "id": res['workspaces'][0]['id'],
                    "name": res['workspaces'][0]['name'],
                    "datasets": lista_datasets 
                    }]
                lista_workspaces.extend(datasets)
                lista_datasets=[]
            else:
                lista_workspaces = "The dataset in the workspace doesn't have created roles."
            workspaces = {"workspaces": lista_workspaces}
            
            return workspaces
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)