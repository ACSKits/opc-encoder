# Standard libraries import re
import re

# Internal libraries
from scribe import read_file, write_new_lines

def add_encoding_single(path:str, controls, blade, cycle, marker_flag, marker_only_flag, special_tool_flag, fix_file_flag,
                        manual_tool_change_flag, stitched_flag, balsa_flag, flex_flag, customer_rev, acs_rev, customer):
    # Read lines
    old_lines = read_file(path)

    # Determine whether it's already encoded or counted
    already_encoded = any(
        ("P10301" in line if controls == "FAGOR" else "#601" in line)
        for line in old_lines
    )
    already_counted = any(
        ("P10320" in line if controls == "FAGOR" else "#620" in line)
        for line in old_lines
    )

    pattern = re.compile(r"(?:O)?(\d{3,4})")  # Looks for O followed by 4 digits

    for line in old_lines:
        match = pattern.search(line)
        if match:
            filenum = match.group(1)
            break
        else:
            print(f"[WARN] Could not extract file number from {path}")

    new_lines = []
    inserted = False

    # Track last M66 and M30 indexes
    m66_index = -1
    m30_index = -1

    for i, line in enumerate(old_lines):
        stripped = line.strip()

        # Track last occurrence of M66 and M30
        if "M66" in stripped:
            m66_index = len(new_lines)
        if "M30" in stripped:
            m30_index = len(new_lines)

        # Add encoding if not already present
        if not already_encoded:
            if (controls == "FAGOR"
                and i > 10
                and "M1" in stripped
                and not any(x in stripped for x in ["M11", "M10"])
                and not stripped.startswith("(")
                and not inserted):

                new_lines.append(line)
                new_lines += [
                    f"\nP10301 = {filenum}\n",
                    f"P10302 = {cycle}\n",
                    f"P10303 = {blade}\n",
                    f"P10304 = {marker_flag}\n",
                    f"P10305 = {marker_only_flag}\n",
                    f"P10306 = {special_tool_flag}\n",
                    f"P10307 = {fix_file_flag}\n",
                    f"P10308 = {manual_tool_change_flag}\n",
                    f"P10309 = {stitched_flag}\n",
                    f"P10310 = {balsa_flag}\n",
                    f"P10311 = 0\n",
                    f"P10312 = {flex_flag}\n",
                    f"P10313 = {customer_rev}\n",
                    f"P10314 = {acs_rev}\n",
                    f"P10315 = {customer}\n\n"
                ]
                inserted = True
                continue

            elif (controls == "FANUC"
                  and i > 10
                  and i + 1 < len(old_lines)
                  and not old_lines[i + 1].strip().startswith("(")
                  and not inserted):

                new_lines.append(line)
                new_lines += [
                    f"\n#601 = {filenum}\n",
                    f"#602 = {cycle}\n",
                    f"#603 = {blade}\n",
                    f"#604 = {marker_flag}\n",
                    f"#605 = {marker_only_flag}\n",
                    f"#606 = {special_tool_flag}\n",
                    f"#607 = {fix_file_flag}\n",
                    f"#608 = {manual_tool_change_flag}\n",
                    f"#609 = {stitched_flag}\n",
                    f"#610 = {balsa_flag}\n",
                    f"#611 = 0\n",
                    f"#612 = {flex_flag}\n",
                    f"#613 = {customer_rev}\n",
                    f"#614 = {acs_rev}\n",
                    f"#615 = {customer}\n\n"
                ]
                inserted = True
                continue

        new_lines.append(line)

    # Insert counter after M66 and before M30, only if not already present
    if not already_counted and m66_index != -1 and m30_index != -1 and m30_index > m66_index:
        increment_line = "P10320 = P10320 + 1\n\n" if controls == "FAGOR" else "#620 = #620 + 1\n\n"
        new_lines.insert(m30_index, increment_line)

    if not inserted and not already_encoded:
        print(f"[Encoding Adder][Warning] No encoding insertion point found in {path} — file may be incomplete or unconventional")

    if not new_lines or len(new_lines) < 5:
        print(f"[Encoding Adder][Warning] Refusing to overwrite {path} — too few lines remain")
        return

    write_new_lines(path, new_lines)
