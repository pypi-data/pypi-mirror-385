""" Core module with cli """
import csv
import click
import json
import os
import requests
import sys
import yaml
from pypus import shelf
from pypus import Octo
from termcolor import cprint
from pprint import pprint
from requests.api import get, head
from urllib3.exceptions import InsecureRequestWarning


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
# Set `verify=False` on `requests.post`.
# requests.post(url='https://example.com', data={'bar':'baz'}, verify=False)



@click.group()
def main():
    """
    Pypus is a cli tool for making changes to Octopus Deploy\n
    Set the following environment variables\n
    OCTOPUS_API_KEY = 'API-YOURAPIKEY'\n
    OCTOPUS_SERVER_URI = 'https://my-octopus-server.com/api'

    Example Usage: pypus get-projects Default

    Variable set examples \n
    Example with scope: \n
    pypus set-var SQLDBA SSIS_BONDDB test test1 \\
            '{"Environment":["Environments-90"]}'

    Example without scope: \n
    pypus set-var SQLDBA SSIS_BONDDB test1 test2 '{}'

    """

@main.command('check-env', short_help='Check required environment variables')
def check_env():
    """ Prints out the current necessary environment variables """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    print(f"Your environment has {octopus_api_key} for the variable OCTOPUS_API_KEY")
    print(f"Your environment has {octopus_server_uri} for the variable OCTOPUS_SERVER_URI")


