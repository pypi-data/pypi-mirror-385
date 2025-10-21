# File: interactx/confirm.py

def confirm_action(prompt="Are you sure?", default=False, required=False, allow_skip=True):
    choices = "[Y/n]" if default else "[y/N]"
    while True:
        resp = input(f"{prompt} {choices}: ").strip().lower()
        if allow_skip and resp == "" and not required:
            return None
        if resp == "" and required:
            print("Confirmation required.")
            continue
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Invalid choice. Please enter y or n.")
