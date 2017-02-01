# codey.py
# Brian Koopman
# Contains all the methods required for processing data from CODEV to get it
# ready for use in fitting the detector positions and polarization angles.

# static copy (duh) - copied from codevpol repo on 2016-10-04 for get_fields method

import re
import numpy as np

# Field Definitions
# Returns the fields on the sky in CODEV.
def get_fields(pa):
    """Retrieve the fields input to CODEV, these are sky coordinates.

    Keyword arguments:
    pa -- Which optics tube you want fields for, PA1 or PA2.
    """
    ## PA1 - Zoom 3
    #pa1_fields = np.around(np.array([[0.625000,0.480000],
    #[0.456667,0.480000],
    #[0.625000,0.648333],
    #[0.793333,0.480000],
    #[0.625000,0.311667],
    #[0.288333,0.480000],
    #[0.386941,0.718059],
    #[0.625000,0.816667],
    #[0.863059,0.718059],
    #[0.961667,0.480000],
    #[0.863059,0.241941],
    #[0.625000,0.143333],
    #[0.386941,0.241941],
    #[0.120000,0.480000],
    #[0.187657,0.732500],
    #[0.372500,0.917343],
    #[0.625000,0.985000],
    #[0.877500,0.917343],
    #[1.06234,0.732500],
    #[1.13000,0.480000],
    #[1.06234,0.227500],
    #[0.877500,0.0426571],
    #[0.625000,-0.0250000],
    #[0.372500,0.0426571],
    #[0.187657,0.227500]]),4)

    # Added on 2014-12-08 when I realized my python script exports the fields in a different order for PA1 and PA2.
    pa1_fields = np.around(np.array([[ 0.625 ,  0.48  ],
    [ 0.7933,  0.48  ],
    [ 0.625 ,  0.6483],
    [ 0.4567,  0.48  ],
    [ 0.625 ,  0.3117],
    [ 0.9617,  0.48  ],
    [ 0.8631,  0.7181],
    [ 0.625 ,  0.8167],
    [ 0.3869,  0.7181],
    [ 0.2883,  0.48  ],
    [ 0.3869,  0.2419],
    [ 0.625 ,  0.1433],
    [ 0.8631,  0.2419],
    [ 1.13  ,  0.48  ],
    [ 1.0623,  0.7325],
    [ 0.8775,  0.9173],
    [ 0.625 ,  0.985 ],
    [ 0.3725,  0.9173],
    [ 0.1877,  0.7325],
    [ 0.12  ,  0.48  ],
    [ 0.1877,  0.2275],
    [ 0.3725,  0.0427],
    [ 0.625 , -0.025 ],
    [ 0.8775,  0.0427],
    [ 1.0623,  0.2275]]),4)
   
    # PA2 - Zoom 2
    pa2_fields = np.around(np.array([[-0.625000,0.480000],
    [-0.456667,0.480000],
    [-0.625000,0.648333],
    [-0.793333,0.480000],
    [-0.625000,0.311667],
    [-0.288333,0.480000],
    [-0.386941,0.718059],
    [-0.625000,0.816667],
    [-0.863059,0.718059],
    [-0.961667,0.480000],
    [-0.863059,0.241941],
    [-0.625000,0.143333],
    [-0.386941,0.241941],
    [-0.120000,0.480000],
    [-0.187657,0.732500],
    [-0.372500,0.917343],
    [-0.625000,0.985000],
    [-0.877500,0.917343],
    [-1.06234,0.732500],
    [-1.13000,0.480000],
    [-1.06234,0.227500],
    [-0.877500,0.0426571],
    [-0.625000,-0.0250000],
    [-0.372500,0.0426571],
    [-0.187657,0.227500]]),4)

    # Additional 24 fields that were generated to try and further constrain position fits.
    pa2_addition_24_fields = np.around(np.array([[-0.219     ,  0.48      ],
    [-0.27325971,  0.6825    ],
    [-0.4215    ,  0.83074029],
    [-0.624     ,  0.885     ],
    [-0.8265    ,  0.83074029],
    [-0.97474029,  0.6825    ],
    [-1.029     ,  0.48      ],
    [-0.97474029,  0.2775    ],
    [-0.8265    ,  0.12925971],
    [-0.624     ,  0.075     ],
    [-0.4215    ,  0.12925971],
    [-0.27325971,  0.2775    ],
    [-0.26691108,  0.83708892],
    [-0.49329638,  0.96779254],
    [-0.75470362,  0.96779254],
    [-0.98108892,  0.83708892],
    [-1.11179254,  0.61070362],
    [-1.11179254,  0.34929638],
    [-0.98108892,  0.12291108],
    [-0.75470362, -0.00779254],
    [-0.49329638, -0.00779254],
    [-0.26691108,  0.12291108],
    [-0.13620746,  0.34929638],
    [-0.13620746,  0.61070362]]),4)

    # pa3_fields, generated with generateFields.py with radius of 0.455
    pa3_fields = np.around(np.array([[0,   -0.75],
    [0.156667       , -0.75],
    [-6.84812e-009  , -0.570333],
    [-0.156667      , -0.75],
    [1.86823e-009   , -0.929667],
    [0.313333       , -0.75],
    [0.22156        , -0.495913],
    [-1.36962e-008  , -0.390667],
    [-0.22156       , -0.495913],
    [-0.313333      , -0.75],
    [-0.22156       , -1.00409],
    [3.73646e-009   , -1.10933],
    [0.22156        , -1.00409],
    [0.47           , -0.75],
    [0.407032       , -0.4805],
    [0.235          , -0.283212],
    [-2.05444e-008  , -0.211],
    [-0.235         , -0.283212],
    [-0.407032      , -0.4805],
    [-0.47          , -0.75],
    [-0.407032      , -1.0195],
    [-0.235         , -1.21679],
    [5.60469e-009   , -1.289],
    [0.235          , -1.21679],
    [0.407032       , -1.0195]]),4)


    if pa in [1, 4]:
        return pa1_fields
    elif pa == 2:
        return pa2_fields
    elif pa == -2:
        return pa2_addition_24_fields
    elif pa == 3:
        return pa3_fields
    else:
        raise ValueError("Please pick either PA1 (1), PA2 (2), or PA3 (3).")

