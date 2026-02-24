import sys
import os

class ConfigPasrer:
    def __init__(self, filename):
        self.filename = filename
        self.parsed_dict = {}
        self.bon_keys = []


    def parse_coordinate(self, coordinates: str, height: int, width: int) -> tuple[int, int]:
        try:
            cords = coordinates.split(',')
            if len(cords) != 2:
                print(f"Error: Expected format of EXIT AND ENTRY 'x,y'")
                sys.exit(1)
            x = int(cords[0])
            y = int(cords[1])

            if x < 0 or x >= width or y < 0 or y >= height:
                print(f"Error: Coordinate {x},{y} is outside map dimensions ({width}x{height}).")
                sys.exit(1)
            if not (x == 0 or x == width - 1 or y == 0 or y == height - 1):
                print("Error: 'ENTRY' and 'EXIT' must be on the border of the maze")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid coordinate '{coordinates}'. Expected integers 'x,y'.")
            sys.exit(1)
        return (x, y)

    def val_dimensions(self, parsed_dict: dict) -> dict:
        try:
            width_value = int(parsed_dict['WIDTH'])
            height_value = int(parsed_dict['HEIGHT'])

            if width_value < 9 or height_value < 7:
                print("Error: Map dimensions must be at least 9x7 (WIDTH x HEIGHT).")
                sys.exit(1)
        except ValueError:
            print("Error: WIDTH and HEIGHT must be integers.")
            sys.exit(1)
        parsed_dict['WIDTH'] = width_value
        parsed_dict['HEIGHT'] = height_value
        return parsed_dict

    def val_keys(self, parsed_dict: dict) -> list[str]:
        allowed_keys = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT']
        bonus_keys = []
        #looping through parsed_dict looking for any unsupported keys
        for key in parsed_dict:
            if key not in allowed_keys:
                bonus_keys.append(key)
        #looping through allowed_keys checking for missing keys
        for key in allowed_keys:
            if key not in parsed_dict:
                print(f"Error: Missing mandatory key '{key}'.")
                sys.exit(1)
        return bonus_keys

    def val_bool(self, parsed_dict: dict) -> dict:
        parsed_dict['PERFECT'] = parsed_dict['PERFECT'].strip().lower()
        if parsed_dict['PERFECT'] == "true":
            parsed_dict['PERFECT'] = True
            return parsed_dict
        elif parsed_dict['PERFECT'] == "false":
            parsed_dict['PERFECT'] = False
            return parsed_dict
        else:
            print(f"Error: PERFECT must be 'True' or 'False'. Found '{parsed_dict['PERFECT']}'.")
            sys.exit(1)

    def val_file(self, parsed_dict: dict) -> None:
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

    def file_to_dict(self, filename: str) -> dict:
        try:
            with open(filename, "r") as file:
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
                    parts = line.split(sep='=', maxsplit=1)
                    #check if '=' exists
                    if len(parts) != 2:
                        continue
                    #adding result to the dict
                    parsed_dict.update({parts[0].strip() : parts[1].strip()})
        #handling if file was not found error
        except FileNotFoundError:
            print(f"Error: the file '{filename} was not found")
            sys.exit(1)
        #handling permission denied error
        except PermissionError:
            print(f"Error: you do not have permission to read '{filename}'")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

        return parsed_dict

    def parse(self) -> None:
        #Turning the file into a dict
        self.parsed_dict = self.file_to_dict(self.filename)

        #Checking for missing or unsupported keys
        self.bon_keys = self.val_keys(self.parsed_dict)

        #Validting the values of HEIGHT AND WIDTH
        self.parsed_dict = self.val_dimensions(self.parsed_dict)

        self.parsed_dict['ENTRY'] = self.parse_coordinate(self.parsed_dict['ENTRY'], self.parsed_dict['HEIGHT'], self.parsed_dict['WIDTH'])
        self.parsed_dict['EXIT'] = self.parse_coordinate(self.parsed_dict['EXIT'], self.parsed_dict['HEIGHT'], self.parsed_dict['WIDTH'])
        if self.parsed_dict['ENTRY'] == self.parsed_dict['EXIT']:
            print("Error: 'ENTRY' and 'EXIT' coordinates cannot be the same!")
            sys.exit(1)

        self.parsed_dict = self.val_bool(self.parsed_dict)

        self.val_file(self.parsed_dict)