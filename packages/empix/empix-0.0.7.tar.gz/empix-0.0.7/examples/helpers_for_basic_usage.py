"""This module contains helper functions for the Jupyter notebook located at
``<root>/examples/basic_usage.ipynb``, where ``<root>`` is the root of the
``empix`` repository.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For general array handling and constructing random number generators.
import numpy as np

# For creating hyperspy signals.
import hyperspy.signals
import hyperspy.axes



##################################
## Define classes and functions ##
##################################

# List of public objects in module.
__all__ = ["generate_real_2d_input_signal",
           "generate_complex_2d_input_signal",
           "generate_complex_2d_input_signal_data",
           "generate_complex_2d_input_signal_data_shape",
           "generate_complex_2d_input_signal_metadata",
           "generate_ring_centers_in_pixel_coords",
           "generate_complex_2d_input_signal_axes",
           "generate_real_1d_input_signal",
           "generate_complex_1d_input_signal",
           "generate_complex_1d_input_signal_data",
           "generate_complex_1d_input_signal_data_shape",
           "generate_complex_1d_input_signal_metadata",
           "generate_slopes",
           "generate_complex_1d_input_signal_axes"]



def generate_real_2d_input_signal():
    complex_2d_input_signal = generate_complex_2d_input_signal()
    
    real_2d_input_signal = complex_2d_input_signal.real
    real_2d_input_signal.metadata.General.title = "First Real 2D Input"
    real_2d_input_signal.metadata.max_imag_val_inside_ring = 0
    real_2d_input_signal.metadata.avg_imag_val_inside_ring = 0

    real_2d_input_signal.axes_manager[-2].name = "$x$"
    real_2d_input_signal.axes_manager[-2].units = "Å"

    real_2d_input_signal.axes_manager[-1].name = "$y$"
    real_2d_input_signal.axes_manager[-1].units = "Å"

    return real_2d_input_signal



def generate_complex_2d_input_signal():
    kwargs = {"data": generate_complex_2d_input_signal_data(), 
              "metadata": generate_complex_2d_input_signal_metadata()}
    complex_2d_input_signal = hyperspy.signals.ComplexSignal2D(**kwargs)

    axes = generate_complex_2d_input_signal_axes()

    for axis_idx, axis in enumerate(axes):
        complex_2d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_2d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_2d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_2d_input_signal



def generate_complex_2d_input_signal_data():
    signal_data_shape = generate_complex_2d_input_signal_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape

    metadata = generate_complex_2d_input_signal_metadata()
    ring_centers_in_pixel_coords = metadata["ring_centers_in_pixel_coords"]
    inner_ring_radius_in_pixels = metadata["inner_ring_radius_in_pixels"]
    outer_ring_radius_in_pixels = metadata["outer_ring_radius_in_pixels"]
    max_real_val_inside_ring = metadata["max_real_val_inside_ring"]
    max_imag_val_inside_ring = metadata["max_imag_val_inside_ring"]

    kwargs = {"shape": signal_data_shape, "dtype": "complex"}
    signal_data = np.zeros(**kwargs)

    navigation_dims = (Y_dim, X_dim)
    num_patterns = Y_dim*X_dim

    cols = np.arange(h_dim)
    rows = np.arange(v_dim)

    pair_of_1d_coord_arrays = (cols, rows)
    n_h, n_v = np.meshgrid(*pair_of_1d_coord_arrays, indexing="xy")

    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        Y_idx, X_idx = navigation_indices
        
        n_h_c, n_v_c = ring_centers_in_pixel_coords[Y_idx][X_idx]

        n_hv = np.sqrt((n_h-n_h_c)**2 + (n_v-n_v_c)**2)

        signal_data.real[navigation_indices] = \
            (inner_ring_radius_in_pixels <= n_hv)
        signal_data.real[navigation_indices] *= \
            (n_hv <= outer_ring_radius_in_pixels)
        signal_data.imag[navigation_indices] = \
            signal_data.real[navigation_indices]
        signal_data.real[*navigation_indices, :, n_h_c:] *= \
            max_real_val_inside_ring
        signal_data.imag[*navigation_indices, :, n_h_c:] *= \
            max_imag_val_inside_ring

    complex_2d_input_signal_data = signal_data

    return complex_2d_input_signal_data



def generate_complex_2d_input_signal_data_shape():
    complex_2d_input_signal_data_shape = (3, 2, 181, 200)
    
    return complex_2d_input_signal_data_shape



def generate_complex_2d_input_signal_metadata():
    axes = generate_complex_2d_input_signal_axes()
    h_offset = axes[-2].offset
    h_scale = axes[-2].scale
    v_offset = axes[-1].offset
    v_scale = axes[-1].scale

    ring_centers_in_pixel_coords = generate_ring_centers_in_pixel_coords()
    
    ring_centers = np.array(ring_centers_in_pixel_coords, dtype="float")
    ring_centers[:, :, 0] = h_offset + ring_centers[:, :, 0]*h_scale
    ring_centers[:, :, 1] = v_offset + ring_centers[:, :, 1]*v_scale
    ring_centers = ring_centers.tolist()

    inner_ring_radius_in_pixels = 50
    outer_ring_radius_in_pixels = 60
    inner_ring_radius = abs(h_scale)*inner_ring_radius_in_pixels
    outer_ring_radius = abs(h_scale)*outer_ring_radius_in_pixels

    max_real_val_inside_ring = 2
    max_imag_val_inside_ring = 3

    avg_real_val_inside_ring = (1+max_real_val_inside_ring)/2
    avg_imag_val_inside_ring = (1+max_imag_val_inside_ring)/2
    
    metadata = {"General": {"title": "First Complex 2D Input"}, 
                "Signal": dict(), 
                "ring_centers_in_pixel_coords": ring_centers_in_pixel_coords, 
                "ring_centers": ring_centers,
                "inner_ring_radius_in_pixels": inner_ring_radius_in_pixels, 
                "outer_ring_radius_in_pixels": outer_ring_radius_in_pixels, 
                "inner_ring_radius": inner_ring_radius, 
                "outer_ring_radius": outer_ring_radius, 
                "max_real_val_inside_ring": max_real_val_inside_ring,
                "max_imag_val_inside_ring": max_imag_val_inside_ring,
                "avg_real_val_inside_ring": avg_real_val_inside_ring, 
                "avg_imag_val_inside_ring": avg_imag_val_inside_ring}

    complex_2d_input_signal_metadata = metadata

    return complex_2d_input_signal_metadata



def generate_ring_centers_in_pixel_coords():
    signal_data_shape = generate_complex_2d_input_signal_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape
    
    ring_centers_in_pixel_coords = np.zeros((Y_dim, X_dim, 2), dtype="int")

    for Y_idx in range(Y_dim):
        for X_idx in range(X_dim):
            n_h_c = (h_dim-1)/2 + 10*(X_idx - (X_dim//2))
            n_v_c = (v_dim-1)/2 + 10*(Y_idx - (Y_dim//2))
            
            ring_centers_in_pixel_coords[Y_idx, X_idx, 0] = n_h_c
            ring_centers_in_pixel_coords[Y_idx, X_idx, 1] = n_v_c

    ring_centers_in_pixel_coords = ring_centers_in_pixel_coords.tolist()

    return ring_centers_in_pixel_coords



def generate_complex_2d_input_signal_axes():
    signal_data_shape = generate_complex_2d_input_signal_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape

    d_h = 0.1
    d_v = -d_h

    axes_sizes = (X_dim, Y_dim, h_dim, v_dim)
    axes_scales = (1, 7, d_h, d_v)
    axes_offsets = (11, 22, -((h_dim-1)//2)*d_h, ((v_dim-1)//2)*abs(d_v))
    axes_names = ("$X$", "$Y$", "$k_x$", "$k_y$")
    axes_units = ("mm", "mm", "1/Å", "1/Å")

    axes = tuple()
    for axis_idx, _ in enumerate(axes_names):
        kwargs = {"size": axes_sizes[axis_idx],
                  "scale": axes_scales[axis_idx],
                  "offset": axes_offsets[axis_idx],
                  "name": axes_names[axis_idx], 
                  "units": axes_units[axis_idx]}
        axis = hyperspy.axes.UniformDataAxis(**kwargs)
        axes += (axis,)

    complex_2d_input_signal_axes = axes

    return complex_2d_input_signal_axes



def generate_real_1d_input_signal():
    complex_1d_input_signal = generate_complex_1d_input_signal()
    
    real_1d_input_signal = complex_1d_input_signal.real
    real_1d_input_signal.metadata.General.title = "First Real 1D Input"
    real_1d_input_signal.metadata.y_intercept_of_imag_part = 0

    real_1d_input_signal.axes_manager[-1].name = "$r_{xy}$"
    real_1d_input_signal.axes_manager[-1].units = "Å"

    return real_1d_input_signal



def generate_complex_1d_input_signal():
    kwargs = {"data": generate_complex_1d_input_signal_data(), 
              "metadata": generate_complex_1d_input_signal_metadata()}
    complex_1d_input_signal = hyperspy.signals.ComplexSignal1D(**kwargs)

    axes = generate_complex_1d_input_signal_axes()

    for axis_idx, axis in enumerate(axes):
        complex_1d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_1d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_1d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_1d_input_signal



def generate_complex_1d_input_signal_data():
    signal_data_shape = generate_complex_1d_input_signal_data_shape()
    Y_dim, X_dim, u_dim = signal_data_shape

    metadata = generate_complex_1d_input_signal_metadata()
    slopes = metadata["slopes"]
    y_intercept_of_real_part = metadata["y_intercept_of_real_part"]
    y_intercept_of_imag_part = metadata["y_intercept_of_imag_part"]

    kwargs = {"shape": signal_data_shape, "dtype": "complex"}
    signal_data = np.zeros(**kwargs)

    navigation_dims = (Y_dim, X_dim)
    num_patterns = Y_dim*X_dim

    axes = generate_complex_1d_input_signal_axes()
    d_u = axes[-1].scale

    n_u = np.arange(u_dim)

    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        Y_idx, X_idx = navigation_indices

        u = n_u*d_u
        
        slope = slopes[Y_idx][X_idx]

        signal_data.real[navigation_indices] = (slope*u
                                                + y_intercept_of_real_part)
        signal_data.imag[navigation_indices] = (slope*u
                                                + y_intercept_of_imag_part)

    complex_1d_input_signal_data = signal_data

    return complex_1d_input_signal_data



def generate_complex_1d_input_signal_data_shape():
    complex_1d_input_signal_data_shape = (3, 2, 200)
    
    return complex_1d_input_signal_data_shape



def generate_complex_1d_input_signal_metadata():
    metadata = {"General": {"title": "First Complex 1D Input"}, 
                "Signal": dict(), 
                "slopes": generate_slopes(), 
                "y_intercept_of_real_part": 0,
                "y_intercept_of_imag_part": 10}

    complex_1d_input_signal_metadata = metadata

    return complex_1d_input_signal_metadata



def generate_slopes():
    signal_data_shape = generate_complex_1d_input_signal_data_shape()
    Y_dim, X_dim, r_dim = signal_data_shape
    
    slopes = np.zeros((Y_dim, X_dim))

    for Y_idx in range(Y_dim):
        for X_idx in range(X_dim):
            slopes[Y_idx, X_idx] = Y_idx*X_dim + X_idx

    slopes = slopes.tolist()

    return slopes



def generate_complex_1d_input_signal_axes():
    signal_data_shape = generate_complex_1d_input_signal_data_shape()
    Y_dim, X_dim, u_dim = signal_data_shape

    axes_sizes = (X_dim, Y_dim, u_dim)
    axes_scales = (1, 1, 0.1)
    axes_offsets = (0, 0, 0)
    axes_names = ("$X$", "$Y$", "$k_{xy}$")
    axes_units = ("mm", "mm", "1/Å")

    axes = tuple()
    for axis_idx, _ in enumerate(axes_names):
        kwargs = {"size": axes_sizes[axis_idx],
                  "scale": axes_scales[axis_idx],
                  "offset": axes_offsets[axis_idx],
                  "name": axes_names[axis_idx], 
                  "units": axes_units[axis_idx]}
        axis = hyperspy.axes.UniformDataAxis(**kwargs)
        axes += (axis,)

    complex_1d_input_signal_axes = axes

    return complex_1d_input_signal_axes



###########################
## Define error messages ##
###########################
