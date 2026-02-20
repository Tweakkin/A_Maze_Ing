import sys
from config_parser import parse_coordinate, file_to_dict, val_keys, val_dimensions, val_bool, val_file

if __name__ == "__main__":

	# sys.argv must contain exactly 2 items: [script_name, config_file]
	if len(sys.argv) != 2:
		print("Error: Usage is python3 a_maze_ing.py <config_file>")
		sys.exit(1)
	
	#Turning the file into a dict
	parsed_dict = file_to_dict(sys.argv[1])

	#Checking for missing or unsupported keys
	bon_keys = val_keys(parsed_dict)
	
	#Validting the values of HEIGHT AND WIDTH
	parsed_dict = val_dimensions(parsed_dict)
	
	#Checking if ENTRY and EXIT values are valid
	parsed_dict['ENTRY'] = parse_coordinate(parsed_dict['ENTRY'], parsed_dict['HEIGHT'], parsed_dict['WIDTH'])
	parsed_dict['EXIT'] = parse_coordinate(parsed_dict['EXIT'], parsed_dict['HEIGHT'], parsed_dict['WIDTH'])
	if parsed_dict['ENTRY'] == parsed_dict['EXIT']:
		print("Error: 'ENTRY' and 'EXIT' coordinates cannot be the same!")
		sys.exit(1)
	#Validating 'PERFECT' value	
	parsed_dict = val_bool(parsed_dict)
	
	#Validating 'OUTPUT_FILE'
	val_file(parsed_dict)