@main.command('search-vars-by-value', short_help='Search all variables in a space')
@click.argument("space")
@click.argument("value")
def search_vars_by_value(space, value) -> None:
    """Finds service by name and disables it"""
    if 'OCTOPUS_API_KEY' in os.environ and 'OCTOPUS_SERVER_URI' in os.environ:
        octopus_api_key = os.getenv('OCTOPUS_API_KEY')
        octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
        headers = {'X-Octopus-ApiKey': octopus_api_key}
        print("This will not search values that are a type of 'SECRET'!")
    else:
        print('Please set the OCTOPUS_API_KEY and OCTOPUS_SERVER_URI environment variables.')
        print("Example API: export OCTOPUS_API_KEY=API-5NKCSNK4U1231231232332")
        print("Example URI: export OCTOPUS_SERVER_URI=https://deploys.example.com/api")
        exit(1)
    space_name = space
    variable_value = value
    def get_octopus_resource(uri):
        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)



    csv_export_path = 'var-search-by-value.csv'
    # Optional: set a path to export to csv

    variable_tracker = []
    octopus_server_uri = octopus_server_uri.rstrip('/')
    octopus_server_base_uri = octopus_server_uri.rstrip('api')

    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    print('Looking for usages of variable value \'{0}\' in space \'{1}\''.format(variable_value, space_name))

    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))

    for project in projects:
        project_name = project['Name']
        project_web_uri = project['Links']['Web'].lstrip('/')
        print('Checking project \'{0}\''.format(project_name))
        #uri = '{0}/api/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], project['VariableSetId'])
        #project_variable_set = get_octopus_resource(uri, headers)
        project_variable_set = get_octopus_resource('{0}/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], project['VariableSetId']))
        
        # Check to see if variable is named in project variables.
        matching_value_variables = [variable for variable in project_variable_set['Variables'] if variable['Value'] != None and variable_value in variable['Value']]
        if matching_value_variables is not None:
            for variable in matching_value_variables:
                tracked_variable = {
                    'Project': project_name,
                    'MatchType': 'Named Project Variable',
                    'Context': variable['Name'],
                    'AdditionalContext': None,
                    'Property': None,
                    'VariableSet': None
                }
                if tracked_variable not in variable_tracker:
                    variable_tracker.append(tracked_variable)
        
    # Get variable sets
    uri = '{0}/{1}/libraryvariablesets?contentType=Variables'.format(octopus_server_uri, space['Id'])
    variable_sets = get_octopus_resource(uri)

    for variable_set in variable_sets['Items']:
        print(variable_set)
        uri = '{0}/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], variable_set['VariableSetId'])
        variables = get_octopus_resource(uri)
        matching_value_variables = [variable for variable in variables['Variables'] if variable['Value'] != None and variable_value in variable['Value']]
        if matching_value_variables is not None:
            for variable in matching_value_variables:
                tracked_variable = {
                    'Project': None,
                    'VariableSet': variable_set['Name'],
                    'MatchType': 'Value in Variable Set',
                    'Context': variable['Value'],
                    'Property': None,
                    'AdditionalContext': variable['Name']
                }

                if tracked_variable not in variable_tracker:
                    variable_tracker.append(tracked_variable)


    results_count = len(variable_tracker)
    if results_count > 0:
        print('')    
        print('Found {0} results:'.format(results_count))
        for tracked_variable in variable_tracker:
            print('Project           : {0}'.format(tracked_variable['Project']))
            print('MatchType         : {0}'.format(tracked_variable['MatchType']))
            print('Context           : {0}'.format(tracked_variable['Context']))
            print('AdditionalContext : {0}'.format(tracked_variable['AdditionalContext']))
            print('Property          : {0}'.format(tracked_variable['Property']))
            print('VariableSet              : {0}'.format(tracked_variable['VariableSet']))
            print('')
        if csv_export_path:
            with open(csv_export_path, mode='w') as csv_file:
                fieldnames = ['Project', 'MatchType', 'Context', 'AdditionalContext', 'Property', 'VariableSet']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for tracked_variable in variable_tracker:
                    writer.writerow(tracked_variable)


@main.command('search-vars-by-name', short_help='Search all variables in a space')
@click.argument("space")
@click.argument("name")
def search_vars_by_name(space, name) -> None:
    """ Search for variable by name """
    if 'OCTOPUS_API_KEY' in os.environ and 'OCTOPUS_SERVER_URI' in os.environ:
        octopus_api_key = os.getenv('OCTOPUS_API_KEY')
        octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
        headers = {'X-Octopus-ApiKey': octopus_api_key}
    else:
        print('Please set the OCTOPUS_API_KEY and OCTOPUS_SERVER_URI environment variables.')
        print("Example API: export OCTOPUS_API_KEY=API-5NKCSNK4U1231231232332")
        print("Example URI: export OCTOPUS_SERVER_URI=https://deploys.example.com/api")
        exit(1)
    space_name = space
    variable_name = name
    def get_octopus_resource(uri):
        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)

    # Search through Project's Deployment Processes?
    search_deployment_processes = True

    # Search through Project's Runbook Processes?
    search_runbook_processes = False

    # Optional: set a path to export to csv
    csv_export_path = 'var-search-by-name.csv'

    variable_tracker = []
    octopus_server_uri = octopus_server_uri.rstrip('/')
    octopus_server_base_uri = octopus_server_uri.rstrip('api')

    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    print('Looking for usages of variable named \'{0}\' in space \'{1}\''.format(variable_name, space_name))

    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))

    for project in projects:
        project_name = project['Name']
        project_web_uri = project['Links']['Web'].lstrip('/')
        print('Checking project \'{0}\''.format(project_name))
        project_variable_set = get_octopus_resource('{0}/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], project['VariableSetId']))
        
        # Check to see if variable is named in project variables.
        matching_named_variables = [variable for variable in project_variable_set['Variables'] if variable_name.lower() in variable['Name'].lower()]
        if matching_named_variables is not None:
            for variable in matching_named_variables:
                tracked_variable = {
                    'Project': project_name,
                    'MatchType': 'Named Project Variable',
                    'Context': variable['Name'],
                    'AdditionalContext': None,
                    'Property': None,
                    'Link': '{0}{1}/variables'.format(octopus_server_base_uri, project_web_uri)
                }
                if tracked_variable not in variable_tracker:
                    variable_tracker.append(tracked_variable)
        
        # Check to see if variable is referenced in other project variable values.
        matching_value_variables = [variable for variable in project_variable_set['Variables'] if variable['Value'] is not None and variable_name.lower() in variable['Value'].lower()]
        if matching_value_variables is not None:
            for variable in matching_value_variables:
                tracked_variable = {
                    'Project': project_name,
                    'MatchType': 'Referenced Project Variable',
                    'Context': variable['Name'],
                    'AdditionalContext': variable['Value'],
                    'Property': None,
                    'Link': '{0}{1}/variables'.format(octopus_server_base_uri, project_web_uri)
                }
                if tracked_variable not in variable_tracker:
                    variable_tracker.append(tracked_variable)
        
        # Search Deployment process if enabled
        if search_deployment_processes:
            deployment_process = get_octopus_resource('{0}/{1}/deploymentprocesses/{2}'.format(octopus_server_uri, space['Id'], project['DeploymentProcessId']))
            for step in deployment_process['Steps']:
                for step_key in step.keys():
                    step_property_value = str(step[step_key])
                    if step_property_value is not None and variable_name.lower() in step_property_value.lower():
                        tracked_variable = {
                            'Project': project_name,
                            'MatchType': 'Step',
                            'Context': step['Name'],
                            'Property': step_key,
                            'AdditionalContext': None,
                            'Link': '{0}{1}/deployments/process/steps?actionId={2}'.format(octopus_server_base_uri, project_web_uri, step['Actions'][0]['Id'])
                        }
                        if tracked_variable not in variable_tracker:
                            variable_tracker.append(tracked_variable)

        # Search Runbook processes if configured
        if search_runbook_processes == True:
            runbooks_resource = get_octopus_resource('{0}/{1}/projects/{2}/runbooks?skip=0&take=5000'.format(octopus_server_uri, space['Id'], project['Id']))
            runbooks = runbooks_resource['Items']
            for runbook in runbooks:
                runbook_processes_link = runbook['Links']['RunbookProcesses']
                runbook_process = get_octopus_resource('{0}/{1}'.format(octopus_server_base_uri, runbook_processes_link))
                for step in runbook_process['Steps']:
                    for step_key in step.keys():
                        step_property_value = str(step[step_key])
                        if step_property_value is not None and variable_name in step_property_value:
                            tracked_variable = {
                                'Project': project_name,
                                'MatchType': 'Runbook Step',
                                'Context': runbook['Name'],
                                'Property': step_key,
                                'AdditionalContext': step['Name'],
                                'Link': '{0}{1}/operations/runbooks/{2}/process/{3}/steps?actionId={4}'.format(octopus_server_base_uri, project_web_uri, runbook['Id'], runbook['RunbookProcessId'], step['Actions'][0]['Id'])
                            }
                            if tracked_variable not in variable_tracker:
                                variable_tracker.append(tracked_variable)               

    results_count = len(variable_tracker)
    if results_count > 0:
        print('')    
        print('Found {0} results:'.format(results_count))
        for tracked_variable in variable_tracker:
            print('Project           : {0}'.format(tracked_variable['Project']))
            print('MatchType         : {0}'.format(tracked_variable['MatchType']))
            print('Context           : {0}'.format(tracked_variable['Context']))
            print('AdditionalContext : {0}'.format(tracked_variable['AdditionalContext']))
            print('Property          : {0}'.format(tracked_variable['Property']))
            print('Link              : {0}'.format(tracked_variable['Link']))
            print('')
        if csv_export_path:
            with open(csv_export_path, mode='w') as csv_file:
                fieldnames = ['Project', 'MatchType', 'Context', 'AdditionalContext', 'Property', 'Link']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for tracked_variable in variable_tracker:
                    writer.writerow(tracked_variable)


@main.command('get-machines', short_help='Get a list of all machines for a space')
@click.argument("space")
def get_machines(space):
    """ Get a list of all machines for the defined space

    Arguments:
        space: The name of the Octopus Deploy Space

    """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    def get_octopus_resource(uri):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        response = requests.get(uri, headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        """ Gets a resource from the API by name

        Arguments:
            uri: The base url of the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)
    space_name = space
    space = get_by_name(f"{octopus_server_uri}/spaces/all", space_name)
    machines = get_octopus_resource(f"{octopus_server_uri}/{space['Id']}/machines/all")
    print(f"The space {space_name} has these machines in it")
    for i in machines:
        print(f"Machine {i['Name']} has an ID of {i['Id']} and \
                is assigned to these {i['Roles']} roles.")
    return machines


@main.command('get-spaces', short_help='Get a list of spaces for server')
def get_spaces():
    """ Get spaces for Octopus instance """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    def get_octopus_resource(uri, headers,
                             skip_count=0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)), headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0) and (len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)
        else:
            return results
        # return results
        return items
    uri = f"{octopus_server_uri}/spaces"
    spaces = get_octopus_resource(uri, headers)
    for i in spaces:
        print(f"Space {i['Name']} has an ID of {i['Id']}")
    uri_main = octopus_server_uri.split('//')[1]
    uri_main = uri_main.split('/')[0]
    return spaces


@main.command('add-vars-toshelf',
              short_help='Parse json object and store variables')
@click.argument('json-file', type=click.Path(exists=True))
def add_vars_toshelf(json_file):
    """ Add variables to shelf for storage """
    filename = str(json_file)
    filename = filename.split('.', 1)[0]
    with open(json_file, encoding='UTF-8') as file:
        data = json.load(file)
        shelf.shelf_add_item(filename, 'Variables', data['Variables'])
        shelf.shelf_add_item(filename, 'ScopeValues', data['ScopeValues'])


@main.command('get-vars',
              short_help='Get a list of vars for a project in a space')
@click.argument("space")
@click.argument("project")
def get_vars(space, project):
    """ Get a list of vars for a project within a space

    Arguments:
        space: The space where the project resides
        project: The project from which to get variables

    """
    def get_octopus_resource(uri, headers, skip_count=0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)),
                                headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0
                    and len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)
            return items
        return results
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    project_name = project
    space_name = space
    uri = f"{octopus_server_uri}/spaces"
    spaces = get_octopus_resource(uri, headers)
    space = next((x for x in spaces if x['Name'] == space_name), None)
    uri = f"{octopus_server_uri}/{space['Id']}/projects"
    projects = get_octopus_resource(uri, headers)
    project = next((x for x in projects if x['Name'] == project_name), None)
    if project is not None:
        uri = f"{octopus_server_uri}/{space['Id']}/variables/{project['VariableSetId']}"
        print(uri)
        project_variables = get_octopus_resource(uri, headers)
        for var in project_variables['Variables']:
            print(f"ID: {var['Id']} Name: {var['Name']}\
                  Value: {var['Value']} Scope: {var['Scope']}")
        return project_variables
    return None


@main.command('dump-vars-all-projects',
              short_help='Dump vars for all projects in a space to json files')
@click.argument("space")
def dump_vars_all_projects(space):
    """ Dump vars for all projects in a space to json files

    Arguments:
        space: The space where the project resides

    """
    def get_octopus_resource(uri, headers, skip_count=0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)),
                                headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0
                    and len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)
            return items
        return results
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    space_name = space
    uri = f"{octopus_server_uri}/spaces"
    spaces = get_octopus_resource(uri, headers)
    space = next((x for x in spaces if x['Name'] == space_name), None)
    uri = f"{octopus_server_uri}/{space['Id']}/projects"
    projects = get_octopus_resource(uri, headers)
    print(f"Found {len(projects)} projects in {space_name}")
    json_dir = f"{space_name}-vars"
    if os.path.isdir(json_dir) is False:
        os.mkdir(json_dir)
    os.chdir(json_dir)
    for project in projects:
        project_name = project['Name']
        uri = f"{octopus_server_uri}/{space['Id']}/projects/{project['Id']}"
        #print(uri)
        project = get_octopus_resource(uri, headers)
        uri = f"{octopus_server_uri}/{space['Id']}/variables/{project['VariableSetId']}"
        #print(uri)
        project_dict = get_octopus_resource(uri, headers)
        project_variables = project_dict['Variables']
        #for var in project_variables:
            #print(f"ID: {var['Id']} Name: {var['Name']}\
                  #Value: {var['Value']} Scope: {var['Scope']}")
        json.dump(project_variables, open(f"{space_name}-{project_name}-vars.json", 'w'))
    print(f"JSON files written to {json_dir}")


@main.command('get-vars-add-toshelf',
              short_help='Get a list of vars for a project in a\
              space and add to shelf')
@click.argument("space")
@click.argument("project")
@click.argument("shelf-name")
def get_vars_add_toshelf(space, project, shelf_name):
    """ Get a list of vars for a project within a space

    Arguments:
        space: The space where the project resides
        project: The project from which to get variables
        shelf-name: The name of the shelf to create

    """
    def get_octopus_resource(uri, headers, skip_count=0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)),
                                headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0
                    and len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)
            return items
        return results
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    project_name = project
    space_name = space
    uri = f"{octopus_server_uri}/spaces"
    spaces = get_octopus_resource(uri, headers)
    space = next((x for x in spaces if x['Name'] == space_name), None)
    uri = f"{octopus_server_uri}/{space['Id']}/projects"
    projects = get_octopus_resource(uri, headers)
    project = next((x for x in projects if x['Name'] == project_name), None)
    if project is not None:
        uri = f"{octopus_server_uri}/{space['Id']}/variables/{project['VariableSetId']}"
        project_variables = get_octopus_resource(uri, headers)
        shelf.shelf_add_item(shelf_name, 'Variables', project_variables)
    else:
        print(f"Unable to locate project {project}")


@main.command('set-var', short_help='Set a variable for a project in a space')
@click.argument("space")
@click.argument("project")
@click.argument("variable-name")
@click.argument("variable-value")
@click.argument("variable-scope")
@click.option('--sensitive', is_flag=True)
def set_var(space, project, variable_name, variable_value,
            variable_scope, sensitive):
    """ Set a variable for a project in a space

    Arguments:
        space: The space where the project resides
        project: The project where the variable is created
        variable-name: The name of the variable
        variable-value: The value to set for the variable
        scope-values: A list of key value pairs
        sensitive: Set this flag for passwords

        note: Only string variable types are currently supported

        Example: pypus set-var SQLDBA SSIS_BONDDB test test1 '{"Environment":["Environments-90"]}'
    """
    def get_octopus_resource(uri, headers, skip_count = 0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)), headers=headers, verify=False)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0) and (len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)

        else:
            return results
        # return results
        return items
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    project_name = project
    space_name = space
    variable_scope = json.loads(variable_scope)
    variable = {
            'Name': variable_name,
            'Value': variable_value,
            'Type': 'String',
            'Scope': variable_scope,
            'IsSensitive': sensitive
    }
    uri = '{0}/spaces'.format(octopus_server_uri)
    spaces = get_octopus_resource(uri, headers)
    space = next((x for x in spaces if x['Name'] == space_name), None)
    uri = '{0}/{1}/projects'.format(octopus_server_uri, space['Id'])
    projects = get_octopus_resource(uri, headers)
    project = next((x for x in projects if x['Name'] == project_name), None)
    if project != None:
        uri = '{0}/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], project['VariableSetId'])
        project_variables = get_octopus_resource(uri, headers)
        project_variable = next((x for x in project_variables['Variables'] if (x['Name'] == variable['Name']) and
            (x['Scope'] == variable['Scope'])), None)

        if project_variable == None:
            project_variables['Variables'].append(variable)
        else:
            project_variable['Value'] = variable['Value']
            project_variable['Type'] = variable['Type']
            project_variable['Scope'] = variable['Scope']
            project_variable['IsSensitive'] = variable ['IsSensitive']

        print(f"The json looks like {project_variables}")
        response = requests.put(uri, headers=headers, json=project_variables, verify=False)
        response.raise_for_status
        print(response)


@main.command('get-projects', short_help='Get a list of projects for space')
@click.argument("space")
def get_projects(space):
    """ Get a list of Projects for the defined URI

    Arguments:
        space: The name of the Octopus Deploy Space

    """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    def get_octopus_resource(uri):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        response = requests.get(uri, headers=headers, verify=False)
        response.raise_for_status()
        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        """ Gets a resource from the API by name

        Arguments:
            uri: The base url of the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)
    space_name = space
    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))
    print(f"The space {space_name} has these Projects in it")
    for i in projects:
        print(f"Project {i['Name']} has an ID of {i['Id']}")
    return projects


