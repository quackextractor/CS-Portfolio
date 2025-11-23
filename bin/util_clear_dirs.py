import os
import shutil


def clear_output_directory():
    output_dir = "../output"

    if not os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' does not exist.")
        return

    # Remove and recreate the directory
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    print(f"Successfully cleared '{output_dir}'")

def clear_input_directory():
    input_dir = "../input"

    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return

    # Remove and recreate the directory
    shutil.rmtree(input_dir)
    os.makedirs(input_dir)
    print(f"Successfully cleared '{input_dir}'")

def user_prompt():
    while True:
        question = input("What do you want to clear? (0:exit/1:input/2:output/3:both):\n").strip().lower()
        if question == "0":
            print("Exiting without making changes.")
            break
        elif question in ['1', 'input']:
            clear_input_directory()
            break
        elif question in ['2', 'output']:
            clear_output_directory()
            break
        elif question in ['3', 'both']:
            clear_input_directory()
            clear_output_directory()
            break
        else:
            print("Invalid option. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    user_prompt()