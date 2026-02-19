import sys
import os


def parse_coordinate(coordinates, height, width):
	try:
		cords = coordinates.split(',')
		if len(cords) != 2:
			raise ValueError
		x = int(cords[0])
		y = int(cords[1])

		if x < 0 or x >= width or y < 0 or y >= height:
			print(f"Error: Coordinate {x},{y} is outside map dimensions ({width}x{height}).")
			sys.exit(1)
	except ValueError:
		print(f"Error: Invalid coordinate '{coordinates}'. Expected integers 'x,y'.")
		sys.exit(1)


if __name__ == "__main__":
	#=====================THE SYNTAX CHECK============================
	#
	# sys.argv must contain exactly 2 items: [script_name, config_file]
	if len(sys.argv) != 2:
		print("Error: Usage is python3 main.py <config_file>")
		sys.exit(1)
	try:
		#using 'with' to always close the file
		with open(sys.argv[1], "r") as file:
			parsed_dict = {}
			#looping through lines of the file
			for line in file:
				#removing white spaces at the beggining and end of file
				line = line.strip()
				#skipping the line if its empty
				if not line:
					continue
				#skipping the line if its a comment
				if line.startswith('#'):
					continue
				#splitting when first '=' is found
				line = line.split(sep='=', maxsplit=1)
				#check if '=' exists
				if len(line) != 2:
					continue
				#adding result to the dict
				parsed_dict.update({line[0].strip() : line[1].strip()})
	#handling if file was not found error
	except FileNotFoundError:
		print(f"Error: the file '{sys.argv[1]} was not found")
		sys.exit(1)
	#handling permission denied error
	except PermissionError:
		print(f"Error: you do not have permission to read '{sys.argv[1]}'")
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error: {e}")
	#============================================================================
	#
	#===============================The logic check=============================
	#
	allowed_keys = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT']
	#looping through parsed_dict looking for any unsupported keys
	for key in parsed_dict:
		if key not in allowed_keys:
			print(f"Error: Unknown or unsupported key '{key}'.")
			sys.exit(1)
	#looping through allowed_keys checking for missing keys
	for key in allowed_keys:
		if key not in parsed_dict:
			print(f"Error: Missing mandatory key '{key}'.")
			sys.exit(1)
	
	#Validting the values of HEIGHT AND WIDTH
	try:
		width_value = int(parsed_dict['WIDTH'])
		height_value = int(parsed_dict['HEIGHT'])

		if width_value < 3 or height_value < 3:
			print("Error: Map dimensions must be at least 3x3 (HEIGHT, WIDTH).")
			sys.exit(1)
	except ValueError:
		print("Error: WIDTH and HEIGHT must be integers.")
		sys.exit(1)
	
	#Checking if ENTRY and EXIT values are valid
	parse_coordinate(parsed_dict['ENTRY'], height_value, width_value)
	parse_coordinate(parsed_dict['EXIT'], height_value, width_value)

	#Validating 'PERFECT' value	
	raw_perfect = parsed_dict['PERFECT']
	if raw_perfect == "True":
		perfect_val = True
	elif raw_perfect == "False":
		perfect_val = False
	else:
		print(f"Error: PERFECT must be 'True' or 'False'. Found '{raw_perfect}'.")
		sys.exit(1)
	
	#Validating 'OUTPUT_FILE'
	#does it end with .txt?
	if not parsed_dict['OUTPUT_FILE'].endswith('.txt'):
		print("Error: 'OUTPUT_FILE' must end with .txt")
		sys.exit(1)
	#is it a directory?
	if os.path.isdir(parsed_dict['OUTPUT_FILE']):
		print("Error: 'OUTPUT_FILE' is a directory, not a file.")
		sys.exit(1)
	#Is the path valid?
	path = os.path.dirname(parsed_dict['OUTPUT_FILE'])
	if path and (not os.path.exists(path)):
		print("Error: Path doesn't exist for 'OUTPUT_FILE'")
		sys.exit(1)