@main.command('get-process', short_help='Display the deployment process for a project')
@click.argument("space")
@click.argument("project")
@click.option('--raw', is_flag=True, help='Output the full deployment process JSON')
def get_process(space, project, raw):
    """Display the deployment process for a project within a space

    Arguments:
        space: The name of the Octopus Deploy Space
        project: The project whose deployment process will be displayed

    """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    if not octopus_api_key or not octopus_server_uri:
        print('Please set the OCTOPUS_API_KEY and OCTOPUS_SERVER_URI environment variables.')
        print("Example API: export OCTOPUS_API_KEY=API-EXAMPLE1234567890")
        print("Example URI: export OCTOPUS_SERVER_URI=https://deploys.example.com/api")
        exit(1)

    headers = {'X-Octopus-ApiKey': octopus_api_key}
    octopus_server_uri = octopus_server_uri.rstrip('/')

    def get_octopus_resource(uri):
        response = requests.get(uri, headers=headers, verify=False, timeout=60)
        response.raise_for_status()
        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)

    space_resource = get_by_name(f"{octopus_server_uri}/spaces/all", space)
    if space_resource is None:
        print(f"Could not find space named '{space}'.")
        exit(1)

    project_resource = get_by_name(f"{octopus_server_uri}/{space_resource['Id']}/projects/all", project)
    if project_resource is None:
        print(f"Could not find project '{project}' in space '{space}'.")
        exit(1)

    try:
        deployment_process = get_octopus_resource(
            f"{octopus_server_uri}/{space_resource['Id']}/deploymentprocesses/{project_resource['DeploymentProcessId']}"
        )
    except requests.HTTPError as error:
        print(f"Failed to retrieve deployment process: {error}")
        exit(1)

    if raw:
        print(json.dumps(deployment_process, indent=2))
        return

    def format_value(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        value_str = str(value)
        if len(value_str) > 120:
            return f"{value_str[:117]}..."
        return value_str

    def print_properties(properties):
        displayable = {
            key: value for key, value in properties.items()
            if key != 'Octopus.Action.Script.ScriptBody'
        }
        if displayable:
            print("       Properties:")
            for key in sorted(displayable.keys()):
                print(f"         {key}: {format_value(displayable[key])}")

        script_body = properties.get('Octopus.Action.Script.ScriptBody')
        if script_body:
            script_lines = script_body.splitlines()
            preview = script_lines[:3]
            if preview:
                print("       Script Body (preview):")
                for line in preview:
                    print(f"         {line}")
                if len(script_lines) > 3:
                    print("         ... (use --raw to view the full script)")

    print(f"Deployment process for project '{project}' in space '{space}':")
    steps = deployment_process.get('Steps', [])
    if not steps:
        print("No steps defined in the deployment process.")
        return

    for index, step in enumerate(steps, start=1):
        print(f"{index}. Step: {step.get('Name', 'Unnamed step')}")
        condition = step.get('Condition')
        if condition and condition != 'Success':
            print(f"   Condition: {condition}")
        start_trigger = step.get('StartTrigger')
        if start_trigger and start_trigger != 'DeploymentStarted':
            print(f"   Start Trigger: {start_trigger}")

        actions = step.get('Actions', [])
        if not actions:
            print("   (no actions defined)")
            continue

        for action in actions:
            action_name = action.get('Name', 'Unnamed action')
            action_type = action.get('ActionType', 'UnknownType')
            print(f"   - Action: {action_name} [{action_type}]")

            action_condition = action.get('Condition')
            if action_condition and action_condition != 'Success':
                print(f"       Condition: {action_condition}")

            packages = action.get('Packages') or []
            if packages:
                package_summary = ', '.join(
                    filter(None, [
                        pkg.get('PackageId') or pkg.get('Name') or pkg.get('StepPackageId')
                        for pkg in packages
                    ])
                )
                if package_summary:
                    print(f"       Packages: {package_summary}")

            properties = action.get('Properties') or {}
            if properties:
                print_properties(properties)

@main.command('get-runbooks', short_help='Get a list of Runbooks for space')
@click.argument("space")
def get_runbooks(space):
    """ get a list of Runbooks for the defined URI """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    def get_octopus_resource(uri):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        response = requests.get(uri, headers=headers, verify=False)
        response.raise_for_status()
        return json.loads(response.content.decode('utf-8'))

    def get_by_name(uri, name):
        """ Gets a resource from the API by name

        Arguments:
            uri: The base url of the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)
    space_name = space
    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))
    print(f"The space {space_name} has these Projects in it")
    for i in projects:
        print("++++++++++++++++++++++++++++++++++++++")
        print(f"Project {i['Name']} has an ID of {i['Id']}")
        projname = i['Name']
        projectid = i['Id']
        projbooks = get_octopus_resource('{0}/{1}/projects/{2}/runbooks'.format(octopus_server_uri, space['Id'], projectid))
        print(f"The Project {projname} has {len(projbooks['Items'])} Runbooks")
        runbooks = projbooks['Items']
        for i in runbooks:
            print(f"Runbook {i['Name']} has an ID of {i['Id']}")
            runbookid = i['Id']


@main.command('view-runbooks-publish-status', short_help='View which Runbooks have unpublished changes')
@click.argument("space")
def view_runbooks_publish_status(space):
    """ get a list of Runbooks for the defined URI
    and display the variable/snapshot publish status

    Arguments:
        space: The name of the Octopus Deploy Space
    """
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}


    def get_octopus_resource(uri):
        """ Gets a resource from the API

        Arguments:
            uri: The base url for the Octopus Deploy API
        """
        try:
            response = requests.get(uri, headers=headers, verify=False)
            response.raise_for_status()
        except requests.HTTPError as exception:
            print(exception)
        return json.loads(response.content.decode('utf-8'))


    def post_octopus_resource(uri, body):
        """ Posts a request to API

        Arguments:
            uri: The base url of the Octopus Deploy API
            body: The body of the HTTP POST request
        """
        response = requests.post(url = uri, json = body, headers=headers, verify=False)
        return response

    def get_by_name(uri, name):
        """ Gets a resource from the API by name

        Arguments:
            uri: The base url of the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)

    def get_item_by_name(uri, name):
        """ Gets a particular resource item by name

        Arguments:
            uri: The base url of the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources['Items'] if x['Name'] == name), None)

    def get_publishing_info(octopus_server_uri, space_id, runbook_id, runbook_pid, publish_id):
        """ Get the necessary info to determine if publishing is requred

        Arguments:
            octopus_server_uri: The base url of the Octopus Deploy API
            space_id: The ID of the Octopus Deploy Space
            runbook_id: The ID of the Octopus Deploy Runbook
            runbook_pid: The Process ID of the Octopus Deploy Runbook
            publish_id: The Publish ID of the Octopus Deploy Snapshot
        """
        snaptemp = get_octopus_resource('{0}/{1}/runbookProcesses/{2}/runbookSnapshotTemplate'.format(octopus_server_uri, space_id, runbook_pid))
        id_info = get_octopus_resource('{0}/{1}/runbookSnapshots/{2}/runbookRuns/template'.format(octopus_server_uri, space_id, publish_id))
        pub_info = { 'next_name': ((snaptemp['NextNameIncrement']).split()).pop(), 'packages': len(snaptemp['Packages']),
                'lib_set_modified': id_info['IsLibraryVariableSetModified'], 'run_proc_modified': id_info['IsRunbookProcessModified']}
        return pub_info

    def needs_publish(pub_info):
        """ Returns boolean based on whether the Runbook requires publishing

        Arguments:
            pub_info: A dictionary containing the necessary information for evaluation
        """
        if ((pub_info['lib_set_modified']) or (pub_info['run_proc_modified'])) and pub_info['packages'] == 0:
            return True
        else:
            return False

    space_name = space
    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))
    print(f"The space {space_name} has these Projects in it")
    for i in projects:
        print("++++++++++++++++++++++++++++++++++++++")
        print(f"Project {i['Name']} has an ID of {i['Id']}")
        projname = i['Name']
        projectid = i['Id']
        projbooks = get_octopus_resource('{0}/{1}/projects/{2}/runbooks'.format(octopus_server_uri, space['Id'], projectid))
        print(f"The Project {projname} has {len(projbooks['Items'])} Runbooks")
        runbooks = projbooks['Items']
        for i in runbooks:
            print(f"Runbook {i['Name']} has an ID of {i['Id']}")
            runbook_id = i['Id']
            runbook_pid = i['RunbookProcessId']
            publish_id = i['PublishedRunbookSnapshotId']
            info = get_publishing_info(octopus_server_uri, space['Id'], runbook_id, runbook_pid, publish_id)
            cprint(info, 'yellow')
            if((info['packages']) > 0):
                cprint('Packages are not supported in this revision of Pypus!!!', 'red')
                cprint('Publish this Runbook manually!!!', 'red')
            if(needs_publish(info)):
                cprint('Runbook needs publishing', 'red')
            else:
                cprint('No publishing needed', 'green')


@main.command('publish-runbooks', short_help='Publish Runbooks with unpublished variables')
@click.argument("space")
def publish_runbooks(space):
    """ get a list of Runbooks for the defined URI

    Arguments:
        space: The name of the Octopus Deploy Space
    """
    print('\n' * 3)
    print("This is going to publish ALL Runbooks for ALL Projects in the Space you provided")
    print("Try the view-runbook-publish-status first to see what will be affected.")
    input("CTRL+C to abort!!!   Press any key to continue.")
    print('\n' * 3)
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}

    def get_octopus_resource(uri):
        """ Gets a resource from the API

        Arguments:
            uri: The base url for the Octopus Deploy API
        """
        try:
            response = requests.get(uri, headers=headers, verify=False)
            response.raise_for_status()
        except requests.HTTPError as exception:
            print(exception)
        return json.loads(response.content.decode('utf-8'))

    def post_octopus_resource(uri, body):
        """ Posts a request to API

        Arguments:
            uri: The base url ofr the Octopus Deploy API
            body: The body of the HTTP POST
        """
        response = requests.post(url = uri, json = body, headers=headers, verify=False)
        return response

    def get_by_name(uri, name):
        """ Gets a resource from the API by name

        Arguments:
            uri: The base url for the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)

    def get_item_by_name(uri, name):
        """ Gets a particular resource item by name

        Arguments:
            uri: The base url for the Octopus Deploy API
            name: The name of the resource
        """
        resources = get_octopus_resource(uri)
        return next((x for x in resources['Items'] if x['Name'] == name), None)

    def get_publishing_info(octopus_server_uri, space_id, runbook_id, runbook_pid, publish_id):
        """ Get the necessary info to determine if publishing is requred

        Arguments:
            octopus_server_uri: The base url of the Octopus Deploy API
            space_id: The ID of the Octopus Deploy Space
            runbook_id: The ID of the Octopus Deploy Runbook
            runbook_pid: The Process ID of the Octopus Deploy Runbook
            publish_id: The Publish ID of the Octopus Deploy Snapshot
        """
        snaptemp = get_octopus_resource('{0}/{1}/runbookProcesses/{2}/runbookSnapshotTemplate'.format(octopus_server_uri, space_id, runbook_pid))
        id_info = get_octopus_resource('{0}/{1}/runbookSnapshots/{2}/runbookRuns/template'.format(octopus_server_uri, space_id, publish_id))
        pub_info = { 'next_name': snaptemp['NextNameIncrement'], 'packages': len(snaptemp['Packages']),
                'lib_set_modified': id_info['IsLibraryVariableSetModified'], 'run_proc_modified': id_info['IsRunbookProcessModified']}
        return pub_info

    def needs_publish(pub_info):
        """ Returns boolean based on whether the Runbook requires publishing

        Arguments:
            pub_info: A dictionary containing the necessary information for evaluation
        """
        if ((pub_info['lib_set_modified']) or (pub_info['run_proc_modified'])) and pub_info['packages'] == 0:
            return True
        else:
            return False

    def create_publish_object(project_id, runbook_id, snapshot_name):
        pub_object = {"ProjectId":project_id,"RunbookId":runbook_id,"Notes":'null',"Name":snapshot_name,"SelectedPackages":[]}
        return pub_object



    space_name = space
    space = get_by_name('{0}/spaces/all'.format(octopus_server_uri), space_name)
    projects = get_octopus_resource('{0}/{1}/projects/all'.format(octopus_server_uri, space['Id']))
    print(f"The space {space_name} has these Projects in it")
    for i in projects:
        print("++++++++++++++++++++++++++++++++++++++")
        print(f"Project {i['Name']} has an ID of {i['Id']}")
        project_name = i['Name']
        project_id = i['Id']
        project_runbooks = get_octopus_resource('{0}/{1}/projects/{2}/runbooks'.format(octopus_server_uri, space['Id'], project_id))
        print(f"The Project {project_name} has {len(project_runbooks['Items'])} Runbooks")
        runbooks = project_runbooks['Items']
        for i in runbooks:
            print(f"Runbook {i['Name']} has an ID of {i['Id']}")
            runbook_id = i['Id']
            runbook_pid = i['RunbookProcessId']
            publish_id = i['PublishedRunbookSnapshotId']
            info = get_publishing_info(octopus_server_uri, space['Id'], runbook_id, runbook_pid, publish_id)
            cprint(info, 'yellow')
            if((info['packages']) > 0):
                cprint('Packages are not supported in this revision of Pypus!!!', 'red')
                cprint('Publish this Runbook manually!!!', 'red')
                sys.exit()
            if(needs_publish(info)):
                cprint('Runbook needs publishing', 'red')
                publish_object = create_publish_object(project_id, runbook_id, info['next_name'])
                print(f" This is the publish_object {publish_object}")
                publish_result = post_octopus_resource('{0}/{1}/runbookSnapshots?publish=true'.format(octopus_server_uri, space['Id']), publish_object)
                print(publish_result)
            else:
                cprint('No publishing needed', 'green')


