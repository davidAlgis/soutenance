import os
import re

# Configuration
SLIDES_DIR = "slides_src"

# Define the move
SOURCE_SLIDE = 42  # The slide we are moving
TARGET_POS = 4  # The position we want to move it to


def get_filename(number):
    """Returns the filename format sXX.py"""
    return f"s{number:02d}.py"


def update_file_content(content, old_num, new_num):
    """
    Updates @slide(x) and def slide_xx(self) in the content.
    """
    # 1. Update @slide(X)
    # pattern: @slide(42) -> @slide(4)
    slide_decorator_pattern = r"(@slide\s*\(\s*)" + str(old_num) + r"(\s*\))"
    content = re.sub(
        slide_decorator_pattern, r"\g<1>" + str(new_num) + r"\g<2>", content
    )

    # 2. Update def slide_XX(self)
    # Pattern for padded: slide_42 -> slide_04
    func_name_padded = f"slide_{old_num:02d}"
    new_func_name_padded = f"slide_{new_num:02d}"
    content = re.sub(
        r"def\s+" + func_name_padded, f"def {new_func_name_padded}", content
    )

    # Pattern for non-padded (just in case): slide_42 -> slide_4
    func_name_raw = f"slide_{old_num}"
    new_func_name_raw = f"slide_{new_num}"
    if func_name_raw != func_name_padded:
        content = re.sub(
            r"def\s+" + func_name_raw, f"def {new_func_name_raw}", content
        )

    return content


def main():
    if not os.path.exists(SLIDES_DIR):
        print(f"Error: Directory '{SLIDES_DIR}' not found.")
        return

    # --- Generate the Mapping Logic ---
    reorder_map = {}

    # 1. The main move: 42 becomes 4
    reorder_map[SOURCE_SLIDE] = TARGET_POS

    # 2. The shift: All slides currently at TARGET_POS (4) up to SOURCE_SLIDE - 1 (41)
    # need to move up by 1 (4 becomes 5, 41 becomes 42)
    # range(4, 42) generates numbers 4, 5, ..., 41
    for i in range(TARGET_POS, SOURCE_SLIDE):
        reorder_map[i] = i + 1

    print(
        f"Plan generated: Moving {SOURCE_SLIDE} to {TARGET_POS} and shifting {len(reorder_map)-1} slides."
    )

    # --- Execution Phase ---

    # Step 1: Rename ALL affected files to temporary names
    # This is critical to avoid overwriting s05 while processing s04
    temp_files = {}

    for old_num in reorder_map.keys():
        filename = get_filename(old_num)
        filepath = os.path.join(SLIDES_DIR, filename)

        if not os.path.exists(filepath):
            print(f"Warning: File {filename} not found. Skipping.")
            continue

        temp_filename = f"temp_{filename}"
        temp_filepath = os.path.join(SLIDES_DIR, temp_filename)

        os.rename(filepath, temp_filepath)
        temp_files[old_num] = temp_filepath

    # Step 2: Process content and write to NEW filenames
    for old_num, new_num in reorder_map.items():
        if old_num not in temp_files:
            continue

        temp_path = temp_files[old_num]
        new_filename = get_filename(new_num)
        new_filepath = os.path.join(SLIDES_DIR, new_filename)

        # Read from temp
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Modify content
        new_content = update_file_content(content, old_num, new_num)

        # Write to new file
        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        # Remove temp file
        os.remove(temp_path)

        print(f"Processed: Old {old_num} -> New {new_num} ({new_filename})")

    print("Reordering complete.")


if __name__ == "__main__":
    main()