# Position Information
# Extracts position information from CODEV output files.
def get_trace(log_file):
    """Reads and returns ray trace positions on the focal plane given a log file.

    Keyword agruments:
    log_file -- Location of an unmodified .txt file from CODEV containing
               information from an RSI command.
    """
    read_data = []
    with open(log_file, 'r') as f:
        for line in f:
            if line.rstrip():
                read_data.append(line)
    f.close()
    
    process_data = np.zeros((25,2))
    for i in range(len(read_data)):
        # This regex will match for RSI lines. 
        # m.group(0) is the entire line.
        # m.group(1) should be 'RSI'
        # m.group(2) should be the Field number.
        m = re.search('(RSI)[A-Z, 0-9]+F([0-9]+)', read_data[i])
        # This regex will match for IMG lines. 
        # n.group(0) is the entire line.
        # n.group(1) should be 'IMG'
        # n.group(2) should be X
        # n.group(3) should be Y
        n = re.search('(IMG)[ ]+(.[0-9].[0-9]+)[ ]+(.[0-9].[0-9]+)', read_data[i])
        if m is not None:
            if m.group(1) == 'RSI':
                field = int(m.group(2))-1
        if n is not None:
            if n.group(1) == 'IMG':
                process_data[field][0] = float(n.group(2)) #X
                process_data[field][1] = float(n.group(3)) #Y

    return process_data