@main.command('read-yaml', short_help='Read a yaml file')
@click.argument('yaml-file', type=click.Path(exists=True))
def import_yaml(yaml_file):
    """ Reads a yaml file """
    with open(yaml_file, "r") as stream:
        try:
            print(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)


@main.command("list-shelf-data", short_help="Print data in a shelf")
@click.argument("shelf_name")
def list_shelf_data(shelf_name):
    """ Lists out contents for a Python shelf
    do not provide the file extension for the shelf
    you are referencing. The path should be included
    """
    shelf.shelf_list_contents(shelf_name)


@main.command("get-shelf-key", short_help="Print data for a key in a shelf")
@click.argument("shelf_name")
@click.argument("key_name")
def get_shelf_key(shelf_name, key_name):
    """ Assuming your shelf is a list of key value pairs,
    get the value for a particular key.
    """
    contents = shelf.get_shelf_item(shelf_name, key_name)
    for var in contents['Variables']:
        print(f"{var['Name']} {var['Value']} {var['Scope']}")


@main.command('transpose-from-shelf', short_help='Transpose variables from shelf')
@click.argument('shelf-name')
@click.argument('key-name')
@click.argument('yaml-map-file', type=click.Path(exists=True))
@click.argument('new-shelf')
def transpose_from_shelf(shelf_name, key_name, yaml_map_file, new_shelf):
    """ Takes variables from a shelf and transposes Scope Values
    based on a provided map from a yaml file. New values are written
    to a new shelf file.

    Example: yaml-map-file image in documentation

    Arguments:
        shelf-name: The current shelf that holds the variables
        key-name: The key that holds the variables to transpose
        yaml-map-file: The yaml file with the mapped values
        new-shelf: The new shelf created with the transposed values

    """
    object_list = []
    var_dicts = []
    contents = shelf.get_shelf_item(shelf_name, key_name)
    with open(yaml_map_file, 'r') as stream:
        try:
            map_values = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)

    for var in contents['Variables']:
        obj = Octo.OctoVar(var['Name'], var['Value'], var['Scope'])
        scopes = obj.getScope()
        if 'Environment' in scopes:
            env_list = scopes['Environment']
            for index, env in enumerate(env_list):
                if env in map_values['env_map']:
                    env_list[index] = map_values['env_map'][env]
            obj.setScopeEnvironment(env_list)
        object_list.append(obj)
    for obj in object_list:
        vdict = obj.getVarAsDict()
        var_dicts.append(vdict)
    shelf.shelf_add_item(new_shelf, 'Variables', var_dicts)


