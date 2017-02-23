# Parse seq files to get original optics path values.
import re

def read_seq(filename):
    """Read in a CODE V sequence file.

    :param filename: Filename for sequence file.
    :type filename: str

    Returns:
        List of strings, each element being a line in the .seq file. Newline
        characters are rstripped.
    """
    with open(filename, 'r') as f:
        content = f.readlines()

    content = [x.rstrip() for x in content]

    return content

def _find_start_end(content):
    """Given content, find start and end of surface definitions.

    :param content: Content of .seq file read with read_seq().
    :type content: list of str

    Returns:
        Tuple of (start, end) values for surfaces in content.
    """
    # Find start and end of surface definitions.
    close_to_end = False
    for i in range(len(content)):
        if re.search("^SO .+", content[i]):
            surface_start = i

        if close_to_end:
            if re.search("^  .+", content[i]):
                surface_end = i
            else:
                close_to_end = False

        # Subtle point, this should come after close_to_end search, else it just
        # sets back to False.
        if re.search("^SI .+", content[i]):
            close_to_end = True
    return (surface_start, surface_end)

def _find_all_surface_starts(content):
    """Find the index of each surface starting line.

    :param content: Content of .seq file read with read_seq().
    :type content: list of str

    Returns:
        List of ints which are the indicies for the start of each surface.
    """
    # Get the start of each surface.
    surface_start, surface_end = _find_start_end(content)
    surfaces = []
    for i in range(surface_start, surface_end):
        if re.search("^S.+", content[i]):
            surfaces.append(i)
    return surfaces

def _generate_raw_surf_dict(content):
    """Create a dictionary with the (start, end) value for each surface.

    :param content: Content of .seq file read with read_seq().
    :type content: list of str

    Returns:
        A dictionary with the surfaces numbers as keys and a tuple with (start,
        end) indicies as the values.
    """
    # Create dictionary with surface numbers as the key. The elements are then a
    # tuple of (start, end) values for the surface.
    surfaces = _find_all_surface_starts(content)
    surface_end = _find_start_end(content)[1]
    surface_start_stop_dict = {}
    for i in range(len(surfaces)):
        if i < len(surfaces)-1:
            surface_start_stop_dict[i] = (surfaces[i], surfaces[i+1]-1)
        else:
            surface_start_stop_dict[i] = (surfaces[i], surface_end)
    return surface_start_stop_dict

def parse_surface(content, surface):
    """Extract parameter values from a surface.

    :param seq_content: Content from reading in a .seq file with read_seq().
    :type seq_content: list of str
    :param surface: Surface to parse.
    :type surface: int
    :return: surface info dictionary
    :rtype: dict
    """
    surface_start_stop_dict = _generate_raw_surf_dict(content) # need to get surfaces automatically
    all_params = content[surface_start_stop_dict[surface][0]:surface_start_stop_dict[surface][1]+1]

    surface_info = {"Surface": surface}

    for param in all_params:
        decenter = False # set true if XDE or ADE lines exist
        if re.search("^  DAR", param):
            surface_info['Decenter Type'] = "DAR"
        elif re.search("^  REV", param):
            surface_info['Decenter Type'] = "REV"

        xyzde_search = re.search(r"^  XDE ([-\.0-9]+); YDE ([-\.0-9]+); ZDE ([-\.0-9]+)", param)
        if xyzde_search:
            surface_info["XDE"] = float(xyzde_search.group(1))
            surface_info["YDE"] = float(xyzde_search.group(2))
            surface_info["ZDE"] = float(xyzde_search.group(3))
            decenter = True

        abcde_search = re.search(r"^  ADE ([-\.0-9]+); BDE ([-\.0-9]+); CDE ([-\.0-9]+)", param)
        if abcde_search:
            surface_info["ADE"] = float(abcde_search.group(1))
            surface_info["BDE"] = float(abcde_search.group(2))
            surface_info["CDE"] = float(abcde_search.group(3))
            decenter = True

        if decenter and ('Decenter Type' not in surface_info.keys()):
            print "Basic Decenter"

    return surface_info


if __name__ == "__main__":
    seq_file = "ACTPol_150GHz_v28_optical_filter_aperture_study_20110809.seq"
    seq_file_contents = read_seq(seq_file)
    print parse_surface(seq_file_contents, 5)
