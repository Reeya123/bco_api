# For JSON.
import json

# For exiting the program.
import sys

# For regular expressions
import re

class ConvertToSchema:

    # Class Description
    # -----------------

    # These methods are for taking a BCO and making it fit into a schema. More broadly, this script takes a JSON and converts it into JSON with a provided schema.

    # Load a schema to force the provided JSON to fit.
    def load_schema(self, schema_location, location_type):


        # Arguments
        # ---------

        # schema_location:  either the URI or the file location of the schema.

        #   location_type:  either 'URI', or 'file'

        # Returns
        # -------

        # A JSON object derived from the provided schema.


        # First, determine the location type.
        
        if location_type == 'URI':

            # ...for Chris
            print('hi')

        elif location_type == 'file':

            # Open the file.
            with open(schema_location, mode='r') as file:
                schema = json.load(file)

        # Return our new ID.
        return schema

    # Define a function to load multiple BCO files.
    def load_bco_files(self, file_locations):


        # Arguments
        # ---------

        # file_locations:  a list of BCO file locations.

        # *** Develop a check to make sure that a file with multiple BCOs are in an array. ***

        # Returns
        # -------

        # A dictionary of BCOs where the key is the file and the value is the BCO index.
        # Each of these values also contains a dictionary with the BCO contents.

        # Declare the dictionary that will return the BCO.
        bcos = {}

        # Create a flag that indicates there was a JSON conversion error.
        json_conversion_error = 0

        # Go over each file.
        for current_file in file_locations:

            # Open the file and store it.
            with open(current_file, mode='r') as file:

                # Try to see if the file actually has legitimate JSON.
                try:

                    bco = json.load(file)

                    # Store the BCO.
                    bcos[current_file] = bco

                except:

                    # Print the error to the command line.
                    print('Provided file ' + current_file + ' was unable to be converted to JSON.  The conversion error is listed below.')
                    print(json.load(file))

                    # Change the flag.
                    json_conversion_error = 1

        # If there was a JSON conversion error, stop the program.
        if json_conversion_error == 1:

            # Exit the program completely.
            sys.exit(2)

        else:

            # Dictionary for itemized BCOS from each file.
            processed_bcos = {}

            # Go over each file and its BCO(s) and assign a number to each BCO.
            for filename, contents in bcos.items():

                # Declare the filename key.
                processed_bcos[filename] = {}

                # Determine the type of contents.
                if type(contents) == 'list':

                    # Iterate over each item in the list.
                    for index in range(0, len(contents)):
                        processed_bcos[filename][str(index)] = contents

                else:
                    processed_bcos[filename]['0'] = contents

            # Return all the processed BCOs.
            return processed_bcos

    # Create a file with field discrepancies between the original object and the schema.
    def create_comparison_file(self, p_bcos, incoming_schema):

        # Arguments
        # ---------

        # p_bcos is the processed BCOs from ConvertToSchema().load_bco_files.
        # incoming_schema is the schema from ConvertToSchema().load_schema.

        # Returns
        # -------

        # something

        for file, contents in p_bcos.items():
            if file.get('ROOT') is not None:

                # Compare the single object against the schema.
                comparison = self.check_object_against_schema(bco_object=contents, i_schema=incoming_schema)


            else:
                print('hi')



    def read_mapping_files(self, mapping_locations):

        # Arguments
        # ---------

        # mapping_locations is a path with the mapping files.

        # Returns
        # -------

        # A dictionary where each key is the mapping file and each value is the instructions for that file.

        # Declare the dictionary that will return the mappings.
        mappings = {}


        # Go over each mapping file.
        for current_file in mapping_locations:

            # Open the mapping file and store it.
            with open(current_file, mode='r') as file:

                # Initialize mappings[current_file]
                mappings[current_file] = {}

                for line in file.readlines():

                    # Check each line for compliance with CRD with regex, quit on failure.
                    # Source: https://stackoverflow.com/questions/8888567/match-a-line-with-multiple-regex-using-python
                    # *** Find JSON path regex
                    # Regex accepts any values for JSON path and old/new values
                    #if not any re.match(line) for re in ['^FILE_PATH_REGEX,URI_REGEX,CREATE,[\"(.*?)\"],[\"(.*?)\"]$','^FILE_PATH_REGEX,URI_REGEX,CONVERT,[\"(.*?)\"],[\"(.*?)\"],[\"(.*?)\"]$','^FILE_PATH_REGEX,URI_REGEX,DELETE,[\"(.*?)\"]$']:
                    if 1:
                        # Print the error to the command line.
                        # *** How do you print the line number
                        print('Provided mapping file ' + current_file + ' had invalid instruction formatting for line ' + line)

                        # Exit the program completely.
                        sys.exit(2)

                    else:
                        # Store the mappings.
                        split_line = ','.split(line)

                        # Check if the BCO URI is already defined in mappings dict.
                        # Append the instructions after the BCO URI if the BCO URI is already defined.
                        if split_line[1] in mappings[current_file][split_line[0]]:
                            mappings[current_file][split_line[0]][split_line[1]].append(','.join(split_line[2:]))

                        # If the BCO URI is not already defined, define it and make it a list populated with the instructions.
                        else:
                            mappings[current_file][split_line[0]][split_line[1]] = [','.join(split_line[2:])]

        return mappings




            


    def check_object_against_schema(self, bco_object, i_schema):
        print('1')

    def create_bco_from_instructions(self, bco_dict, mappings_dict):

        # Arguments
        # ---------

        # Take in the dictionary from read_mapping_files (mappings_dict) and the BCOs from load_bco_files.

        # Returns
        # -------

        # A dictionary of where the key is the new BCO file name and the value is the new BCO contents.

        # Possible errors:
        # - file existence has already been checked in previous functions
        # - an instruction is given in mappings_dict for an object in bco_dict that does not exist
        # - an instruction is given in mappings_dict for a field that does not exist in an existing object in bco_dict

        # Create a dictionary to hold the new jsons and their contents.
        new_jsons = {}

        # Iterate through the mappings files dict.
        for mappings_file, mappings_contents in mappings_dict.items():

            # Iterate through the mappings contents dict, where each key is a bco_file and each value is a bco_id within that file.
            for bco_file, bco_id in mappings_contents.items():

                # Iterate over each of the BCOs in the bco file.
                for bco in bco_dict[bco_file]:

                    # Check that bco_id exists in the bco. If so, run all commands.
                    if bco_id in bco:

                        # Create a copy of the bco contents.
                        new_bco = bco

                        # Load the commands from the mapping dictionary.
                        commands = mappings_dict[mappings_file][bco_file][bco_id]

                        # Iterate through the commands for that bco.
                        for command in commands:

                            # Split the command string into blocks.
                            split_command = ','.split(command)

                            # Perform the CREATE command.
                            if split_command[0] == 'CREATE':
                                exec('new_bco[' + split_command[1] + '] =' + split_command[2])

                            # Perform the CONVERT command.
                            elif split_command[0] == 'CONVERT':

                                # Come back to this.
                                exec(split_command[1] + '=' + split_command[2])

                            # Perform the DELETE command.
                            else:
                                new_bco.pop(split_command[1], None)

                        # Write new_bco to file.


                    # Error statement if bco_id was not found.
                    else:
                        print(bco_id + ' was not found in ' + bco_file)