@main.command('set-vars-from-shelf', short_help='Set project variables from values stored in shelf')
@click.argument("space")
@click.argument("project")
@click.argument("shelf-name")
def set_vars_from_shelf(space, project, shelf_name):
    """ Sets project variables from values stored in shelf.

    Arguments:
        space: The space where the project resides
        project: The project where the variable is created
        shelf-name: Name of the shelf where values are stored

        note: Only string variable types are currently supported

        Example: pypus set-var-from-shelf SQLDBA SSIS_BONDDB transposed-vars-for-space1-project1'
    """
    def get_octopus_resource(uri, headers, skip_count = 0):
        """ Gets a resource from the API

        Arguments:
            uri: The base url of the Octopus Deploy API
        """
        items = []
        response = requests.get((uri + "?skip=" + str(skip_count)), headers=headers, verify=False)
        response.raise_for_status()
        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))
        # Store results
        if 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0) and (len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += get_octopus_resource(uri, headers, skip_count)

        else:
            return results
        # return results
        return items
    def get_shelf_key(shelf_name, key_name):
        var_list = []
        contents = shelf.get_shelf_item(shelf_name, key_name)
        for var in contents:
            var_list.append(var)
        return var_list
    octopus_api_key = os.getenv('OCTOPUS_API_KEY')
    octopus_server_uri = os.getenv('OCTOPUS_SERVER_URI')
    headers = {'X-Octopus-ApiKey': octopus_api_key}
    project_name = project
    space_name = space
    var_list = get_shelf_key(shelf_name, 'Variables')
    uri = '{0}/spaces'.format(octopus_server_uri)
    spaces = get_octopus_resource(uri, headers)
    space = next((x for x in spaces if x['Name'] == space_name), None)
    uri = '{0}/{1}/projects'.format(octopus_server_uri, space['Id'])
    projects = get_octopus_resource(uri, headers)
    project = next((x for x in projects if x['Name'] == project_name), None)
    if project != None:
        uri = '{0}/{1}/variables/{2}'.format(octopus_server_uri, space['Id'], project['VariableSetId'])
        project_variables = get_octopus_resource(uri, headers)
    else:
        print(f"Project {project_name} was not found")
        sys.exit(1)
    for var in var_list:
        variable_name = var['Name']
        variable_scope = var['Scope']
        variable_value = var['Value']
        sensitive = False
        variable = {
                'Name': variable_name,
                'Value': variable_value,
                'Type': 'String',
                'Scope': variable_scope,
                'IsSensitive': sensitive
        }
        project_variable = next((x for x in project_variables['Variables'] if (x['Name'] == variable['Name']) and
            (x['Scope'] == variable['Scope'])), None)

        if project_variable == None:
            project_variables['Variables'].append(variable)
        else:
            project_variable['Value'] = variable['Value']
            project_variable['Type'] = variable['Type']
            project_variable['Scope'] = variable['Scope']
            project_variable['IsSensitive'] = variable['IsSensitive']
    response = requests.put(uri, headers=headers, json=project_variables, verify=False)
    response.raise_for_status
    print(response)
