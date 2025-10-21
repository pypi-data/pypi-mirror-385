import sys
from IPython import embed


def interactive_shell():
    score = 0
    shell = embed()

    def check_imported(module_name):
        nonlocal score
        if module_name in shell.user_ns:
            print(f"Congratulations! You have successfully imported {module_name}.")
            score += 1
            print(f"Your current score is: {score}")
        else:
            print(f"Please import the {module_name} module.")

    while True:
        user_input = input("Type 'import math' to test if you've imported it correctly: ")
        if user_input == "import math":
            check_imported('math')
        elif user_input.lower() in ['exit', 'quit']:
            print(f"Final score: {score}")
            break
        else:
            print("Invalid input. Please try again.")


if __name__ == '__main__':
    interactive_shell()
