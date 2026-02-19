import sys
import os
from config_parser import parse_coordinate, file_to_dict, val_keys, val_dimensions, val_bool, val_file

if __name__ == "__main__":

	# sys.argv must contain exactly 2 items: [script_name, config_file]
	if len(sys.argv) != 2:
		print("Error: Usage is python3 a_maze_ing.py <config_file>")
		sys.exit(1)
	
	#Turning the file into a dict
	parsed_dict = file_to_dict(sys.argv[1])

	#Checking for missing or unsupported keys
	val_keys(parsed_dict)
	
	#Validting the values of HEIGHT AND WIDTH
	width_value, height_value = val_dimensions(parsed_dict)
	
	#Checking if ENTRY and EXIT values are valid
	parse_coordinate(parsed_dict['ENTRY'], height_value, width_value)
	parse_coordinate(parsed_dict['EXIT'], height_value, width_value)

	#Validating 'PERFECT' value	
	raw_perfect = val_bool(parsed_dict)
	
	#Validating 'OUTPUT_FILE'
	val_file(parsed_dict)