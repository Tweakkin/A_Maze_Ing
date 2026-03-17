import sys
import os
from typing import Any


# Class that reads a config file and validates all its fields
class ConfigPasrer:
    # Initializes the parser with the config filename
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.parsed_dict: dict[str, Any] = {}
        self.bon_keys: list[str] = []

    # Parses and validates a coordinate string "x,y" against maze dimensions
    def parse_coordinate(
        self, coordinates: str, height: int, width: int
    ) -> tuple[int, int]:
        try:
            # Split the string by comma to get x and y
            cords = coordinates.split(',')
            if len(cords) != 2:
                print("Error: Expected format of EXIT AND ENTRY 'x,y'")
                sys.exit(0)
            x = int(cords[0])
            y = int(cords[1])

            # Check if coordinate is within maze bounds
            if x < 0 or x >= width or y < 0 or y >= height:
                print(
                    (
                        f"Error: Coordinate {x},{y} is outside map "
                        f"dimensions ({width}x{height})."
                    )
                )
                sys.exit(0)
            # if not (x == 0 or x == width - 1 or y == 0 or y == height - 1):
            #     print(
            #         "Error: 'ENTRY' and 'EXIT' must be on the border of "
            #         "the maze"
            #     )
            #     sys.exit(0)
        except ValueError:
            print(
                (
                    f"Error: Invalid coordinate '{coordinates}'. Expected "
                    "integers 'x,y'."
                )
            )
            sys.exit(0)
        return (x, y)

    # Validates that WIDTH and HEIGHT are integers within allowed range
    def val_dimensions(self, parsed_dict: dict[str, Any]) -> dict[str, Any]:
        try:
            width_value = int(parsed_dict['WIDTH'])
            height_value = int(parsed_dict['HEIGHT'])

            # Minimum maze size is 9x7
            if width_value < 9 or height_value < 7:
                print(
                    "Error: Map dimensions must be at least 9x7 "
                    "(WIDTH x HEIGHT)."
                )
                sys.exit(0)
            # Maximum maze size is 200x200
            if width_value > 200 or height_value > 200:
                print("Error: Map dimensions must not exceed 200x200.")
                sys.exit(0)
        except ValueError:
            print("Error: WIDTH and HEIGHT must be integers.")
            sys.exit(0)
        parsed_dict['WIDTH'] = width_value
        parsed_dict['HEIGHT'] = height_value
        return parsed_dict

    # Checks for missing mandatory keys and collects unsupported bonus keys
    def val_keys(self, parsed_dict: dict[str, Any]) -> list[str]:
        allowed_keys = ['WIDTH', 'HEIGHT', 'ENTRY',
                        'EXIT', 'OUTPUT_FILE', 'PERFECT', 'ALGO']
        mandatory_keys = ['WIDTH', 'HEIGHT', 'ENTRY',
                          'EXIT', 'OUTPUT_FILE', 'PERFECT']
        bonus_keys = []
        # looping through parsed_dict looking for any unsupported keys
        for key in parsed_dict:
            if key not in allowed_keys:
                bonus_keys.append(key)
        # looping through allowed_keys checking for missing keys
        for key in mandatory_keys:
            if key not in parsed_dict:
                print(f"Error: Missing mandatory key '{key}'.")
                sys.exit(0)
        return bonus_keys

    # Validates that ALGO is either 'dfs' or 'prim'
    def val_algo(self, parsed_dict: dict[str, Any]) -> dict[str, Any]:
        algo = parsed_dict.get('ALGO', 'dfs')
        algo = str(algo).strip().lower()

        if algo not in ('dfs', 'prim'):
            print(f"Error: ALGO must be 'dfs' or 'prim'. Found '{algo}'.")
            sys.exit(0)

        parsed_dict['ALGO'] = algo
        return parsed_dict

    # Validates and converts PERFECT value from string to boolean
    def val_bool(self, parsed_dict: dict[str, Any]) -> dict[str, Any]:
        parsed_dict['PERFECT'] = parsed_dict['PERFECT'].strip().lower()
        if parsed_dict['PERFECT'] == "true":
            parsed_dict['PERFECT'] = True
            return parsed_dict
        elif parsed_dict['PERFECT'] == "false":
            parsed_dict['PERFECT'] = False
            return parsed_dict
        else:
            print(
                (
                    "Error: PERFECT must be 'True' or 'False'. "
                    f"Found '{parsed_dict['PERFECT']}'."
                )
            )
            sys.exit(0)
            return parsed_dict

    # Validates that OUTPUT_FILE is a valid .txt file path
    def val_file(self, parsed_dict: dict[str, Any]) -> None:
        # does it end with .txt?
        if not parsed_dict['OUTPUT_FILE'].endswith('.txt'):
            print("Error: 'OUTPUT_FILE' must end with .txt")
            sys.exit(0)
        # is it a directory?
        if os.path.isdir(parsed_dict['OUTPUT_FILE']):
            print("Error: 'OUTPUT_FILE' is a directory, not a file.")
            sys.exit(0)
        # Is the path valid?
        path = os.path.dirname(parsed_dict['OUTPUT_FILE'])
        if path and (not os.path.exists(path)):
            print("Error: Path doesn't exist for 'OUTPUT_FILE'")
            sys.exit(0)

    # Reads the config file and converts key=value lines into a dictionary
    def file_to_dict(self, filename: str) -> dict[str, Any]:
        try:
            with open(filename, "r") as file:
                parsed_dict = {}
                # looping through lines of the file
                for line in file:
                    # removing white spaces at the beggining and end of file
                    line = line.strip()
                    # skipping the line if its empty
                    if not line:
                        continue
                    # skipping the line if its a comment
                    if line.startswith('#'):
                        continue
                    # splitting when first '=' is found
                    parts = line.split(sep='=', maxsplit=1)
                    # check if '=' exists
                    if len(parts) != 2:
                        continue
                    key = parts[0].strip().upper()
                    value = parts[1].strip()
                    # Check for duplicate keys
                    if key in parsed_dict:
                        print(
                            (
                                f"Error: Duplicate key '{key}' found in "
                                "config file."
                            )
                        )
                        sys.exit(0)
                    parsed_dict[key] = value
                    # adding result to the dict
                    # parsed_dict.update(
                    #     {parts[0].strip().upper(): parts[1].strip()}
                    # )
        # handling if file was not found error
        except FileNotFoundError:
            print(f"Error: the file '{filename}' was not found")
            sys.exit(0)
        # handling permission denied error
        except PermissionError:
            print(f"Error: you do not have permission to read '{filename}'")
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(0)

        return parsed_dict

    # Main method that runs all validation steps in order
    def parse(self) -> None:
        # Turning the file into a dict
        self.parsed_dict = self.file_to_dict(self.filename)

        # Checking for missing or unsupported keys
        self.bon_keys = self.val_keys(self.parsed_dict)

        # Validting the values of HEIGHT AND WIDTH
        self.parsed_dict = self.val_dimensions(self.parsed_dict)

        # Parsing and validating ENTRY coordinate
        self.parsed_dict['ENTRY'] = self.parse_coordinate(
            self.parsed_dict['ENTRY'],
            self.parsed_dict['HEIGHT'],
            self.parsed_dict['WIDTH'],
        )
        # Parsing and validating EXIT coordinate
        self.parsed_dict['EXIT'] = self.parse_coordinate(
            self.parsed_dict['EXIT'],
            self.parsed_dict['HEIGHT'],
            self.parsed_dict['WIDTH'],
        )
        # ENTRY and EXIT must be different
        if self.parsed_dict['ENTRY'] == self.parsed_dict['EXIT']:
            print("Error: 'ENTRY' and 'EXIT' coordinates cannot be the same!")
            sys.exit(0)

        # Validating PERFECT boolean and ALGO values
        self.parsed_dict = self.val_bool(self.parsed_dict)
        self.parsed_dict = self.val_algo(self.parsed_dict)

        # Validating the output file path
        self.val_file(self.parsed_dict)

        # Handling optional SEED key from bonus keys
        if 'SEED' in self.bon_keys:
            try:
                self.parsed_dict['SEED'] = int(self.parsed_dict['SEED'])
            except ValueError:
                print("Error: SEED must be an integer.")
                sys.exit(0)
            self.bon_keys.remove('SEED')
        else:
            self.parsed_dict['SEED'] = None