def get_psf(log_file):
    """Reads and returns psf position offsets on the focal plane given a log file.

    Keyword agruments:
    log_file -- Location of an unmodified .txt file from CODEV containing
               information from a psf analysis.
    """
    read_data = []
    with open(log_file, 'r') as f:
        for line in f:
            if line.rstrip():
                read_data.append(line)
    f.close()
    
    process_data = np.zeros((25,2))
    field = 0
    for i in range(len(read_data)):
        try:
            if read_data[i].strip().split()[0] == 'relative':
                process_data[field][0] = float(read_data[i].strip().split()[4]) #X
                process_data[field][1] = float(read_data[i].strip().split()[5]) #Y
                field+=1
        except IndexError:
            print "Index Error, probably have blank lines somehow."

    return process_data

def get_positions(data_dir,trace_file,psf_file):
    """Runs the get_trace and get_psf functions to return final focal plane positions.
    
    The returned array assumes you will never have a 0,0 position, if you do
    end up with a 0,0 position, it's not going to get returned here. I'm
    assuming this because it's unlikely we'll get a perfect 0,0. If you do have
    one, you're returned array size will of course be smaller than you'd expect.

    Keyword agruments:
    data_dir -- Location of the directory used to store the data files.
    trace_file -- Location of the ray trace log file within the data_dir.
    psf_file -- Location of the psf log file within the data_dir.
    """
    trace = get_trace(data_dir + trace_file)
    psf = get_psf(data_dir + psf_file)

    c = np.around(trace+psf,4) #round
    # The return statement returns all focal plane positions that aren't 0,0
    return c[c[:,0].nonzero() and c[:,1].nonzero()]

# Position Information
# Extracts position information from CODEV output files.
def get_pol(data_file):
    """Reads a polarization text file.

    Keyword arguments:
    data_file -- Unmodified data file containing text output from CODEV's poldsp macro.
                 Note that this should be the "FULL" output in CODEV.
    """
    # TODO: write regex to determine size of header and footer dynamically?
    return np.genfromtxt(data_file, skip_header=15,skip_footer=37)

def math_fix(angle,data):
    """Fix the strange math that happens in the poldsp macro from CODEV.

    This module is based on the original mathfix.m MATLAB script, which was
    worked out long ago. It operates on the assumption that what was done there
    to fix the strange math was correct.

    Keyword arguments:
    angle -- The input polarization angle used when the data was gathered in
             CODEV, supported angles are 0, 90, -45
    data -- Data array, not yet split, generated from get_pol(data_file)
    """
    if angle == 0:
        for i in range(len(data)):
            # Corrects angle for Zero Deg Input
            if data[i,4] < -70:
                data[i,4] = data[i,4] + 90
            # Corrects magnitude signs
            if data[i,5] < 0:
                data[i,5] = data[i,5]*(-1)
    elif angle == 90:
        for i in range(len(data)):
            # Corrects angle for Ninety Deg Input
            if data[i,4] < -170:
                data[i,4] = data[i,4] + 180
            # Corrects magnitude signs
            if data[i,5] < 0:
                data[i,5] = data[i,5]*(-1)
    elif angle == -45:
        for i in range(len(data)):
            # Corrects angle for -45 Deg Input
            data[i,4] = data[i,4] + 90
            # Corrects magnitude signs
            if data[i,5] < 0:
                data[i,5] = data[i,5]*(-1)
    else:
        raise ValueError("Input polarization angle not supported, please refer to the documentation and try again.")

    return data

def get_angles(data_dir,data_file,input_angle):
    """Get the polarization angle averages from CODEV output.

    Keyword arguments:
    data_dir -- directory with data_file for reading in CODEV output
    data_file -- CODEV output file, likely from automated running of CODEV
    input_angle -- CODEV polarization input angle, required for math_fix to run properly

    Returns:
    (N,1) sized np.array with average angles across the pupil for each field. N
    is likely 25."""
    # Read in data and fix angles and magnitudes.
    a = math_fix(input_angle,get_pol(data_dir + data_file))
    
    #Split on fields.
    split_at = a[:,0].searchsorted(range(2,26))
    b = np.split(a,split_at)
    
    # Take the averages.
    b_mean = []
    for i in range(len(b)):
        b_mean.append(np.mean(b[i],axis=0))
    
    b_mean = np.array(b_mean)
    
    return np.array([np.around(b_mean[:,4],4)]).T
