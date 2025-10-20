# -*- coding: utf-8 -*-
# Copyright 2024 Matthew Fitzpatrick.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
r"""Contains tests for the root of the package :mod:`empix`.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For operations related to unit tests.
import pytest

# For general array handling.
import numpy as np

# For creating hyperspy signals.
import hyperspy.signals
import hyperspy.axes

# For downsampling hyperspy signals.
import skimage.measure



# For analyzing electron microscopy data.
import empix



##################################
## Define classes and functions ##
##################################



@pytest.fixture
def real_2d_input_signal_1():
    fixture_output = generate_real_2d_input_signal_1()

    return fixture_output



def generate_real_2d_input_signal_1():
    complex_2d_input_signal_1 = generate_complex_2d_input_signal_1()
    
    real_2d_input_signal = complex_2d_input_signal_1.real
    real_2d_input_signal.metadata.General.title = "First Real 2D Input"
    real_2d_input_signal.metadata.max_imag_val_inside_ring = 0
    real_2d_input_signal.metadata.avg_imag_val_inside_ring = 0

    real_2d_input_signal.axes_manager[-2].name = "$x$"
    real_2d_input_signal.axes_manager[-2].units = "Å"

    real_2d_input_signal.axes_manager[-1].name = "$y$"
    real_2d_input_signal.axes_manager[-1].units = "Å"

    return real_2d_input_signal



def generate_complex_2d_input_signal_1():
    kwargs = {"data": generate_complex_2d_input_signal_1_data(), 
              "metadata": generate_complex_2d_input_signal_1_metadata()}
    complex_2d_input_signal = hyperspy.signals.ComplexSignal2D(**kwargs)

    axes = generate_complex_2d_input_signal_1_axes()

    for axis_idx, axis in enumerate(axes):
        complex_2d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_2d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_2d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_2d_input_signal



def generate_complex_2d_input_signal_1_data():
    signal_data_shape = generate_complex_2d_input_signal_1_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape

    metadata = generate_complex_2d_input_signal_1_metadata()
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
        signal_data.real[Y_idx, X_idx, :, n_h_c:] *= \
            max_real_val_inside_ring
        signal_data.imag[Y_idx, X_idx, :, n_h_c:] *= \
            max_imag_val_inside_ring

    complex_2d_input_signal_1_data = signal_data

    return complex_2d_input_signal_1_data



def generate_complex_2d_input_signal_1_data_shape():
    complex_2d_input_signal_1_data_shape = (3, 2, 181, 200)
    
    return complex_2d_input_signal_1_data_shape



def generate_complex_2d_input_signal_1_metadata():
    axes = generate_complex_2d_input_signal_1_axes()
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

    complex_2d_input_signal_1_metadata = metadata

    return complex_2d_input_signal_1_metadata



def generate_ring_centers_in_pixel_coords():
    signal_data_shape = generate_complex_2d_input_signal_1_data_shape()
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



def generate_complex_2d_input_signal_1_axes():
    signal_data_shape = generate_complex_2d_input_signal_1_data_shape()
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

    complex_2d_input_signal_1_axes = axes

    return complex_2d_input_signal_1_axes



@pytest.fixture
def complex_2d_input_signal_1():
    fixture_output = generate_complex_2d_input_signal_1()

    return fixture_output



@pytest.fixture
def real_1d_input_signal_1():
    fixture_output = generate_real_1d_input_signal_1()

    return fixture_output



def generate_real_1d_input_signal_1():
    complex_1d_input_signal_1 = generate_complex_1d_input_signal_1()
    
    real_1d_input_signal = complex_1d_input_signal_1.real
    real_1d_input_signal.metadata.General.title = "First Real 1D Input"
    real_1d_input_signal.metadata.y_intercept_of_imag_part = 0

    real_1d_input_signal.axes_manager[-1].name = "$r_{xy}$"
    real_1d_input_signal.axes_manager[-1].units = "Å"

    return real_1d_input_signal



def generate_complex_1d_input_signal_1():
    kwargs = {"data": generate_complex_1d_input_signal_1_data(), 
              "metadata": generate_complex_1d_input_signal_1_metadata()}
    complex_1d_input_signal = hyperspy.signals.ComplexSignal1D(**kwargs)

    axes = generate_complex_1d_input_signal_1_axes()

    for axis_idx, axis in enumerate(axes):
        complex_1d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_1d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_1d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_1d_input_signal



def generate_complex_1d_input_signal_1_data():
    signal_data_shape = generate_complex_1d_input_signal_1_data_shape()
    Y_dim, X_dim, u_dim = signal_data_shape

    metadata = generate_complex_1d_input_signal_1_metadata()
    slopes = metadata["slopes"]
    y_intercept_of_real_part = metadata["y_intercept_of_real_part"]
    y_intercept_of_imag_part = metadata["y_intercept_of_imag_part"]

    kwargs = {"shape": signal_data_shape, "dtype": "complex"}
    signal_data = np.zeros(**kwargs)

    navigation_dims = (Y_dim, X_dim)
    num_patterns = Y_dim*X_dim

    axes = generate_complex_1d_input_signal_1_axes()
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

    complex_1d_input_signal_1_data = signal_data

    return complex_1d_input_signal_1_data



def generate_complex_1d_input_signal_1_data_shape():
    complex_1d_input_signal_1_data_shape = (3, 2, 200)
    
    return complex_1d_input_signal_1_data_shape



def generate_complex_1d_input_signal_1_metadata():
    metadata = {"General": {"title": "First Complex 1D Input"}, 
                "Signal": dict(), 
                "slopes": generate_slopes(), 
                "y_intercept_of_real_part": 0,
                "y_intercept_of_imag_part": 10}

    complex_1d_input_signal_1_metadata = metadata

    return complex_1d_input_signal_1_metadata



def generate_slopes():
    signal_data_shape = generate_complex_1d_input_signal_1_data_shape()
    Y_dim, X_dim, r_dim = signal_data_shape
    
    slopes = np.zeros((Y_dim, X_dim))

    for Y_idx in range(Y_dim):
        for X_idx in range(X_dim):
            slopes[Y_idx, X_idx] = Y_idx*X_dim + X_idx

    slopes = slopes.tolist()

    return slopes



def generate_complex_1d_input_signal_1_axes():
    signal_data_shape = generate_complex_1d_input_signal_1_data_shape()
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

    complex_1d_input_signal_1_axes = axes

    return complex_1d_input_signal_1_axes



@pytest.fixture
def complex_1d_input_signal_1():
    fixture_output = generate_complex_1d_input_signal_1()

    return fixture_output



@pytest.fixture
def real_2d_input_signal_2():
    fixture_output = generate_real_2d_input_signal_2()

    return fixture_output



def generate_real_2d_input_signal_2():
    complex_2d_input_signal_2 = generate_complex_2d_input_signal_2()
    
    real_2d_input_signal = complex_2d_input_signal_2.real

    path_to_item = "General.title"
    real_2d_input_signal.metadata.set_item(path_to_item, 
                                           "Second Real 2D Input")

    path_to_item = "imag_val_inside_imaged_part_of_rectangular_image_subject"
    real_2d_input_signal.metadata.set_item(path_to_item, 0)

    path_to_item = "imag_val_outside_imaged_part_of_rectangular_image_subject"
    real_2d_input_signal.metadata.set_item(path_to_item, 0)

    real_2d_input_signal.axes_manager[-2].name = "$x$"
    real_2d_input_signal.axes_manager[-2].units = "Å"

    real_2d_input_signal.axes_manager[-1].name = "$y$"
    real_2d_input_signal.axes_manager[-1].units = "Å"

    return real_2d_input_signal



def generate_complex_2d_input_signal_2():
    kwargs = {"data": generate_complex_2d_input_signal_2_data(), 
              "metadata": generate_complex_2d_input_signal_2_metadata()}
    complex_2d_input_signal = hyperspy.signals.ComplexSignal2D(**kwargs)

    axes = generate_complex_2d_input_signal_2_axes()

    for axis_idx, axis in enumerate(axes):
        complex_2d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_2d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_2d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_2d_input_signal



def generate_complex_2d_input_signal_2_data():
    signal_data_shape = generate_complex_2d_input_signal_2_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape

    metadata = \
        generate_complex_2d_input_signal_2_metadata()
    frames_of_entire_rectangular_image_subjects = \
        metadata["frames_of_entire_rectangular_image_subjects"]
    real_val_inside_imaged_part_of_rectangular_image_subject = \
        metadata["real_val_inside_imaged_part_of_rectangular_image_subject"]
    imag_val_inside_imaged_part_of_rectangular_image_subject = \
        metadata["imag_val_inside_imaged_part_of_rectangular_image_subject"]
    real_val_outside_imaged_part_of_rectangular_image_subject = \
        metadata["real_val_outside_imaged_part_of_rectangular_image_subject"]
    imag_val_outside_imaged_part_of_rectangular_image_subject = \
        metadata["imag_val_outside_imaged_part_of_rectangular_image_subject"]

    kwargs = {"shape": signal_data_shape, "dtype": "complex"}
    signal_data = np.ones(**kwargs)

    signal_data[:] = \
        (real_val_outside_imaged_part_of_rectangular_image_subject
         + 1j*imag_val_outside_imaged_part_of_rectangular_image_subject)

    navigation_dims = (Y_dim, X_dim)
    num_patterns = Y_dim*X_dim

    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        Y_idx, X_idx = navigation_indices

        L, R, B, T = frames_of_entire_rectangular_image_subjects[Y_idx][X_idx]

        signal_data[Y_idx, X_idx, 0:(v_dim-B)-T, 0:(h_dim-R)-L] = \
            (real_val_inside_imaged_part_of_rectangular_image_subject
             + 1j*imag_val_inside_imaged_part_of_rectangular_image_subject)

        kwargs = {"a": signal_data[Y_idx, X_idx], 
                  "indices": np.arange(-T, -T+v_dim), 
                  "axis": 0, 
                  "mode": "wrap"}
        signal_data[Y_idx, X_idx] = np.take(**kwargs)

        kwargs["indices"] = np.arange(-L, -L+h_dim)
        kwargs["axis"] = 1
        signal_data[Y_idx, X_idx] = np.take(**kwargs)

    complex_2d_input_signal_2_data = signal_data

    return complex_2d_input_signal_2_data



def generate_complex_2d_input_signal_2_data_shape():
    _, _, v_dim, h_dim = generate_complex_2d_input_signal_1_data_shape()

    frames_of_entire_rectangular_image_subjects = \
        np.array(generate_frames_of_entire_rectangular_image_subjects())

    Y_dim = frames_of_entire_rectangular_image_subjects.shape[0]
    X_dim = frames_of_entire_rectangular_image_subjects.shape[1]
    
    complex_2d_input_signal_2_data_shape = (Y_dim, X_dim, v_dim, h_dim)
    
    return complex_2d_input_signal_2_data_shape



def generate_frames_of_entire_rectangular_image_subjects():
    _, _, v_dim, h_dim = generate_complex_2d_input_signal_1_data_shape()
    
    frames_of_entire_rectangular_image_subjects = \
        (((-5, h_dim-15, v_dim-6, -7), 
          (h_dim-5, -16, v_dim-6, -8)),
         ((-5, h_dim-15, v_dim-102, 85), 
          (h_dim-5, -16, v_dim-110, 87)),
         ((-5, h_dim-15, -15, v_dim-5), 
          (h_dim-5, -16, -5, v_dim-15)),
         ((100, h_dim-140, v_dim-21, -9), 
          (98, h_dim-129, -15, v_dim-13)), 
         ((30, h_dim-70, v_dim-150, 110), 
          (110, h_dim-140, v_dim-72, 35)),
         ((-5, -11, v_dim-151, 111), 
          (68, h_dim-137, -7, -21)), 
         ((-9, -18, -6, -4), 
          (61, h_dim-88, v_dim-170, 144)))

    return frames_of_entire_rectangular_image_subjects



def generate_complex_2d_input_signal_2_metadata():
    frames_of_entire_rectangular_image_subjects = \
        generate_frames_of_entire_rectangular_image_subjects()
    frames_of_imaged_parts_of_rectangular_image_subjects = \
        generate_frames_of_imaged_parts_of_rectangular_image_subjects()
    
    metadata = {"General": \
                {"title": "Second Complex 2D Input"}, 
                "Signal": \
                dict(), 
                "frames_of_entire_rectangular_image_subjects": \
                frames_of_entire_rectangular_image_subjects, 
                "frames_of_imaged_parts_of_rectangular_image_subjects": \
                frames_of_imaged_parts_of_rectangular_image_subjects, 
                "real_val_inside_imaged_part_of_rectangular_image_subject": \
                3,
                "imag_val_inside_imaged_part_of_rectangular_image_subject": \
                4,
                "real_val_outside_imaged_part_of_rectangular_image_subject": \
                1,
                "imag_val_outside_imaged_part_of_rectangular_image_subject": \
                2}

    complex_2d_input_signal_2_metadata = metadata

    return complex_2d_input_signal_2_metadata



def generate_frames_of_imaged_parts_of_rectangular_image_subjects():
    clipped_frames = \
        np.array(generate_frames_of_entire_rectangular_image_subjects())
    clipped_frames[:, :, 0] = \
        clipped_frames[:, :, 0].clip(min=0)
    clipped_frames[:, :, 1] = \
        clipped_frames[:, :, 1].clip(min=0)
    clipped_frames[:, :, 2] = \
        clipped_frames[:, :, 2].clip(min=0)
    clipped_frames[:, :, 3] = \
        clipped_frames[:, :, 3].clip(min=0)
    
    frames_of_imaged_parts_of_rectangular_image_subjects = \
        clipped_frames.tolist()

    return frames_of_imaged_parts_of_rectangular_image_subjects



def generate_complex_2d_input_signal_2_axes():
    signal_data_shape = generate_complex_2d_input_signal_2_data_shape()
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

    complex_2d_input_signal_2_axes = axes

    return complex_2d_input_signal_2_axes



@pytest.fixture
def complex_2d_input_signal_2():
    fixture_output = generate_complex_2d_input_signal_2()

    return fixture_output



@pytest.fixture
def real_2d_input_signal_3():
    fixture_output = generate_real_2d_input_signal_3()

    return fixture_output



def generate_real_2d_input_signal_3():
    complex_2d_input_signal_3 = generate_complex_2d_input_signal_3()
    
    real_2d_input_signal = complex_2d_input_signal_3.real

    path_to_item = "General.title"
    real_2d_input_signal.metadata.set_item(path_to_item, 
                                           "Third Real 2D Input")

    path_to_item = "imag_val_of_const_bg"
    real_2d_input_signal.metadata.set_item(path_to_item, 0)

    path_to_item = "imag_val_of_peak_amplitude"
    real_2d_input_signal.metadata.set_item(path_to_item, 0)

    real_2d_input_signal.axes_manager[-2].name = "$x$"
    real_2d_input_signal.axes_manager[-2].units = "Å"

    real_2d_input_signal.axes_manager[-1].name = "$y$"
    real_2d_input_signal.axes_manager[-1].units = "Å"

    return real_2d_input_signal



def generate_complex_2d_input_signal_3():
    kwargs = {"data": generate_complex_2d_input_signal_3_data(), 
              "metadata": generate_complex_2d_input_signal_3_metadata()}
    complex_2d_input_signal = hyperspy.signals.ComplexSignal2D(**kwargs)

    axes = generate_complex_2d_input_signal_3_axes()

    for axis_idx, axis in enumerate(axes):
        complex_2d_input_signal.axes_manager[axis_idx].update_from(axis)
        complex_2d_input_signal.axes_manager[axis_idx].name = axis.name
        complex_2d_input_signal.axes_manager[axis_idx].units = axis.units

    return complex_2d_input_signal



def generate_complex_2d_input_signal_3_data():
    signal_data_shape = generate_complex_2d_input_signal_3_data_shape()
    Y_dim, X_dim, v_dim, h_dim = signal_data_shape

    metadata = generate_complex_2d_input_signal_3_metadata()
    real_val_of_const_bg = metadata["real_val_of_const_bg"]
    imag_val_of_const_bg = metadata["imag_val_of_const_bg"]
    A_real = metadata["real_val_of_peak_amplitude"]
    A_imag = metadata["imag_val_of_peak_amplitude"]
    sigma = metadata["peak_width_in_pixels"]
    peak_centers_in_pixel_coords = metadata["peak_centers_in_pixel_coords"]

    kwargs = {"shape": signal_data_shape, "dtype": "complex"}
    signal_data = np.ones(**kwargs)

    signal_data[:] = real_val_of_const_bg + 1j*imag_val_of_const_bg

    navigation_dims = (Y_dim, X_dim)
    num_patterns = Y_dim*X_dim

    cols = np.arange(h_dim)
    rows = np.arange(v_dim)

    pair_of_1d_coord_arrays = (cols, rows)
    n_h, n_v = np.meshgrid(*pair_of_1d_coord_arrays, indexing="xy")

    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        Y_idx, X_idx = navigation_indices
        
        n_h_c, n_v_c = peak_centers_in_pixel_coords[Y_idx][X_idx]

        n_hv_sq = (n_h-n_h_c)**2 + (n_v-n_v_c)**2
        sigma_sq = sigma*sigma

        signal_data[Y_idx, X_idx] += \
            (A_real*np.exp(-n_hv_sq / (2*sigma_sq))
             + 1j*A_imag*np.exp(-n_hv_sq / (2*sigma_sq)))

    complex_2d_input_signal_3_data = signal_data

    return complex_2d_input_signal_3_data



def generate_complex_2d_input_signal_3_data_shape():
    complex_2d_input_signal_3_data_shape = \
        generate_complex_2d_input_signal_1_data_shape()
    
    return complex_2d_input_signal_3_data_shape



def generate_complex_2d_input_signal_3_metadata():
    peak_centers_in_pixel_coords = generate_peak_centers_in_pixel_coords()
    
    metadata = {"General": {"title": "Third Complex 2D Input"}, 
                "Signal": dict(), 
                "real_val_of_const_bg":0, 
                "imag_val_of_const_bg": 1, 
                "real_val_of_peak_amplitude": 2,
                "imag_val_of_peak_amplitude": 1,
                "peak_width_in_pixels": 50,
                "peak_centers_in_pixel_coords": peak_centers_in_pixel_coords}

    complex_2d_input_signal_3_metadata = metadata

    return complex_2d_input_signal_3_metadata



def generate_peak_centers_in_pixel_coords():
    peak_centers_in_pixel_coords = generate_ring_centers_in_pixel_coords()

    return peak_centers_in_pixel_coords



def generate_complex_2d_input_signal_3_axes():
    complex_2d_input_signal_3_axes = \
        generate_complex_2d_input_signal_1_axes()

    return complex_2d_input_signal_3_axes



@pytest.fixture
def complex_2d_input_signal_3():
    fixture_output = generate_complex_2d_input_signal_3()

    return fixture_output



def test_1_of_abs_sq(real_2d_input_signal_1, 
                     complex_2d_input_signal_1, 
                     real_1d_input_signal_1, 
                     complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        kwargs = {"input_signal": input_signal_candidate, "title": None}
        if input_signal_candidate is None:
            with pytest.raises(TypeError) as err_info:
                empix.abs_sq(**kwargs)
        else:
            output_signal = empix.abs_sq(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Modulus Squared of " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            tol = 1e-10
            expected_output_signal_data = np.abs(input_signal_candidate.data)**2
            abs_diff = np.abs(output_signal.data-expected_output_signal_data)
            assert np.sum(abs_diff) < tol

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_abs_sq(**kwargs)

    return None



def check_metadata(input_signal, output_signal):
    input_signal_metadata_excluding_title_as_dict = \
        input_signal.metadata.as_dictionary()
    output_signal_metadata_excluding_title_as_dict = \
        output_signal.metadata.as_dictionary()

    key_1 = "General"
    key_2 = "title"
    del input_signal_metadata_excluding_title_as_dict[key_1][key_2]
    del output_signal_metadata_excluding_title_as_dict[key_1][key_2]

    dict_1 = input_signal_metadata_excluding_title_as_dict
    dict_2 = output_signal_metadata_excluding_title_as_dict

    assert (dict_1 == dict_2)

    return None



def check_axes_after_applying_abs_sq(input_signal, 
                                     output_signal):
    num_axes = len(input_signal.data.shape)
    for axis_idx in range(num_axes):
        axis_of_input_signal = input_signal.axes_manager[axis_idx]
        axis_of_output_signal = output_signal.axes_manager[axis_idx]

        assert (axis_of_input_signal.size == axis_of_output_signal.size)
        assert (axis_of_input_signal.scale == axis_of_output_signal.scale)
        assert (axis_of_input_signal.offset == axis_of_output_signal.offset)
        assert (axis_of_input_signal.units == axis_of_output_signal.units)
        assert (axis_of_input_signal.name == axis_of_output_signal.name)
    
    return None



def test_2_of_abs_sq(real_2d_input_signal_1):
    kwargs = {"input_signal": real_2d_input_signal_1, "title": "foobar"}
    output_signal = empix.abs_sq(**kwargs)
    
    title = output_signal.metadata.General.title
    expected_title = kwargs["title"]
    assert (title == expected_title)

    kwargs["title"] = slice(None)
    with pytest.raises(TypeError) as err_info:
        empix.abs_sq(**kwargs)

    return None



def test_1_of_OptionalAzimuthalAveragingParams():
    cls_alias = empix.OptionalAzimuthalAveragingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"center": (10, 9),
              "radial_range": (0.1, 0.3),
              "num_bins": 10}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = (10, 9)
        kwargs["radial_range"] = (-0.1, 0.3)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["radial_range"] = (0.3, 0.1)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["radial_range"] = (0.1, 0.3)
        kwargs["num_bins"] = 0
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_azimuthally_average(real_2d_input_signal_1, 
                                  complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius
        avg_real_val_inside_ring = metadata.avg_real_val_inside_ring
        avg_imag_val_inside_ring = metadata.avg_imag_val_inside_ring

        radial_range = (inner_ring_radius/2, outer_ring_radius+1)
        num_bins = 180

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAzimuthalAveragingParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range, 
                          "num_bins": num_bins}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.azimuthally_average(**kwargs)

                u = (inner_ring_radius + outer_ring_radius)/2
                expected_data_elem_val = avg_real_val_inside_ring
                if np.iscomplexobj(output_signal.data):
                    expected_data_elem_val += 1j*avg_imag_val_inside_ring

                kwargs = {"output_signal": output_signal, 
                          "Y_idx": Y_idx,
                          "X_idx": X_idx,
                          "u": u,
                          "expected_data_elem_val": expected_data_elem_val}
                check_1d_output_signal_data_elem(**kwargs)

                kwargs["u"] = inner_ring_radius / 2
                kwargs["expected_data_elem_val"] *= 0
                check_1d_output_signal_data_elem(**kwargs)

    return None



def check_1d_output_signal_data_elem(output_signal, 
                                     Y_idx, 
                                     X_idx, 
                                     u,
                                     expected_data_elem_val):
    u_scale = output_signal.axes_manager[-1].scale
    u_offset = output_signal.axes_manager[-1].offset
    n_u = round((u-u_offset) / u_scale)

    tol = 1e-2

    if np.isrealobj(output_signal.data):
        data_elem = output_signal.data[Y_idx, X_idx, n_u].item()

        if expected_data_elem_val != 0:
            rel_diff = (abs(data_elem-expected_data_elem_val) 
                        / expected_data_elem_val)
            assert (rel_diff < tol)
        else:
            abs_diff = abs(data_elem-expected_data_elem_val)
            assert (abs_diff < tol)
    else:
        data_elem = output_signal.data[Y_idx, X_idx, n_u].item()

        if expected_data_elem_val.real != 0:
            rel_diff = (abs(data_elem.real-expected_data_elem_val.real) 
                        / abs(expected_data_elem_val.real))
            assert (rel_diff < tol)
        else:
            abs_diff = abs(data_elem.real-expected_data_elem_val.real)
            assert (abs_diff < tol)

        if expected_data_elem_val.imag != 0:
            rel_diff = (abs(data_elem.imag-expected_data_elem_val.imag) 
                        / abs(expected_data_elem_val.imag))
            assert (rel_diff < tol)
        else:
            abs_diff = abs(data_elem.imag-expected_data_elem_val.imag)
            assert (abs_diff < tol)

    return None



def test_2_of_azimuthally_average(real_2d_input_signal_1, 
                                  complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius

        radial_range = (inner_ring_radius/2, outer_ring_radius+1)
        num_bins = 180

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAzimuthalAveragingParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range, 
                          "num_bins": num_bins}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.azimuthally_average(**kwargs)

                u_size = output_signal.axes_manager[-1].size
                u_scale = output_signal.axes_manager[-1].scale
                u_offset = output_signal.axes_manager[-1].offset

                assert (num_bins == u_size)

                tol = 1e-2

                n_u_set = (0, u_size-1)
                expected_u_set = radial_range
                zip_obj = zip(n_u_set, expected_u_set)

                for n_u, expected_u in zip_obj:
                    u = u_offset + n_u*u_scale
                    rel_diff = abs(u-expected_u) / expected_u
                    assert (rel_diff < tol)

    return None



def test_3_of_azimuthally_average(real_2d_input_signal_1, 
                                  complex_2d_input_signal_1, 
                                  real_1d_input_signal_1, 
                                  complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.azimuthally_average(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Azimuthally Averaged " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_azimuthally_average(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.azimuthally_average(**kwargs)

    return None



def check_axes_after_applying_azimuthally_average(input_signal, 
                                                  output_signal):
    kwargs = locals()
    check_axes_after_applying_azimuthally_integrate(**kwargs)

    return None



def check_axes_after_applying_azimuthally_integrate(input_signal, 
                                                    output_signal):
    check_navigation_space_axes(input_signal, output_signal)

    input_u_units = input_signal.axes_manager[-1].units
    output_u_units = output_signal.axes_manager[-1].units

    output_u_name = output_signal.axes_manager[-1].name

    expected_output_u_units = input_u_units

    if input_u_units == "Å":
        expected_output_u_name = "$r_{xy}$"
    else:
        expected_output_u_name = "$k_{xy}$"

    assert (output_u_name == expected_output_u_name)
    assert (output_u_units == expected_output_u_units)

    return None



def check_navigation_space_axes(input_signal, 
                                output_signal):
    num_navigation_space_axes = len(input_signal.data.shape[:-2])
    for axis_idx in range(num_navigation_space_axes):
        axis_of_input_signal = input_signal.axes_manager[axis_idx]
        axis_of_output_signal = output_signal.axes_manager[axis_idx]

        assert (axis_of_input_signal.size == axis_of_output_signal.size)
        assert (axis_of_input_signal.scale == axis_of_output_signal.scale)
        assert (axis_of_input_signal.offset == axis_of_output_signal.offset)
        assert (axis_of_input_signal.units == axis_of_output_signal.units)
        assert (axis_of_input_signal.name == axis_of_output_signal.name)

    return None



def test_4_of_azimuthally_average(real_2d_input_signal_1):
    kwargs = {"center": (5, 5),
              "radial_range": (0.1, 0.3),
              "num_bins": 10, 
              "title": "foobar"}
    optional_params = empix.OptionalAzimuthalAveragingParams(**kwargs)

    kwargs = {"input_signal": real_2d_input_signal_1, 
              "optional_params": optional_params}
    output_signal = empix.azimuthally_average(**kwargs)
    
    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    new_core_attr_subset_candidate = {"center": (100, 100)}
    optional_params.update(new_core_attr_subset_candidate)

    with pytest.raises(ValueError) as err_info:
        kwargs = {"input_signal": real_2d_input_signal_1,
                  "optional_params": optional_params}
        empix.azimuthally_average(**kwargs)

    return None



def test_1_of_OptionalAzimuthalIntegrationParams():
    cls_alias = empix.OptionalAzimuthalIntegrationParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"center": (10, 9),
              "radial_range": (0.1, 0.3),
              "num_bins": 10}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = (10, 9)
        kwargs["radial_range"] = (-0.1, 0.3)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["radial_range"] = (0.3, 0.1)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["radial_range"] = (0.1, 0.3)
        kwargs["num_bins"] = 0
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_azimuthally_integrate(real_2d_input_signal_1, 
                                    complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius
        avg_real_val_inside_ring = metadata.avg_real_val_inside_ring
        avg_imag_val_inside_ring = metadata.avg_imag_val_inside_ring

        radial_range = (inner_ring_radius/2, outer_ring_radius+1)
        num_bins = 180

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAzimuthalIntegrationParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range, 
                          "num_bins": num_bins}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.azimuthally_integrate(**kwargs)

                u = (inner_ring_radius + outer_ring_radius)/2
                expected_data_elem_val = (2*np.pi*u) * avg_real_val_inside_ring
                if np.iscomplexobj(output_signal.data):
                    expected_data_elem_val += (1j 
                                               * (2*np.pi*u) 
                                               * avg_imag_val_inside_ring)

                kwargs = {"output_signal": output_signal, 
                          "Y_idx": Y_idx,
                          "X_idx": X_idx,
                          "u": u,
                          "expected_data_elem_val": expected_data_elem_val}
                check_1d_output_signal_data_elem(**kwargs)

                kwargs["u"] = inner_ring_radius / 2
                kwargs["expected_data_elem_val"] *= 0
                check_1d_output_signal_data_elem(**kwargs)

    return None



def test_2_of_azimuthally_integrate(real_2d_input_signal_1, 
                                    complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius

        radial_range = (inner_ring_radius/2, outer_ring_radius+1)
        num_bins = 180

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAzimuthalIntegrationParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range, 
                          "num_bins": num_bins}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.azimuthally_integrate(**kwargs)

                u_size = output_signal.axes_manager[-1].size
                u_scale = output_signal.axes_manager[-1].scale
                u_offset = output_signal.axes_manager[-1].offset

                assert (num_bins == u_size)

                tol = 1e-2

                n_u_set = (0, u_size-1)
                expected_u_set = radial_range
                zip_obj = zip(n_u_set, expected_u_set)

                for n_u, expected_u in zip_obj:
                    u = u_offset + n_u*u_scale
                    rel_diff = abs(u-expected_u) / expected_u
                    assert (rel_diff < tol)

    return None



def test_3_of_azimuthally_integrate(real_2d_input_signal_1, 
                                    complex_2d_input_signal_1, 
                                    real_1d_input_signal_1, 
                                    complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.azimuthally_integrate(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Azimuthally Integrated " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_azimuthally_integrate(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.azimuthally_integrate(**kwargs)

    return None



def test_4_of_azimuthally_integrate(real_2d_input_signal_1):
    kwargs = {"center": (5, 5),
              "radial_range": (0.1, 0.3),
              "num_bins": 10, 
              "title": "foobar"}
    optional_params = empix.OptionalAzimuthalIntegrationParams(**kwargs)

    kwargs = {"input_signal": real_2d_input_signal_1, 
              "optional_params": optional_params}
    output_signal = empix.azimuthally_integrate(**kwargs)
    
    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    new_core_attr_subset_candidate = {"center": (100, 100)}
    optional_params.update(new_core_attr_subset_candidate)

    with pytest.raises(ValueError) as err_info:
        kwargs = {"input_signal": real_2d_input_signal_1,
                  "optional_params": optional_params}
        empix.azimuthally_integrate(**kwargs)

    return None



def test_1_of_OptionalAnnularAveragingParams():
    cls_alias = empix.OptionalAnnularAveragingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"center": (1, 0.9),
              "radial_range": (0.1, 0.3)}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = (1, 0.9)
        kwargs["radial_range"] = (-0.1, 0.3)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["radial_range"] = (0.3, 0.1)
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_annularly_average(real_2d_input_signal_1, 
                                complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius
        avg_real_val_inside_ring = metadata.avg_real_val_inside_ring
        avg_imag_val_inside_ring = metadata.avg_imag_val_inside_ring

        a = inner_ring_radius/2
        b = inner_ring_radius
        c = (inner_ring_radius+outer_ring_radius)/2

        A = avg_real_val_inside_ring * np.pi * (c**2 - b**2)
        B = avg_imag_val_inside_ring * np.pi * (c**2 - b**2)
        C = np.pi * (c**2 - a**2)

        radial_range = (a, c)

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAnnularAveragingParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.annularly_average(**kwargs)

                data_elem = output_signal.data[Y_idx, X_idx]
                expected_data_elem_val = A / C
                if np.iscomplexobj(output_signal.data):
                    expected_data_elem_val += 1j * B / C

                tol = 1e-2
                rel_diff = (abs(data_elem-expected_data_elem_val)
                            / abs(expected_data_elem_val))
                assert (rel_diff < tol)

                kwargs = {"input_signal": input_signal, 
                          "output_signal": output_signal}
                check_axes_after_applying_annularly_average(**kwargs)

    return None



def check_axes_after_applying_annularly_average(input_signal, 
                                                output_signal):
    check_navigation_space_axes(input_signal, output_signal)

    return None



def test_2_of_annularly_average(real_2d_input_signal_1, 
                                complex_2d_input_signal_1, 
                                real_1d_input_signal_1, 
                                complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.annularly_average(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Annularly Averaged " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_annularly_average(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.annularly_average(**kwargs)

    return None



def test_3_of_annularly_average(real_2d_input_signal_1):
    kwargs = {"center": (5, 5),
              "radial_range": (0.1, 0.3), 
              "title": "foobar"}
    optional_params = empix.OptionalAnnularAveragingParams(**kwargs)

    kwargs = {"input_signal": real_2d_input_signal_1, 
              "optional_params": optional_params}
    output_signal = empix.annularly_average(**kwargs)
    
    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    new_core_attr_subset_candidate = {"center": (100, 100)}
    optional_params.update(new_core_attr_subset_candidate)

    with pytest.raises(ValueError) as err_info:
        kwargs = {"input_signal": real_2d_input_signal_1,
                  "optional_params": optional_params}
        empix.annularly_average(**kwargs)

    return None



def test_1_of_OptionalAnnularIntegrationParams():
    cls_alias = empix.OptionalAnnularIntegrationParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"center": (1, 0.9),
              "radial_range": (0.1, 0.3)}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = (1, 0.9)
        kwargs["radial_range"] = (-0.1, 0.3)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["radial_range"] = (0.3, 0.1)
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_annularly_integrate(real_2d_input_signal_1, 
                                  complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        metadata = input_signal.metadata
        ring_centers = metadata.ring_centers
        inner_ring_radius = metadata.inner_ring_radius
        outer_ring_radius = metadata.outer_ring_radius
        avg_real_val_inside_ring = metadata.avg_real_val_inside_ring
        avg_imag_val_inside_ring = metadata.avg_imag_val_inside_ring

        a = inner_ring_radius/2
        b = inner_ring_radius
        c = (inner_ring_radius+outer_ring_radius)/2

        A = avg_real_val_inside_ring * np.pi * (c**2 - b**2)
        B = avg_imag_val_inside_ring * np.pi * (c**2 - b**2)

        radial_range = (a, c)

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                cls_alias = empix.OptionalAnnularIntegrationParams
                kwargs = {"center": ring_centers[Y_idx][X_idx],
                          "radial_range": radial_range}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.annularly_integrate(**kwargs)

                tol = 1e-2

                data_elem = output_signal.data[Y_idx, X_idx]
                expected_data_elem_val = A
                if np.iscomplexobj(output_signal.data):
                    expected_data_elem_val += 1j * B

                rel_diff = (abs(data_elem-expected_data_elem_val)
                            / abs(expected_data_elem_val))
                assert (rel_diff < tol)

                kwargs = {"input_signal": input_signal, 
                          "output_signal": output_signal}
                check_axes_after_applying_annularly_integrate(**kwargs)

    return None



def check_axes_after_applying_annularly_integrate(input_signal, 
                                                  output_signal):
    check_navigation_space_axes(input_signal, output_signal)

    return None



def test_2_of_annularly_integrate(real_2d_input_signal_1, 
                                  complex_2d_input_signal_1, 
                                  real_1d_input_signal_1, 
                                  complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.annularly_integrate(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Annularly Integrated " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_annularly_integrate(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.annularly_integrate(**kwargs)

    return None



def test_3_of_annularly_integrate(real_2d_input_signal_1):
    kwargs = {"center": (5, 5),
              "radial_range": (0.1, 0.3), 
              "title": "foobar"}
    optional_params = empix.OptionalAnnularIntegrationParams(**kwargs)

    kwargs = {"input_signal": real_2d_input_signal_1, 
              "optional_params": optional_params}
    output_signal = empix.annularly_integrate(**kwargs)
    
    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    new_core_attr_subset_candidate = {"center": (100, 100)}
    optional_params.update(new_core_attr_subset_candidate)

    with pytest.raises(ValueError) as err_info:
        kwargs = {"input_signal": real_2d_input_signal_1,
                  "optional_params": optional_params}
        empix.annularly_integrate(**kwargs)

    return None



def test_1_of_OptionalCumulative1dIntegrationParams():
    cls_alias = empix.OptionalCumulative1dIntegrationParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"limits": (0.1, 0.3),
              "num_bins": 10,
              "normalize": True}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["limits"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["limits"] = (0.1, 0.1)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["limits"] = (0.1, 0.3)
        kwargs["num_bins"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["num_bins"] = 10
        kwargs["normalize"] = slice(None)
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_cumulatively_integrate_1d(real_1d_input_signal_1, 
                                        complex_1d_input_signal_1):
    input_signals = (real_1d_input_signal_1, complex_1d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, u_dim = input_signal.data.shape

        u_size = input_signal.axes_manager[-1].size
        u_scale = input_signal.axes_manager[-1].scale
        u_offset = input_signal.axes_manager[-1].offset

        u_min = u_offset - 2
        u_max = u_offset + (u_size-1)*u_scale + 2
        u_set = (u_min, u_min+1, u_min+2, (u_max-2)/2, u_max-2, u_max-1, u_max)

        num_bins = u_size+100

        for integration_direction in (-1, 1):
            for normalize in (True, False):
                limits = (u_min, u_max)[::integration_direction]
                
                cls_alias = empix.OptionalCumulative1dIntegrationParams
                kwargs = {"limits": limits,
                          "num_bins": num_bins, 
                          "normalize": normalize}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.cumulatively_integrate_1d(**kwargs)

                for Y_idx in range(Y_dim):
                    for X_idx in range(X_dim):
                        for u in u_set:
                            kwargs = {"input_signal": input_signal, 
                                      "Y_idx": Y_idx,
                                      "X_idx": X_idx,
                                      "limits": limits,
                                      "u": u, 
                                      "normalize": normalize}
                            I = calc_expected_cumulative_integral(**kwargs)

                            kwargs = {"output_signal": output_signal, 
                                      "Y_idx": Y_idx,
                                      "X_idx": X_idx,
                                      "u": u, 
                                      "expected_data_elem_val": I}
                            check_1d_output_signal_data_elem(**kwargs)

    return None



def calc_expected_cumulative_integral(input_signal, 
                                      Y_idx, 
                                      X_idx, 
                                      limits, 
                                      u, 
                                      normalize):
    metadata = input_signal.metadata
    slopes = metadata.slopes
    b_0 = metadata.y_intercept_of_real_part
    b_1 = metadata.y_intercept_of_imag_part

    u_size = input_signal.axes_manager[-1].size
    u_scale = input_signal.axes_manager[-1].scale
    u_offset = input_signal.axes_manager[-1].offset

    m = slopes[Y_idx][X_idx]

    u_a = u_offset
    u_c = u_offset + (u_size-1)*u_scale

    cmpnts = tuple()
    
    if limits[0] < limits[1]:
        for U in (u, limits[1]):
            u_b = min(max(U, u_a), u_c)
            cmpnt = (m/2)*(u_b**2 - u_a**2) + b_0*(u_b - u_a)
            if np.iscomplexobj(input_signal.data):
                cmpnt += 1j * ((m/2)*(u_b**2 - u_a**2) + b_1*(u_b - u_a))
            cmpnts += (cmpnt,)
    else:
        for U in (u, limits[1]):
            u_b = max(min(U, u_c), u_a)
            cmpnt = (m/2)*(u_b**2 - u_c**2) + b_0*(u_b - u_c)
            if np.iscomplexobj(input_signal.data):
                cmpnt += 1j * ((m/2)*(u_b**2 - u_c**2) + b_1*(u_b - u_c))
            cmpnts += (cmpnt,)

    tol = 1e-10
    
    Gamma = (1
             if ((normalize == False) or (abs(cmpnts[1]) <= tol))
             else abs(cmpnts[1]))

    expected_cumulative_integral = cmpnts[0] / Gamma

    return expected_cumulative_integral



def test_2_of_cumulatively_integrate_1d(real_1d_input_signal_1, 
                                        complex_1d_input_signal_1):
    input_signals = (real_1d_input_signal_1, complex_1d_input_signal_1)
    
    for input_signal in input_signals:
        u_size = input_signal.axes_manager[-1].size
        u_scale = input_signal.axes_manager[-1].scale
        u_offset = input_signal.axes_manager[-1].offset

        u_min = u_offset - 2
        u_max = u_offset + (u_size-1)*u_scale + 2

        num_bins = u_size+100

        for integration_direction in (-1, 1):
            for normalize in (True, False):
                limits = (u_min, u_max)[::integration_direction]
                
                cls_alias = empix.OptionalCumulative1dIntegrationParams
                kwargs = {"limits": limits,
                          "num_bins": num_bins, 
                          "normalize": normalize}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.cumulatively_integrate_1d(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "output_signal": output_signal}
                check_axes_after_applying_cumulatively_integrate_1d(**kwargs)

    return None



def check_axes_after_applying_cumulatively_integrate_1d(input_signal, 
                                                        output_signal):
    check_navigation_space_axes(input_signal, output_signal)

    input_u_units = input_signal.axes_manager[-1].units
    output_u_units = output_signal.axes_manager[-1].units

    output_u_name = output_signal.axes_manager[-1].name

    expected_output_u_units = input_u_units

    if input_u_units == "Å":
        expected_output_u_name = "$r$"
    else:
        expected_output_u_name = "$k$"

    assert (output_u_name == expected_output_u_name)
    assert (output_u_units == expected_output_u_units)

    return None



def test_3_of_cumulatively_integrate_1d(real_1d_input_signal_1, 
                                        complex_1d_input_signal_1):
    input_signals = (real_1d_input_signal_1, complex_1d_input_signal_1)
    
    for input_signal in input_signals:
        Y_dim, X_dim, u_dim = input_signal.data.shape

        u_size = input_signal.axes_manager[-1].size
        u_scale = input_signal.axes_manager[-1].scale
        u_offset = input_signal.axes_manager[-1].offset

        u_min = u_offset - 2
        u_max = u_offset + (u_size-1)*u_scale + 2
        
        num_bins = 180

        for integration_direction in (-1, 1):
            limits = (u_min, u_max)[::integration_direction]

            cls_alias = empix.OptionalCumulative1dIntegrationParams
            kwargs = {"limits": limits,
                      "num_bins": num_bins, 
                      "normalize": False}
            optional_params = cls_alias(**kwargs)

            kwargs = {"input_signal": input_signal, 
                      "optional_params": optional_params}
            output_signal = empix.cumulatively_integrate_1d(**kwargs)

            u_size = output_signal.axes_manager[-1].size
            u_scale = output_signal.axes_manager[-1].scale
            u_offset = output_signal.axes_manager[-1].offset

            assert (num_bins == u_size)

            tol = 1e-2

            n_u_set = (0, u_size-1)
            expected_u_set = limits
            zip_obj = zip(n_u_set, expected_u_set)

            for n_u, expected_u in zip_obj:
                u = u_offset + n_u*u_scale
                rel_diff = abs(u-expected_u) / expected_u
                assert (rel_diff < tol)

    return None



def test_4_of_cumulatively_integrate_1d(real_2d_input_signal_1, 
                                        complex_2d_input_signal_1, 
                                        real_1d_input_signal_1, 
                                        complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal1D,
                          hyperspy.signals.ComplexSignal1D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.cumulatively_integrate_1d(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("CDF(" 
                              + input_signal_candidate.metadata.General.title
                              + ")")
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
            check_axes_after_applying_cumulatively_integrate_1d(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.cumulatively_integrate_1d(**kwargs)

    return None



def test_5_of_cumulatively_integrate_1d(real_1d_input_signal_1):
    kwargs = {"limits": (0.3, 0.1),
              "num_bins": 10, 
              "normalize": False, 
              "title": "foobar"}
    optional_params = empix.OptionalCumulative1dIntegrationParams(**kwargs)

    input_signal = real_1d_input_signal_1
    N_u = input_signal.axes_manager[-1].size
    input_signal.axes_manager[-1].offset = 0.1*N_u
    input_signal.axes_manager[-1].scale *= -1

    kwargs = {"input_signal": input_signal, 
              "optional_params": optional_params}
    output_signal = empix.cumulatively_integrate_1d(**kwargs)

    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    return None



def test_1_of_OptionalCroppingParams():
    cls_alias = empix.OptionalCroppingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"center": (1, 0.9),
              "window_dims": (5, 6),
              "pad_mode": "wrap",
              "apply_symmetric_mask": True}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["center"] = (1, 0.9)
        kwargs["window_dims"] = (0, 6)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["window_dims"] = (5, 6)
        kwargs["pad_mode"] = slice(None)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["pad_mode"] = "foobar"
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["pad_mode"] = "zeros"
        kwargs["apply_symmetric_mask"] = slice(None)
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_crop(real_2d_input_signal_2, 
                   complex_2d_input_signal_2):
    input_signals = (real_2d_input_signal_2, complex_2d_input_signal_2)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        h_offset = input_signal.axes_manager[-2].offset
        h_scale = input_signal.axes_manager[-2].scale
        v_offset = input_signal.axes_manager[-1].offset
        v_scale = input_signal.axes_manager[-1].scale

        path_to_item = "frames_of_entire_rectangular_image_subjects"
        frames = input_signal.metadata.get_item(path_to_item)

        for pad_mode in ("wrap", "no-padding", "zeros"):
            for apply_symmetric_mask in (False, True):
                for Y_idx in range(Y_dim):
                    for X_idx in range(X_dim):
                        L, R, B, T = frames[Y_idx][X_idx]

                        window_dims = \
                            ((h_dim-R)-L, (v_dim-B)-T)
                        center_in_pixel_coords = \
                            (L + ((window_dims[0]+1)//2 - 1),
                             T + ((window_dims[1]+1)//2 - 1))
                        center = \
                            (h_offset + center_in_pixel_coords[0]*h_scale, 
                             v_offset + center_in_pixel_coords[1]*v_scale)
                        
                        cls_alias = empix.OptionalCroppingParams
                        kwargs = {"center": center,
                                  "window_dims": window_dims, 
                                  "pad_mode": pad_mode, 
                                  "apply_symmetric_mask": apply_symmetric_mask}
                        optional_params = cls_alias(**kwargs)

                        kwargs = {"input_signal": input_signal, 
                                  "optional_params": optional_params}
                        output_signal = empix.crop(**kwargs)

                        kwargs = {"input_signal": input_signal, 
                                  "output_signal": output_signal, 
                                  "Y_idx": Y_idx, 
                                  "X_idx": X_idx,
                                  "pad_mode": pad_mode, 
                                  "apply_symmetric_mask": apply_symmetric_mask}
                        check_select_areas_of_cropped_signal(**kwargs)

    return None



def check_select_areas_of_cropped_signal(input_signal, 
                                         output_signal, 
                                         Y_idx, 
                                         X_idx, 
                                         pad_mode, 
                                         apply_symmetric_mask):
    input_signal_datasubset = input_signal.inav[X_idx, Y_idx].data
    output_signal_datasubset = output_signal.inav[X_idx, Y_idx].data
    v_dim, h_dim = input_signal_datasubset.shape

    metadata = input_signal.metadata

    signals_are_complex = np.iscomplexobj(output_signal_datasubset)

    path_to_item = ("frames_of_entire_rectangular_image_subjects"
                    if (pad_mode == "wrap")
                    else "frames_of_imaged_parts_of_rectangular_image_subjects")
    frames = metadata[path_to_item ]
    L, R, B, T = frames[Y_idx][X_idx]

    a = metadata["real_val_inside_imaged_part_of_rectangular_image_subject"]
    b = metadata["imag_val_inside_imaged_part_of_rectangular_image_subject"]

    if (not ((pad_mode == "zeros") and (apply_symmetric_mask == True))):
        area = (output_signal_datasubset.real == a).sum()
        expected_area = ((h_dim-R)-L)*((v_dim-B)-T)
        assert (area == expected_area)

        if signals_are_complex:
            area = (output_signal_datasubset.imag == b).sum()
            assert (area == expected_area)

        area = (output_signal_datasubset.real == 0).sum()
        expected_area = (np.prod(output_signal.data.shape[-2:]) 
                         - expected_area)
        assert (area == expected_area)

        if signals_are_complex:
            area = (output_signal_datasubset.imag == 0).sum()
            assert (area == expected_area)

    return None



def test_2_of_crop(real_2d_input_signal_2, 
                   complex_2d_input_signal_2):
    input_signals = (real_2d_input_signal_2, complex_2d_input_signal_2)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        h_offset = input_signal.axes_manager[-2].offset
        h_scale = input_signal.axes_manager[-2].scale
        v_offset = input_signal.axes_manager[-1].offset
        v_scale = input_signal.axes_manager[-1].scale

        path_to_item = "frames_of_entire_rectangular_image_subjects"
        frames = input_signal.metadata.get_item(path_to_item)

        for Y_idx in range(Y_dim):
            for X_idx in range(X_dim):
                L, R, B, T = frames[Y_idx][X_idx]

                cropping_window_dims = \
                    ((h_dim-R)-L, (v_dim-B)-T)
                cropping_center_in_pixel_coords = \
                    (L + ((cropping_window_dims[0]+1)//2 - 1),
                     T + ((cropping_window_dims[1]+1)//2 - 1))
                cropping_center = \
                    (h_offset + cropping_center_in_pixel_coords[0]*h_scale,
                     v_offset + cropping_center_in_pixel_coords[1]*v_scale)
                        
                kwargs = {"cropping_center": cropping_center, 
                          "cropping_window_dims": cropping_window_dims,
                          "input_signal": input_signal, 
                          "Y_idx": Y_idx, 
                          "X_idx": X_idx}
                check_masks_for_cropping(**kwargs)

    return None



def check_masks_for_cropping(cropping_center, 
                             cropping_window_dims,
                             input_signal, 
                             Y_idx, 
                             X_idx):
    masks = tuple()
    for apply_symmetric_mask in (False, True):
        cls_alias = empix.OptionalCroppingParams
        kwargs = {"center": cropping_center,
                  "window_dims": cropping_window_dims, 
                  "pad_mode": "zeros", 
                  "apply_symmetric_mask": apply_symmetric_mask}
        optional_params = cls_alias(**kwargs)

        kwargs = {"input_signal": input_signal.inav[X_idx, Y_idx], 
                  "optional_params": optional_params}
        output_signal = empix.crop(**kwargs)

        mask = (output_signal.data.real == 0)
        masks += (mask,)

        if np.iscomplexobj(output_signal.data):
            assert bool(np.all((output_signal.data.imag == 0) == mask))

    mask_1, mask_2 = masks

    assert bool(np.all((~mask_1)*(~mask_1[::-1, ::-1]) == ~mask_2))

    return None



def test_3_of_crop(real_2d_input_signal_2):
    input_signal = real_2d_input_signal_2
    
    Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

    h_offset = input_signal.axes_manager[-2].offset
    h_scale = input_signal.axes_manager[-2].scale
    v_offset = input_signal.axes_manager[-1].offset
    v_scale = input_signal.axes_manager[-1].scale

    path_to_item = "frames_of_entire_rectangular_image_subjects"
    frames = input_signal.metadata.get_item(path_to_item)

    for pad_mode in ("wrap", "no-padding", "zeros"):
        for apply_symmetric_mask in (False, True):
            for Y_idx in range(Y_dim):
                for X_idx in range(X_dim):
                    L, R, B, T = frames[Y_idx][X_idx]

                    window_dims = \
                        ((h_dim-R)-L, (v_dim-B)-T)
                    center_in_pixel_coords = \
                        (L + ((window_dims[0]+1)//2 - 1),
                         T + ((window_dims[1]+1)//2 - 1))
                    center = \
                        (h_offset + center_in_pixel_coords[0]*h_scale, 
                         v_offset + center_in_pixel_coords[1]*v_scale)
                        
                    cls_alias = empix.OptionalCroppingParams
                    kwargs = {"center": center,
                              "window_dims": window_dims, 
                              "pad_mode": pad_mode, 
                              "apply_symmetric_mask": apply_symmetric_mask}
                    optional_params = cls_alias(**kwargs)

                    kwargs = {"input_signal": input_signal, 
                              "optional_params": optional_params}
                    output_signal = empix.crop(**kwargs)

                    kwargs = {"input_signal": input_signal, 
                              "output_signal": output_signal, 
                              "optional_params": optional_params,
                              "Y_idx": Y_idx, 
                              "X_idx": X_idx}
                    check_axes_after_applying_crop(**kwargs)

    return None



def check_axes_after_applying_crop(input_signal, 
                                   output_signal, 
                                   optional_params, 
                                   Y_idx, 
                                   X_idx):
    kwargs = locals()
    check_signal_space_axes_sizes_after_applying_crop(**kwargs)
    
    check_navigation_space_axes(input_signal, output_signal)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    pad_mode = optional_params_core_attrs["pad_mode"]

    input_h_offset = input_signal.axes_manager[-2].offset
    input_h_scale = input_signal.axes_manager[-2].scale
    input_v_offset = input_signal.axes_manager[-1].offset
    input_v_scale = input_signal.axes_manager[-1].scale

    output_h_offset = output_signal.axes_manager[-2].offset
    output_v_offset = output_signal.axes_manager[-1].offset

    tol = 1e-6

    path_to_item = ("frames_of_imaged_parts_of_rectangular_image_subjects"
                    if (pad_mode == "no-padding")
                    else "frames_of_entire_rectangular_image_subjects")
    frames = input_signal.metadata.get_item(path_to_item)
    L, R, B, T = frames[Y_idx][X_idx]

    expected_output_h_offset = input_h_offset + input_h_scale*L
    abs_diff = abs(output_h_offset-expected_output_h_offset)
    assert (abs_diff < tol)

    expected_output_v_offset = input_v_offset + input_v_scale*T
    abs_diff = abs(output_v_offset-expected_output_v_offset)
    assert (abs_diff < tol)

    num_axes = len(input_signal.data.shape)
    for axis_idx in range(num_axes-2, num_axes):
        axis_of_input_signal = input_signal.axes_manager[axis_idx]
        axis_of_output_signal = output_signal.axes_manager[axis_idx]

        assert (axis_of_input_signal.scale == axis_of_output_signal.scale)
        assert (axis_of_input_signal.units == axis_of_output_signal.units)
        assert (axis_of_input_signal.name == axis_of_output_signal.name)

    return None



def check_signal_space_axes_sizes_after_applying_crop(input_signal, 
                                                      output_signal, 
                                                      optional_params, 
                                                      Y_idx, 
                                                      X_idx):
    Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

    output_h_size = output_signal.axes_manager[-2].size
    output_v_size = output_signal.axes_manager[-1].size
    
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    pad_mode = optional_params_core_attrs["pad_mode"]
    
    path_to_item = ("frames_of_imaged_parts_of_rectangular_image_subjects"
                    if (pad_mode == "no-padding")
                    else "frames_of_entire_rectangular_image_subjects")
    frames = input_signal.metadata.get_item(path_to_item)
    L, R, B, T = frames[Y_idx][X_idx]

    expected_output_h_size = (h_dim-R) - L
    assert (output_h_size == expected_output_h_size)

    expected_output_v_size = (v_dim-B) - T
    assert (output_v_size == expected_output_v_size)

    return None



def test_4_of_crop(real_2d_input_signal_1, 
                   complex_2d_input_signal_1, 
                   real_1d_input_signal_1, 
                   complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.crop(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Cropped " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.crop(**kwargs)

    return None



def test_5_of_crop(real_2d_input_signal_1):
    kwargs = {"center": (5, 5),
              "window_dims": (5, 6), 
              "pad_mode": "no-padding", 
              "apply_symmetric_mask": True,
              "title": "foobar"}
    optional_params = empix.OptionalCroppingParams(**kwargs)

    kwargs = {"input_signal": real_2d_input_signal_1, 
              "optional_params": optional_params}
    output_signal = empix.crop(**kwargs)

    title = output_signal.metadata.General.title
    expected_title = optional_params.core_attrs["title"]
    assert (title == expected_title)

    new_core_attr_subset_candidate = {"center": (100, 100)}
    optional_params.update(new_core_attr_subset_candidate)

    with pytest.raises(ValueError) as err_info:
        empix.crop(**kwargs)

    return None



def test_1_of_OptionalDownsamplingParams():
    cls_alias = empix.OptionalDownsamplingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"block_dims": (2, 3),
              "padding_const": 1.5,
              "downsample_mode": "sum"}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["block_dims"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["block_dims"] = (2, 3)
        kwargs["padding_const"] = slice(None)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["padding_const"] = 1.5
        kwargs["downsample_mode"] = slice(None)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["downsample_mode"] = "foobar"
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_downsample(real_2d_input_signal_1, 
                         complex_2d_input_signal_1):
    input_signals = (real_2d_input_signal_1, complex_2d_input_signal_1)

    padding_const = -5
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape
        for downsample_mode in ("sum", "mean", "median", "amin", "amax"):
            for block_dims in ((1, 1), (2, 2), (2, 3), (3, 2)):
                cls_alias = empix.OptionalDownsamplingParams
                kwargs = {"block_dims": block_dims,
                          "padding_const": padding_const, 
                          "downsample_mode": downsample_mode}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "optional_params": optional_params}
                output_signal = empix.downsample(**kwargs)

                kwargs = {"input_signal": input_signal, 
                          "output_signal": output_signal, 
                          "optional_params": optional_params}
                check_axes_after_applying_downsample(**kwargs)

                for Y_idx in range(Y_dim):
                    for X_idx in range(X_dim):
                        input_signal_datasubset = \
                            input_signal.inav[X_idx, Y_idx].data
                        kwargs = \
                            {"image": input_signal_datasubset, 
                             "block_size": block_dims[::-1],
                             "cval": padding_const,
                             "func": getattr(np, downsample_mode)}
                        downsampled_input_signal_datasubset = \
                            skimage.measure.block_reduce(**kwargs)

                        output_signal_datasubset = \
                            output_signal.inav[X_idx, Y_idx].data

                        array_1 = output_signal_datasubset
                        array_2 = downsampled_input_signal_datasubset

                        assert np.all(array_1 == array_2)

    return None



def check_axes_after_applying_downsample(input_signal, 
                                         output_signal, 
                                         optional_params):
    check_navigation_space_axes(input_signal, output_signal)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    block_dims = optional_params_core_attrs["block_dims"]

    num_spatial_dims = len(block_dims)

    for spatial_dim_idx in range(num_spatial_dims):
        input_axis_size = \
            input_signal.axes_manager[-2+spatial_dim_idx].size
        input_axis_scale = \
            input_signal.axes_manager[-2+spatial_dim_idx].scale
        input_axis_offset = \
            input_signal.axes_manager[-2+spatial_dim_idx].offset
        input_axis_name = \
            input_signal.axes_manager[-2+spatial_dim_idx].name
        input_axis_units = \
            input_signal.axes_manager[-2+spatial_dim_idx].units
        
        output_axis_size = \
            output_signal.axes_manager[-2+spatial_dim_idx].size
        output_axis_scale = \
            output_signal.axes_manager[-2+spatial_dim_idx].scale
        output_axis_offset = \
            output_signal.axes_manager[-2+spatial_dim_idx].offset
        output_axis_name = \
            output_signal.axes_manager[-2+spatial_dim_idx].name
        output_axis_units = \
            output_signal.axes_manager[-2+spatial_dim_idx].units

        block_dim = block_dims[spatial_dim_idx]

        expected_output_axis_size = int(np.ceil(input_axis_size/block_dim))
        expected_output_axis_scale = input_axis_scale*block_dim
        expected_output_axis_offset = (input_axis_offset
                                       + 0.5*input_axis_scale*(block_dim-1))
        expected_output_axis_name = input_axis_name
        expected_output_axis_units = input_axis_units

        assert (output_axis_size == expected_output_axis_size)
        assert (output_axis_scale == expected_output_axis_scale)
        assert (output_axis_offset == expected_output_axis_offset)
        assert (output_axis_name == expected_output_axis_name)
        assert (output_axis_units == expected_output_axis_units)

    return None



def test_2_of_downsample(real_2d_input_signal_1, 
                         complex_2d_input_signal_1, 
                         real_1d_input_signal_1, 
                         complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        optional_params = empix.OptionalDownsamplingParams()

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": optional_params}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.downsample(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Downsampled " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal, 
                      "optional_params": optional_params}
            check_axes_after_applying_downsample(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.downsample(**kwargs)

    return None



def test_1_of_OptionalResamplingParams():
    cls_alias = empix.OptionalResamplingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    kwargs = {"new_signal_space_sizes": (15, 16),
              "new_signal_space_scales": (0.15, 0.2),
              "new_signal_space_offsets": (0.05, 1.2),
              "spline_degrees": (2, 3),
              "interpolate_polar_cmpnts": False}
    optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["new_signal_space_sizes"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["new_signal_space_sizes"] = (15, 16)
        kwargs["new_signal_space_scales"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["new_signal_space_scales"] = (0.1, 0)
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["new_signal_space_scales"] = (0.15, 0.2)
        kwargs["new_signal_space_offsets"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs["new_signal_space_offsets"] = (0.05, 1.2)
        kwargs["spline_degrees"] = 0
        optional_params = cls_alias(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs["spline_degrees"] = (6, 3)
        optional_params = cls_alias(**kwargs)

    return None



def test_2_of_OptionalResamplingParams():
    cls_alias = empix.OptionalResamplingParams

    optional_params = cls_alias()

    optional_params.validation_and_conversion_funcs
    optional_params.pre_serialization_funcs
    optional_params.de_pre_serialization_funcs

    kwargs = {"serializable_rep": optional_params.pre_serialize()}
    cls_alias.de_pre_serialize(**kwargs)

    with pytest.raises(TypeError) as err_info:
        kwargs = {"new_signal_space_sizes": (15, 16),
                  "new_signal_space_scales": (0.15, 0.2),
                  "new_signal_space_offsets": (0.05, 1.2),
                  "spline_degrees": (2, 3),
                  "interpolate_polar_cmpnts": slice(None)}
        optional_params = cls_alias(**kwargs)

    return None



def test_1_of_resample(real_2d_input_signal_3, 
                       complex_2d_input_signal_3):
    input_signals = (real_2d_input_signal_3, complex_2d_input_signal_3)
    
    for input_signal in input_signals:
        Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

        num_spatial_dims = 2
        new_signal_space_sizes = tuple()
        new_signal_space_scales = tuple()
        new_signal_space_offsets = tuple()
        
        for spatial_dim_idx in range(num_spatial_dims):
            input_axis_size = \
                input_signal.axes_manager[-2+spatial_dim_idx].size
            input_axis_scale = \
                input_signal.axes_manager[-2+spatial_dim_idx].scale
            input_axis_offset = \
                input_signal.axes_manager[-2+spatial_dim_idx].offset
            new_signal_space_sizes += \
                (input_axis_size//4,)
            new_signal_space_scales += \
                (1.5*input_axis_scale,)
            new_signal_space_offsets += \
                (input_axis_offset + (input_axis_size//4)*input_axis_scale,)

        for spline_degrees in ((1, 3), (5, 2)):
            for interpolate_polar_cmpnts in (False, True):
                cls_alias = empix.OptionalResamplingParams
                kwargs = {"new_signal_space_sizes": new_signal_space_sizes,
                          "new_signal_space_scales": new_signal_space_scales,
                          "new_signal_space_offsets": new_signal_space_offsets,
                          "spline_degrees": spline_degrees,
                          "interpolate_polar_cmpnts": interpolate_polar_cmpnts}
                optional_params = cls_alias(**kwargs)

                kwargs = {"input_signal": input_signal,
                          "optional_params": optional_params}
                output_signal = empix.resample(**kwargs)

                kwargs["output_signal"] = output_signal
                check_resampled_signal_data(**kwargs)
                check_axes_after_applying_resample(**kwargs)

    return None



def check_resampled_signal_data(input_signal, optional_params, output_signal):
    Y_dim, X_dim, v_dim, h_dim = input_signal.data.shape

    kwargs = {"optional_params": optional_params, 
              "input_signal": input_signal}
    n_h, n_v = calc_resampling_pixel_coords_wrt_input_signal_axes(**kwargs)

    metadata = input_signal.metadata
    real_val_of_const_bg = metadata.real_val_of_const_bg
    imag_val_of_const_bg = metadata.imag_val_of_const_bg
    A_real = metadata.real_val_of_peak_amplitude
    A_imag = metadata.imag_val_of_peak_amplitude
    sigma = metadata.peak_width_in_pixels
    peak_centers_in_pixel_coords = metadata.peak_centers_in_pixel_coords

    kwargs = {"shape": output_signal.data.shape, "dtype": "complex"}
    expected_resampled_signal_data = np.ones(**kwargs)
    expected_resampled_signal_data[:] = (real_val_of_const_bg 
                                         + 1j*imag_val_of_const_bg)

    resampled_signal_data = output_signal.data

    for Y_idx in range(Y_dim):
        for X_idx in range(X_dim):
            n_h_c, n_v_c = peak_centers_in_pixel_coords[Y_idx][X_idx]

            n_hv_sq = (n_h-n_h_c)**2 + (n_v-n_v_c)**2
            sigma_sq = sigma*sigma

            expected_resampled_signal_data[Y_idx, X_idx] += \
                (A_real*np.exp(-n_hv_sq / (2*sigma_sq))
                 + 1j*A_imag*np.exp(-n_hv_sq / (2*sigma_sq)))

    tol = 1e-4
    
    rel_diff = (np.abs(resampled_signal_data
                       - expected_resampled_signal_data)
                / np.abs(expected_resampled_signal_data))
    assert bool(np.all(rel_diff < tol))

    abs_diff = np.abs(np.angle(resampled_signal_data)
                      - np.angle(expected_resampled_signal_data))
    assert bool(np.all(abs_diff < tol))

    rel_diff = (np.abs(np.abs(resampled_signal_data)
                       - np.abs(expected_resampled_signal_data))
                / np.abs(np.abs(expected_resampled_signal_data)))
    assert bool(np.all(rel_diff < tol))

    return None



def calc_resampling_pixel_coords_wrt_input_signal_axes(optional_params, 
                                                       input_signal):
    optional_params_core_attrs = \
        optional_params.get_core_attrs(deep_copy=False)
    new_signal_space_sizes = \
        optional_params_core_attrs["new_signal_space_sizes"]
    new_signal_space_scales = \
        optional_params_core_attrs["new_signal_space_scales"]
    new_signal_space_offsets = \
        optional_params_core_attrs["new_signal_space_offsets"]

    num_spatial_dims = len(new_signal_space_sizes)
    pair_of_1d_coord_arrays = tuple()
    for spatial_dim_idx in range(num_spatial_dims):
        input_axis_scale = input_signal.axes_manager[-2+spatial_dim_idx].scale
        input_axis_offset = input_signal.axes_manager[-2+spatial_dim_idx].offset

        new_signal_space_size = new_signal_space_sizes[spatial_dim_idx]
        new_signal_space_scale = new_signal_space_scales[spatial_dim_idx]
        new_signal_space_offset = new_signal_space_offsets[spatial_dim_idx]

        coord_array = (((new_signal_space_offset-input_axis_offset)
                        + (new_signal_space_scale 
                           * np.arange(new_signal_space_size)))
                       / input_axis_scale)
        pair_of_1d_coord_arrays += (coord_array.tolist(),)

    n_h, n_v = np.meshgrid(*pair_of_1d_coord_arrays, indexing="xy")

    resampling_pixel_coords_wrt_input_signal_axes = (n_h, n_v)

    return resampling_pixel_coords_wrt_input_signal_axes



def check_axes_after_applying_resample(input_signal, 
                                       output_signal, 
                                       optional_params):
    check_navigation_space_axes(input_signal, output_signal)

    optional_params_core_attrs = \
        optional_params.get_core_attrs(deep_copy=False)
    new_signal_space_sizes = \
        optional_params_core_attrs["new_signal_space_sizes"]
    new_signal_space_scales = \
        optional_params_core_attrs["new_signal_space_scales"]
    new_signal_space_offsets = \
        optional_params_core_attrs["new_signal_space_offsets"]

    num_spatial_dims = 2

    for spatial_dim_idx in range(num_spatial_dims):
        input_axis_name = input_signal.axes_manager[-2+spatial_dim_idx].name
        input_axis_units = input_signal.axes_manager[-2+spatial_dim_idx].units
        
        output_axis_size = \
            output_signal.axes_manager[-2+spatial_dim_idx].size
        output_axis_scale = \
            output_signal.axes_manager[-2+spatial_dim_idx].scale
        output_axis_offset = \
            output_signal.axes_manager[-2+spatial_dim_idx].offset
        output_axis_name = \
            output_signal.axes_manager[-2+spatial_dim_idx].name
        output_axis_units = \
            output_signal.axes_manager[-2+spatial_dim_idx].units

        expected_output_axis_size = new_signal_space_sizes[spatial_dim_idx]
        expected_output_axis_scale = new_signal_space_scales[spatial_dim_idx]
        expected_output_axis_offset = new_signal_space_offsets[spatial_dim_idx]
        expected_output_axis_name = input_axis_name
        expected_output_axis_units = input_axis_units

        assert (output_axis_size == expected_output_axis_size)
        assert (output_axis_scale == expected_output_axis_scale)
        assert (output_axis_offset == expected_output_axis_offset)
        assert (output_axis_name == expected_output_axis_name)
        assert (output_axis_units == expected_output_axis_units)

    return None



def test_2_of_resample(real_2d_input_signal_1, 
                       complex_2d_input_signal_1, 
                       real_1d_input_signal_1, 
                       complex_1d_input_signal_1):
    input_signal_candidates = (real_2d_input_signal_1, 
                               complex_2d_input_signal_1, 
                               real_1d_input_signal_1, 
                               complex_1d_input_signal_1,
                               None)
    
    for input_signal_candidate in input_signal_candidates:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)

        kwargs = {"input_signal": input_signal_candidate,
                  "optional_params": None}
        if isinstance(input_signal_candidate, accepted_types):
            output_signal = empix.resample(**kwargs)

            title = output_signal.metadata.General.title
            expected_title = ("Resampled " 
                              + input_signal_candidate.metadata.General.title)
            assert (title == expected_title)

            kwargs = {"input_signal": input_signal_candidate, 
                      "output_signal": output_signal}
            check_metadata(**kwargs)
        else:
            with pytest.raises(TypeError) as err_info:
                empix.resample(**kwargs)

    return None



###########################
## Define error messages ##
###########################
