import os
import sys


def pre_process(baseDir, x1, x2, x3):
    """
    An utility function to pre-process the .comm input files by reading it
    and replacing the design variables(Length, Breadth and Thickness) values with
    the values provided by BOA

    PARAMS:
    baseDir - The path of the directory which holds the required input files
    x1 - Length
    x2 - Thickness
    x3 - Breadth

    RETURNS:
        This function returns the name of export file which is present
        in the baseDir which is required for simulation
    """

    cnt = 0

    # Getting the path of the required input files present in the baseDir
    for file in os.listdir(baseDir):
        if file.endswith(".comm"):
            cnt += 1
            comm_file = os.path.join(baseDir, file)
        elif file.endswith(".export"):
            cnt += 1
            export_file = file
        elif file.endswith(".mmed"):
            cnt += 1

    # Checking whether the base directory has all required input files
    if cnt < 3:
        raise FileNotFoundError("One or all required input files are missing "
                                "in the directory")
        sys.exit()

    # Opening the .comm file to pre-process the design variables
    fhc = open(comm_file, 'r+')
    data = fhc.readlines()

    # Loops to update all 3 design variables values
    # EP - thickness, LONG - Length, LARG - Breadth
    for i, v in enumerate(data):
        if 'EP' in v:
            data[i] = v.split('=')[0] + '= ' + str(x2) + '\n'
            break

    for i, v in enumerate(data):
        if 'LONG' in v:
            data[i] = v.split('=')[0] + '= ' + str(x1) + '\n'
            break

    for i, v in enumerate(data):
        if 'LARG' in v:
            data[i] = v.split('=')[0] + '= ' + str(x3) + '\n'
            break

    # Writing the new data to .comm file
    fhc.seek(0)
    fhc.truncate()
    fhc.writelines(data)
    fhc.close()

    return export_file


def post_process(baseDir):
    """
        An utility function to post-process the .resu result file to get
        the desired displacement value from file

        PARAMS:
        baseDir - The path of the directory which holds the output .resu file

        RETURNS:
            This function returns the displacement value for that epoch
        """

    # Getting the path of the output file created in the baseDir post simulation
    for file in os.listdir(baseDir):
        if file.endswith(".resu"):
            resu_file = os.path.join(baseDir, file)

    # Opening the .resu file to post-process the result to get the required
    # Displacement variable value
    fhc = open(resu_file, 'r')
    data = fhc.readlines()
    fhc.close()

    # Post processing the result
    y = data[198].split()[-1]

    # Delete the result file
    os.remove(resu_file)

    return float(y)
