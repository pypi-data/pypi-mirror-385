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
import io
import os
import base64
from simplepbi import utils
import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder

class Imports():
    """Simple library to use the Power BI api and obtain imports from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request imports API
        Args:
            token: String
                Bearer Token to use the Power Bi Rest API
        """
        self.token = token
    
    def get_import(self, import_id):
        """Returns the specified import from My workspace.
        ### Parameters
        ----
        import_id: str uuid
            The Power Bi import id. 
        ### Returns
        ----
        Dict:
            A dictionary containing a import in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports/{}".format(import_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_import_in_group(self, workspace_id, import_id):
        """Returns the specified import from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        import_id: str uuid
            The Power Bi import id.
        ### Returns
        ----
        Dict:
            A dictionary containing a import in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports/{}".format(workspace_id, import_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_imports(self):
        """Returns a list of imports from My workspace.
        ### Parameters
        ----
        None
        ### Returns
        ----
        Dict:
            A dictionary containing all the imports in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_imports_in_group(self, workspace_id):
        """Returns a list of imports from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the imports in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def simple_import_pbix(self, filePath, datasetDisplayName, nameConflict="CreateOrOverwrite", overrideModelLabel=None, overrideReportLabel=None):
        """Creates new content in My Workspace. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        datasetDisplayName: str 
            The display name of the dataset should include file extension
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath: str
            Full local path like "C:/Users/SimplePBI/Documents/Filename.pbix"
        fileUrl
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports?datasetDisplayName={}".format(datasetDisplayName)
            if nameConflict != None:
                url = url + "&nameConflict={}".format(str(nameConflict))
            if overrideModelLabel != None:
                url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
            if overrideReportLabel != None:
                url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
            # you need this dictionary to convert a binary file into form-data format
            # None here means we skip the filename and file content is important 
            files = {'value': (None, open(filePath, 'rb'), 'multipart/form-data')}
            # The MultipartEncoder is posted as data, don't use files=...!
            mp_encoder = MultipartEncoder(fields=files)
            # The MultipartEncoder provides the content-type header with the boundary:
            headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = mp_encoder, headers=headers)
            res.raise_for_status()
            
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def simple_import_pbix_in_group(self, workspace_id, filePath, datasetDisplayName, nameConflict="CreateOrOverwrite", overrideModelLabel=None, overrideReportLabel=None):
        """Creates new content in the specified workspace. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        datasetDisplayName: str 
            The display name of the dataset should include file extension
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath: str
            Full local path like "C:/Users/SimplePBI/Documents/Filename.pbix"
        fileUrl
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}".format(workspace_id, datasetDisplayName)
            if nameConflict != None:
                url = url + "&nameConflict={}".format(str(nameConflict))
            if overrideModelLabel != None:
                url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
            if overrideReportLabel != None:
                url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
            # you need this dictionary to convert a binary file into form-data format
            # None here means we skip the filename and file content is important 
            files = {'value': (None, open(filePath, 'rb'), 'multipart/form-data')}
            # The MultipartEncoder is posted as data, don't use files=...!
            mp_encoder = MultipartEncoder(fields=files)
            # The MultipartEncoder provides the content-type header with the boundary:
            headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = mp_encoder, headers=headers)
            res.raise_for_status()
            
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def simple_import_pbix_as_parameter(self, workspace_id, fileContent, datasetDisplayName, nameConflict="CreateOrOverwrite", overrideModelLabel=None, overrideReportLabel=None):
        """Creates new content in the specified workspace from a Pbix added by parameter. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        datasetDisplayName: str 
            The display name of the dataset should include file extension
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        fileContent: str
            Pbix file as Response.Content from requests library. If you print the content it might end with something like this format: "x03\x00\x00I.\x10\x00\x00\x00"
        fileUrl
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}".format(workspace_id, datasetDisplayName)
            if nameConflict != None:
                url = url + "&nameConflict={}".format(str(nameConflict))
            if overrideModelLabel != None:
                url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
            if overrideReportLabel != None:
                url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
            # Convert Response.Content file to the correct format
            nube = io.BytesIO(fileContent)
            # you need this dictionary to convert a binary file into form-data format
            # None here means we skip the filename and file content is important 
            files = {'value': (None, nube, 'multipart/form-data')}
            # The MultipartEncoder is posted as data, don't use files=...!
            mp_encoder = MultipartEncoder(fields=files)
            # The MultipartEncoder provides the content-type header with the boundary:
            headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = mp_encoder, headers=headers)
            res.raise_for_status()            
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def simple_import_pbix_folder_preview(self, folderPath, nameConflict=None, overrideModelLabel=None, overrideReportLabel=None):
        """Creates new multiple contents in the specified workspace. Define a local folder with pbix files. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        datasetDisplayName: str 
            The display name of the dataset should include file extension            
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath: str
            Full local path of the files like "C:/Users/SimplePBI/Documents/"
        fileUrl: str
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        results = []
        try:
            allFiles= [files for root, dirs, files in os.walk(folderPath)][0]
            pbixFiles = [name for name in allFiles if name.endswith(("pbix"))]
            for datasetDisplayName in pbixFiles:
                url = "https://api.powerbi.com/v1.0/myorg/imports?datasetDisplayName={}".format(datasetDisplayName)
                if nameConflict != None:
                    url = url + "&nameConflict={}".format(str(nameConflict))
                if overrideModelLabel != None:
                    url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
                if overrideReportLabel != None:
                    url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
                # you need this dictionary to convert a binary file into form-data format
                # None here means we skip the filename and file content is important 
                files = {'value': (None, open(folderPath+datasetDisplayName, 'rb'), 'multipart/form-data')}
                # The MultipartEncoder is posted as data, don't use files=...!
                mp_encoder = MultipartEncoder(fields=files)
                # The MultipartEncoder provides the content-type header with the boundary:
                headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
                res = requests.post(url, data = mp_encoder, headers=headers)
                res.raise_for_status()
                results.append(res)
            return results
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def simple_import_pbix_folder_in_group_preview(self, workspace_id, folderPath, nameConflict=None, overrideModelLabel=None, overrideReportLabel=None):
        """Creates new multiple contents in the specified workspace. Define a local folder with pbix files. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        folderPath: str 
            Set the file path from local file system like C:/Files/
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath: str
            Full local path of the files like "C:/Users/SimplePBI/Documents/"
        fileUrl: str
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        results = []
        try:
            allFiles= [files for root, dirs, files in os.walk(folderPath)][0]
            pbixFiles = [name for name in allFiles if name.endswith(("pbix"))]
            for datasetDisplayName in pbixFiles:
                url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}".format(workspace_id, datasetDisplayName)
                if nameConflict != None:
                    url = url + "&nameConflict={}".format(str(nameConflict))
                if overrideModelLabel != None:
                    url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
                if overrideReportLabel != None:
                    url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
                # you need this dictionary to convert a binary file into form-data format
                # None here means we skip the filename and file content is important 
                files = {'value': (None, open(folderPath+datasetDisplayName, 'rb'), 'multipart/form-data')}
                # The MultipartEncoder is posted as data, don't use files=...!
                mp_encoder = MultipartEncoder(fields=files)
                # The MultipartEncoder provides the content-type header with the boundary:
                headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
                res = requests.post(url, data = mp_encoder, headers=headers)
                res.raise_for_status()
                results.append(res)
            return results
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def simple_import_from_devops(self, organization, project, repository_id, path, devopsKey, workspace_id):
        '''This function will import a PBIX file from DevOps to Power BI. Only available for Pbix with size lower than 1gb
         ### Parameters
        ----
        organization: str
            The organization name in DevOps. For example: https://dev.azure.com/ibarrau/ the organization name is ibarrau
        project: str
            The project name in DevOps. For example: https://dev.azure.com/ibarrau/ladataweb_proj/ the project name is ladataweb_proj
        repository_id: str
            The repository name in DevOps. Sometimes matches the name of the repo.
        path: str
            The path of the file in DevOps. For example: /Prod/PBITenantOverview.pbix
        devopsKey: str
            The DevOps Key. You can turn it on from DevOps > User Settings > Personal Access Tokens
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL    
        ### Returns
        ----
        Dict:
            Response 200 or 202 Ok
        '''
        file_name = path.split("/")[-1]
        try:
            pbix = requests.get(url="https://dev.azure.com/{}/{}/_apis/git/repositories/{}/items?path={}&download=true&api-version=6.0".format(organization, project, repository_id, path), auth=('user', devopsKey))
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        try:
            res = self.simple_import_pbix_as_parameter(workspace_id, pbix.content, file_name)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def simple_import_from_github(self, owner, repo, path, github_pat, workspace_id):
        '''This function will import a PBIX file from GitHub to Power BI. The maximun size is 100Mb.
         ### Parameters
        ----
        owner: str
            The account owner of the repository. The name is not case sensitive. For example: https://dev.azure.com/ibarrau/ the organization name is ibarrau
        repo: str
            The name of the repository without the .git extension. The name is not case sensitive.
        path: str
            The path of the file in GitHub. For example: /Prod/PBITenantOverview.pbix
        github_pat: str
            The GitHub Personal Access Token. You can turn it on from Settings > Developer Settings > Personal Access Tokens
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL    
        ### Returns
        ----
        Dict:
            Response 202 Ok
        '''
        file_name = path.split("/")[-1]
        try:
            url = "https://api.github.com/repos/{}/{}/contents/{}".format(owner, repo, path)
            pbix_str = requests.get(url, headers={'Accept': 'application/vnd.github.raw+json', "Authorization": "Bearer {}".format(github_pat), 'X-GitHub-Api-Version': '2022-11-28' })
            #pbix_bytes = bytes(pbix_str.json()["content"], 'utf-8')
            #pbix = base64.decodebytes(pbix_bytes)
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
        try:
            res = self.simple_import_pbix_as_parameter(workspace_id, pbix_str.content, file_name)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)