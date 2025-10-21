# File: interactx/input_types.py

def input_value(
    prompt="Enter value:",
    value_type=str,
    required=False,
    allow_skip=True
):
    while True:
        val = input(f"{prompt} ").strip()
        if val == "" and allow_skip and not required:
            return None
        try:
            if value_type == str:
                return val
            if value_type == int:
                return int(val)
            if value_type == float:
                return float(val)
            raise ValueError(f"Unsupported type: {value_type}")
        except ValueError:
            print(f"Invalid {value_type.__name__}, please try again.")
