def select_from_list(options, prompt="Select an option:", required=False, allow_skip=True):
    if not options:
        raise ValueError("Options list is empty.")
    while True:
        print(prompt)
        for i, opt in enumerate(options, start=1):
            print(f"{i}. {opt}")
        if allow_skip and not required:
            print("0. Skip")

        selection = input("Enter number: ").strip()
        if allow_skip and selection == "0" and not required:
            return None
        try:
            index = int(selection)
            if 1 <= index <= len(options):
                return options[index - 1]
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def select_from_dict(options, prompt="Select a key:", required=False, allow_skip=True):
    if not options:
        raise ValueError("Options dictionary is empty.")
    keys = list(options.keys())
    values = list(options.values())
    while True:
        print(prompt)
        for i, k in enumerate(keys, start=1):
            print(f"{i}. {k} → {values[i-1]}")
        if allow_skip and not required:
            print("0. Skip")

        selection = input("Enter number: ").strip()
        if allow_skip and selection == "0" and not required:
            return None
        try:
            index = int(selection)
            if 1 <= index <= len(keys):
                return keys[index - 1], values[index - 1]
        except ValueError:
            pass
        print("Invalid selection. Try again.")
