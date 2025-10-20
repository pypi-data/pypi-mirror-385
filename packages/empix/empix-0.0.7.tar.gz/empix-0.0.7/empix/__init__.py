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
"""``empix`` is a Python library that contains tools for analyzing electron
microscopy data that are not available in `hyperspy
<https://hyperspy.org/hyperspy-doc/current/index.html>`_.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For performing deep copies.
import copy

# For checking whether certain submodules exists and for importing said
# submodules should they exist.
import importlib



# For general array handling.
import numpy as np

# For interpolating data.
import scipy.interpolate

# For validating and converting objects.
import czekitout.check
import czekitout.convert

# For defining classes that support enforced validation, updatability,
# pre-serialization, and de-serialization.
import fancytypes

# For creating hyperspy signals.
import hyperspy.signals
import hyperspy.axes

# For azimuthally integrating 2D hyperspy signals.
detectors = importlib.import_module("pyFAI.detectors")
integrators = (importlib.import_module("pyFAI.integrator.azimuthal")
               if importlib.util.find_spec("pyFAI.integrator")
               else importlib.import_module("pyFAI.azimuthalIntegrator"))

# For downsampling hyperspy signals.
import skimage.measure



# Get version of current package.
from empix.version import __version__



##################################
## Define classes and functions ##
##################################

# List of public objects in package.
__all__ = ["abs_sq",
           "OptionalAzimuthalAveragingParams",
           "azimuthally_average",
           "OptionalAzimuthalIntegrationParams",
           "azimuthally_integrate",
           "OptionalAnnularAveragingParams",
           "annularly_average",
           "OptionalAnnularIntegrationParams",
           "annularly_integrate",
           "OptionalCumulative1dIntegrationParams",
           "cumulatively_integrate_1d",
           "OptionalCroppingParams",
           "crop",
           "OptionalDownsamplingParams",
           "downsample",
           "OptionalResamplingParams",
           "resample"]



def _check_and_convert_action_to_apply_to_input_signal(params):
    obj_name = "action_to_apply_to_input_signal"
    action_to_apply_to_input_signal = params[obj_name]

    return action_to_apply_to_input_signal



def _check_and_convert_input_signal(params):
    obj_name = "input_signal"
    input_signal = params[obj_name]

    action_to_apply_to_input_signal = params["action_to_apply_to_input_signal"]

    if action_to_apply_to_input_signal == "abs_sq":
        accepted_types = (hyperspy.signals.Signal1D,
                          hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal1D,
                          hyperspy.signals.ComplexSignal2D)
    elif action_to_apply_to_input_signal == "cumulatively_integrate_1d":
        accepted_types = (hyperspy.signals.Signal1D,
                          hyperspy.signals.ComplexSignal1D)
    else:
        accepted_types = (hyperspy.signals.Signal2D,
                          hyperspy.signals.ComplexSignal2D)
    
    kwargs = {"obj": input_signal,
              "obj_name": obj_name,
              "accepted_types": accepted_types}
    czekitout.check.if_instance_of_any_accepted_types(**kwargs)

    return input_signal



def _check_and_convert_title(params):
    obj_name = "title"
    obj = params[obj_name]

    accepted_types = (str, type(None))

    if isinstance(obj, accepted_types[1]):
        if "input_signal" in params:
            param_name_subset = ("input_signal",
                                 "action_to_apply_to_input_signal")
            kwargs = {param_name: params[param_name]
                      for param_name
                      in param_name_subset}
            title = _generate_title(**kwargs)
        else:
            title = obj
    else:
        try:
            kwargs = {"obj": obj, "obj_name": obj_name}
            title = czekitout.convert.to_str_from_str_like(**kwargs)
        except:
            kwargs["accepted_types"] = accepted_types
            czekitout.check.if_instance_of_any_accepted_types(**kwargs)

    return title



def _generate_title(input_signal, action_to_apply_to_input_signal):
    prefixes = {"abs_sq": "Modulus Squared of ",
                "azimuthally_average": "Azimuthally Averaged ",
                "azimuthally_integrate": "Azimuthally Integrated ",
                "annularly_average": "Annularly Averaged ",
                "annularly_integrate": "Annularly Integrated ",
                "cumulatively_integrate_1d": "CDF(",
                "crop": "Cropped ",
                "downsample": "Downsampled ",
                "resample": "Resampled "}
    prefix = prefixes[action_to_apply_to_input_signal]

    input_signal_title = input_signal.metadata.get_item("General.title",
                                                        "signal")

    suffix = ")" if (prefix[-1] == "(") else ""

    title = prefix + input_signal_title + suffix

    return title



def _pre_serialize_title(title):
    obj_to_pre_serialize = title
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_title(serializable_rep):
    title = serializable_rep

    return title



_default_title = None



def abs_sq(input_signal, title=_default_title):
    r"""The modulus squared of a given input ``hyperspy`` signal.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.complex_signal1d.ComplexSignal1D` | :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Modulus Squared of " +
        input_signal.metadata.General.title``, where ``input_signal`` is the 
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.signal2d.Signal2D`
        The output ``hyperspy`` signal that stores the modulus squared of the
        input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "abs_sq"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _abs_sq(**kwargs)

    return output_signal



def _abs_sq(input_signal, title):
    if isinstance(input_signal, hyperspy.signals.ComplexSignal):
        output_signal = input_signal.amplitude
        output_signal *= output_signal
    else:
        output_signal = input_signal * input_signal
        
    output_signal.metadata.set_item("General.title", title)

    return output_signal



def _check_and_convert_center(params):
    obj_name = "center"
    obj = params[obj_name]

    param_name = "action_to_apply_to_input_signal"
    action_to_apply_to_input_signal = params.get(param_name, None)

    param_name = "input_signal"
    input_signal = params.get(param_name, None)

    current_func_name = "_check_and_convert_center"
    
    if obj is not None:
        try:
            kwargs = {"obj": obj, "obj_name": obj_name}
            center = czekitout.convert.to_pair_of_floats(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)

        if input_signal is not None:
            if action_to_apply_to_input_signal != "crop":
                h_range, v_range = _calc_h_and_v_ranges(signal=input_signal)
                center_is_within_h_range = h_range[0] <= center[0] <= h_range[1]
                center_is_within_v_range = v_range[0] <= center[1] <= v_range[1]
                center_is_invalid = ((not center_is_within_h_range)
                                     or (not center_is_within_v_range))
                if center_is_invalid:
                    err_msg = globals()[current_func_name+"_err_msg_2"]
                    raise ValueError(err_msg)
    else:
        if input_signal is not None:
            if action_to_apply_to_input_signal != "crop":
                h_range, v_range = _calc_h_and_v_ranges(signal=input_signal)
                center = ((h_range[0]+h_range[1])/2, (v_range[0]+v_range[1])/2)
            else:
                N_v, N_h = input_signal.data.shape[-2:]
    
                h_scale = input_signal.axes_manager[-2].scale
                v_scale = input_signal.axes_manager[-1].scale

                h_offset = input_signal.axes_manager[-2].offset
                v_offset = input_signal.axes_manager[-1].offset

                center = (h_offset + h_scale*((N_h-1)//2),
                          v_offset + v_scale*((N_v-1)//2))
        else:
            center = obj

    return center



def _calc_h_and_v_ranges(signal):
    h_scale = signal.axes_manager[-2].scale
    v_scale = signal.axes_manager[-1].scale

    N_v, N_h = signal.data.shape[-2:]

    h_offset = signal.axes_manager[-2].offset
    v_offset = signal.axes_manager[-1].offset

    h_min = min(h_offset, h_offset + (N_h-1)*h_scale)
    h_max = max(h_offset, h_offset + (N_h-1)*h_scale)
    h_range = (h_min, h_max)

    v_min = min(v_offset, v_offset + (N_v-1)*v_scale)
    v_max = max(v_offset, v_offset + (N_v-1)*v_scale)
    v_range = (v_min, v_max)

    return h_range, v_range



def _pre_serialize_center(center):
    obj_to_pre_serialize = center
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_center(serializable_rep):
    center = serializable_rep

    return center



def _check_and_convert_radial_range(params):
    obj_name = "radial_range"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)

    current_func_name = "_check_and_convert_radial_range"
    
    if obj is not None:
        try:
            func_alias = czekitout.convert.to_pair_of_nonnegative_floats
            kwargs = {"obj": obj, "obj_name": obj_name}
            radial_range = func_alias(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)

        if radial_range[0] >= radial_range[1]:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise ValueError(err_msg)
    else:
        if input_signal is not None:
            center = _check_and_convert_center(params)
            h_range, v_range = _calc_h_and_v_ranges(signal=input_signal)
            temp_1 = min(abs(center[0]-h_range[0]), abs(center[0]-h_range[1]))
            temp_2 = min(abs(center[1]-v_range[0]), abs(center[1]-v_range[1]))
            radial_range = (0, min(temp_1, temp_2))
        else:
            radial_range = obj

    return radial_range



def _pre_serialize_radial_range(radial_range):
    obj_to_pre_serialize = radial_range
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_radial_range(serializable_rep):
    radial_range = serializable_rep

    return radial_range



def _check_and_convert_num_bins(params):
    obj_name = "num_bins"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)

    current_func_name = "_check_and_convert_num_bins"
    
    if obj is not None:
        try:
            kwargs = {"obj": obj, "obj_name": obj_name}
            num_bins = czekitout.convert.to_positive_int(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)
    else:
        if input_signal is not None:
            num_bins = (input_signal.data.shape[-1]
                        if _signal_is_1d(signal=input_signal)
                        else min(input_signal.data.shape[-2:]))
        else:
            num_bins = obj

    return num_bins



def _signal_is_1d(signal):
    signal_1d_types = (hyperspy.signals.Signal1D,
                       hyperspy.signals.ComplexSignal1D)
    result = isinstance(signal, signal_1d_types)

    return result



def _pre_serialize_num_bins(num_bins):
    obj_to_pre_serialize = num_bins
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_num_bins(serializable_rep):
    num_bins = serializable_rep

    return num_bins



_default_center = None
_default_radial_range = None
_default_num_bins = None
_default_skip_validation_and_conversion = False



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalAzimuthalAveragingParams(_cls_alias):
    r"""The set of optional parameters for the function
    :func:`empix.azimuthally_average`.

    The Python function :func:`empix.azimuthally_average` averages
    azimuthally a given input 2D ``hyperspy`` signal. The Python function
    assumes that the input 2D ``hyperspy`` signal samples from a mathematical
    function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` which is piecewise
    continuous in :math:`u_{x}` and :math:`u_{y}`, where :math:`u_{x}` and
    :math:`u_{y}` are the horizontal and vertical coordinates in the signal
    space of the input signal, and :math:`\mathbf{m}` is a vector of integers
    representing the navigation indices of the input signal. The Python function
    approximates the azimuthal average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the azimuthal average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
	&\overline{S}_{\mathbf{m}}\left(U_{r}=
        u_{r}\left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\frac{1}{2\pi}\int_{0}^{2\pi}du_{\phi}\,
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: azimuthal_average__1

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the azimuthal averaging.

    Parameters
    ----------
    center : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``center`` is set to ``None``, then the reference point
        :math:`\left(c_{x},c_{y}\right)`, from which the radial distance is
        defined for the azimuthal averaging, is set to the signal space
        coordinates corresponding to the center signal space pixel.  Otherwise,
        if ``center`` is set to a pair of floating-point numbers, then
        ``center[0]`` and ``center[1]`` specify :math:`c_{x}` and :math:`c_{y}`
        respectively, in the same units of the corresponding signal space axes
        of the input signal.
    radial_range : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``radial_range`` is set to ``None``, then the radial range, over
        which the azimuthal averaging is performed, is from zero to the largest
        radial distance within the signal space boundaries of the input signal
        for all azimuthal angles. Otherwise, if ``radial_range`` is set to a
        pair of floating-point numbers, then ``radial_range[0]`` and
        ``radial_range[1]`` specify the minimum and maximum radial distances of
        the radial range respectively, in the same units of the horizontal and
        vertical axes respectively of the signal space of the input signal. Note
        that in this case ``radial_range`` must satisfy
        ``0<=radial_range[0]<radial_range[1]``. Moreover, the function
        represented by the input signal is assumed to be equal to zero
        everywhere outside of the signal space boundaries of said input signal.
    num_bins : `int` | `None`, optional
        ``num_bins`` must either be a positive integer or of the `NoneType`: if
        the former, then the dimension of the signal space of the output signal
        ``output_signal`` is set to ``num_bins``; if the latter, then the
        dimension of the signal space of ``output_signal`` is set to
        ``min(input_signal.data.shape[-2:])``, where ``input_signal`` is the
        input ``hyperspy`` signal.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Azimuthally Averaged " +
        input_signal.metadata.General.title``, where ``input_signal`` is the 
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("center", "radial_range", "num_bins", "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 center=\
                 _default_center,
                 radial_range=\
                 _default_radial_range,
                 num_bins=\
                 _default_num_bins,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def _check_and_convert_optional_params(params):
    obj_name = "optional_params"
    obj = params[obj_name]

    param_name = "action_to_apply_to_input_signal"
    action_to_apply_to_input_signal = params.get(param_name, None)

    optional_params_cls_set = \
        {"azimuthally_average": OptionalAzimuthalAveragingParams,
         "azimuthally_integrate": OptionalAzimuthalIntegrationParams,
         "annularly_average": OptionalAnnularAveragingParams,
         "annularly_integrate": OptionalAnnularIntegrationParams,
         "cumulatively_integrate_1d": OptionalCumulative1dIntegrationParams,
         "crop": OptionalCroppingParams,
         "downsample": OptionalDownsamplingParams,
         "resample": OptionalResamplingParams}
    optional_params_cls = \
        optional_params_cls_set[action_to_apply_to_input_signal]
    
    optional_params = optional_params_cls() if (obj is None) else obj

    kwargs = {"obj": optional_params,
              "obj_name": obj_name,
              "accepted_types": (optional_params_cls, type(None))}
    czekitout.check.if_instance_of_any_accepted_types(**kwargs)

    optional_params_core_attrs = \
        optional_params.get_core_attrs(deep_copy=False)
    params = \
        {"input_signal": _check_and_convert_input_signal(params),
         "action_to_apply_to_input_signal": action_to_apply_to_input_signal,
         **optional_params_core_attrs}

    global_symbol_table = globals()
    for param_name in optional_params_core_attrs:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        optional_params_core_attrs[param_name] = func_alias(params)

    kwargs = {"skip_validation_and_conversion": True,
              **optional_params_core_attrs}
    optional_params = optional_params_cls(**kwargs)

    return optional_params



_default_optional_params = None



def azimuthally_average(input_signal, optional_params=_default_optional_params):
    r"""Average azimuthally a given input 2D ``hyperspy`` signal.

    This Python function assumes that the input 2D ``hyperspy`` signal samples
    from a mathematical function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)`
    which is piecewise continuous in :math:`u_{x}` and :math:`u_{y}`, where
    :math:`u_{x}` and :math:`u_{y}` are the horizontal and vertical coordinates
    in the signal space of the input signal, and :math:`\mathbf{m}` is a vector
    of integers representing the navigation indices of the input signal. The
    Python function approximates the azimuthal average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the azimuthal average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
	&\overline{S}_{\mathbf{m}}\left(U_{r}=
        u_{r}\left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\frac{1}{2\pi}\int_{0}^{2\pi}du_{\phi}\,
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: azimuthal_average__2

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the azimuthal averaging.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalAzimuthalAveragingParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalAzimuthalAveragingParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalAzimuthalAveragingParams`, then the default
        values of the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.complex_signal1d.ComplexSignal1D`
        The output ``hyperspy`` signal that samples the azimuthal average of the
        input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "azimuthally_average"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _azimuthally_average(**kwargs)

    return output_signal



def _azimuthally_average(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    center = optional_params_core_attrs["center"]
    radial_range = optional_params_core_attrs["radial_range"]
    num_bins = optional_params_core_attrs["num_bins"]
    title = optional_params_core_attrs["title"]
    
    azimuthal_integrator = _construct_azimuthal_integrator(input_signal, center)

    func_alias = _apply_azimuthal_integrator_to_input_signal
    kwargs = {"azimuthal_integrator": azimuthal_integrator,
              "input_signal": input_signal,
              "num_bins": num_bins,
              "radial_range": radial_range}
    bin_coords, output_signal_data = func_alias(**kwargs)
    
    kwargs = {"data": output_signal_data,
              "metadata": input_signal.metadata.as_dictionary()}
    if np.isrealobj(output_signal_data):
        output_signal = hyperspy.signals.Signal1D(**kwargs)
    else:
        output_signal = hyperspy.signals.ComplexSignal1D(**kwargs)
    output_signal.metadata.set_item("General.title", title)

    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params,
              "bin_coords": bin_coords,
              "output_signal": output_signal}
    _update_output_signal_axes(**kwargs)

    return output_signal



def _construct_azimuthal_integrator(signal, center):
    detector = _construct_pyfai_detector(signal)

    h_scale = signal.axes_manager[-2].scale
    v_scale = signal.axes_manager[-1].scale

    # ``pone_1`` and ``poni_2`` are the vertical and horizontal displacements
    # of the reference point, from which to perform the azimuthal integration,
    # from the top left corner of the input signal.
    h_range, v_range = _calc_h_and_v_ranges(signal)
    poni_1 = center[1]-v_range[0] if (v_scale > 0) else v_range[1]-center[1]
    poni_2 = center[0]-h_range[0] if (h_scale > 0) else h_range[1]-center[0]

    # We require ``L >> max(v_pixel_size, h_pixel_size)``.
    h_pixel_size = abs(h_scale)
    v_pixel_size = abs(v_scale)
    L = 10000 * max(v_pixel_size, h_pixel_size)

    # ``integrators`` is an alias to a pyFAI submodule that was imported near
    # the top of the current file using the ``importlib.import_module``
    # function.
    AzimuthalIntegrator = integrators.AzimuthalIntegrator
    
    kwargs = {"dist": L,
              "poni1": poni_1,
              "poni2": poni_2,
              "detector": detector}
    azimuthal_integrator = AzimuthalIntegrator(**kwargs)

    return azimuthal_integrator
    


def _construct_pyfai_detector(signal):
    h_pixel_size = abs(signal.axes_manager[-2].scale)
    v_pixel_size = abs(signal.axes_manager[-1].scale)

    # ``detectors`` is an alias to a pyFAI submodule that was imported near the
    # top of the current file using the ``importlib.import_module`` function.
    Detector = detectors.Detector

    kwargs = {"pixel1": v_pixel_size, "pixel2": h_pixel_size}
    detector = Detector(**kwargs)

    return detector



def _apply_azimuthal_integrator_to_input_signal(azimuthal_integrator,
                                                input_signal,
                                                num_bins,
                                                radial_range):
    navigation_dims = input_signal.data.shape[:-2]
    output_signal_data_shape = navigation_dims + (num_bins,)
    output_signal_data = np.zeros(output_signal_data_shape,
                                  dtype=input_signal.data.dtype)

    num_patterns = int(np.prod(navigation_dims))
    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        input_signal_datasubset = input_signal.data[navigation_indices]

        func_alias = _apply_azimuthal_integrator_to_input_signal_datasubset
        kwargs = {"azimuthal_integrator": azimuthal_integrator,
                  "input_signal_datasubset": input_signal_datasubset,
                  "num_bins": num_bins,
                  "radial_range": radial_range}
        bin_coords, output_signal_datasubset = func_alias(**kwargs)
        output_signal_data[navigation_indices] = output_signal_datasubset
    
    bin_coords /= 1000  # Because of the artificial "r_mm" units.

    return bin_coords, output_signal_data



def _apply_azimuthal_integrator_to_input_signal_datasubset(
        azimuthal_integrator,
        input_signal_datasubset,
        num_bins,
        radial_range):
    # Need to multiply range by 1000 because of the units used in pyFAI's
    # azimuthal integrator.
    method_alias = azimuthal_integrator.integrate1d
    kwargs = {"npt": num_bins,
              "radial_range": (radial_range[0]*1000, radial_range[1]*1000),
              "unit": "r_mm"}

    if np.isrealobj(input_signal_datasubset):
        kwargs["data"] = input_signal_datasubset
        bin_coords, output_signal_datasubset = method_alias(**kwargs)
    else:
        kwargs["data"] = input_signal_datasubset.real
        bin_coords, real_output_signal_datasubset = method_alias(**kwargs)

        kwargs["data"] = input_signal_datasubset.imag
        bin_coords, imag_output_signal_datasubset = method_alias(**kwargs)

        output_signal_datasubset = (real_output_signal_datasubset
                                    + 1j*imag_output_signal_datasubset)

    return bin_coords, output_signal_datasubset



def _update_output_signal_axes(input_signal,
                               optional_params,
                               bin_coords,
                               output_signal):
    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params}
    output_signal_axes_names = _calc_output_signal_axes_names(**kwargs)
    output_signal_axes_units = _calc_output_signal_axes_units(**kwargs)

    kwargs["bin_coords"] = bin_coords
    output_signal_axes_offsets = _calc_output_signal_axes_offsets(**kwargs)
    output_signal_axes_scales = _calc_output_signal_axes_scales(**kwargs)

    num_axes = len(output_signal.data.shape)

    output_signal_axes_sizes = tuple(output_signal.axes_manager[idx].size
                                     for idx
                                     in range(num_axes))
        
    for axis_idx in range(num_axes):
        kwargs = {"size": output_signal_axes_sizes[axis_idx],
                  "scale": output_signal_axes_scales[axis_idx],
                  "offset": output_signal_axes_offsets[axis_idx],
                  "units": output_signal_axes_units[axis_idx]}
        new_output_signal_axis = hyperspy.axes.UniformDataAxis(**kwargs)

        name = output_signal_axes_names[axis_idx]
        units = output_signal_axes_units[axis_idx]
        
        output_signal.axes_manager[axis_idx].update_from(new_output_signal_axis)
        output_signal.axes_manager[axis_idx].name = name
        output_signal.axes_manager[axis_idx].units = units

    return None



def _calc_output_signal_axes_names(input_signal, optional_params):
    num_axes = len(input_signal.data.shape)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)

    input_signal_axes_names = tuple(input_signal.axes_manager[idx].name
                                    for idx
                                    in range(num_axes))
    input_signal_axes_units = tuple(input_signal.axes_manager[idx].units
                                    for idx
                                    in range(num_axes))

    if "num_bins" in optional_params_core_attrs:
        if "limits" in optional_params_core_attrs:
            unit_to_axis_name_map = {"Å": "$r$", "1/Å": "$k$"}

            args = (input_signal_axes_units[-1], "")
            output_signal_axis_name = unit_to_axis_name_map.get(*args)

            output_signal_axes_names = (input_signal_axes_names[:-1]
                                        + (output_signal_axis_name,))
        else:
            unit_to_axis_name_map = {"Å": "$r_{xy}$", "1/Å": "$k_{xy}$"}
            
            args = (input_signal_axes_units[-1], "")
            output_signal_axis_name = unit_to_axis_name_map.get(*args)
            
            output_signal_axes_names = (input_signal_axes_names[:-2]
                                        + (output_signal_axis_name,))
    else:
        output_signal_axes_names = input_signal_axes_names

    return output_signal_axes_names



def _calc_output_signal_axes_units(input_signal, optional_params):
    num_axes = len(input_signal.data.shape)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)

    input_signal_axes_units = tuple(input_signal.axes_manager[idx].units
                                    for idx
                                    in range(num_axes))

    if "num_bins" in optional_params_core_attrs:
        if "limits" in optional_params_core_attrs:
            output_signal_axes_units = input_signal_axes_units
        else:
            output_signal_axes_units = (input_signal_axes_units[:-2]
                                        + (input_signal_axes_units[-1],))
    else:
        output_signal_axes_units = input_signal_axes_units

    return output_signal_axes_units



def _calc_output_signal_axes_offsets(input_signal, optional_params, bin_coords):
    num_axes = len(input_signal.data.shape)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)

    input_signal_axes_offsets = tuple(input_signal.axes_manager[idx].offset
                                      for idx
                                      in range(num_axes))

    if "pad_mode" in optional_params_core_attrs:
        func_alias = _calc_output_signal_axes_offsets_resulting_from_crop
        kwargs = {"input_signal": input_signal,
                  "optional_params": optional_params}
        output_signal_axes_offsets = func_alias(**kwargs)
    elif "num_bins" in optional_params_core_attrs:
        if "limits" in optional_params_core_attrs:
            output_signal_axes_offsets = (input_signal_axes_offsets[:-1]
                                          + (bin_coords[0],))
        else:
            output_signal_axes_offsets = (input_signal_axes_offsets[:-2]
                                          + (bin_coords[0],))
    else:
        input_signal_axes_scales = tuple(input_signal.axes_manager[idx].scale
                                         for idx
                                         in range(num_axes))

        output_signal_axes_offsets = list(input_signal_axes_offsets)

        if "block_dims" in optional_params_core_attrs:
            block_dims = optional_params_core_attrs["block_dims"]
            
            for idx in (-2, -1):
                output_signal_axes_offsets[idx] += \
                    0.5*(block_dims[idx]-1)*input_signal_axes_scales[idx]
                
        else:
            for idx in (-2, -1):
                output_signal_axes_offsets[idx] = \
                    optional_params_core_attrs["new_signal_space_offsets"][idx]

        output_signal_axes_offsets = tuple(output_signal_axes_offsets)

    return output_signal_axes_offsets



def _calc_output_signal_axes_offsets_resulting_from_crop(input_signal,
                                                         optional_params):
    func_alias = _calc_input_signal_datasubset_cropping_params
    input_signal_datasubset_cropping_params = func_alias(input_signal,
                                                         optional_params)

    multi_dim_slice_for_cropping = \
        input_signal_datasubset_cropping_params["multi_dim_slice_for_cropping"]

    num_axes = len(input_signal.data.shape)

    input_signal_axes_scales = tuple(input_signal.axes_manager[idx].scale
                                     for idx
                                     in range(num_axes))
    input_signal_axes_offsets = tuple(input_signal.axes_manager[idx].offset
                                      for idx
                                      in range(num_axes))

    num_spatial_dims = len(multi_dim_slice_for_cropping)

    output_signal_axes_offsets = list(input_signal_axes_offsets)
    for spatial_dim_idx in range(num_spatial_dims):
        input_signal_axes_scale = \
            input_signal_axes_scales[-2+spatial_dim_idx]
        input_signal_axes_offset = \
            input_signal_axes_offsets[-2+spatial_dim_idx]
        
        single_dim_slice_for_cropping = \
            multi_dim_slice_for_cropping[-(spatial_dim_idx+1)]

        output_signal_axes_offset = \
            (input_signal_axes_offset
             + input_signal_axes_scale*single_dim_slice_for_cropping.start)
        output_signal_axes_offsets[-2+spatial_dim_idx] = \
            output_signal_axes_offset

    output_signal_axes_offsets = tuple(output_signal_axes_offsets)

    return output_signal_axes_offsets



def _calc_crop_window_center_in_pixel_coords(input_signal,
                                             approximate_crop_window_center):
    h_scale = input_signal.axes_manager[-2].scale
    v_scale = input_signal.axes_manager[-1].scale

    h_offset = input_signal.axes_manager[-2].offset
    v_offset = input_signal.axes_manager[-1].offset

    crop_window_center_in_pixel_coords = \
        tuple()
    crop_window_center_in_pixel_coords += \
        (round((approximate_crop_window_center[0]-h_offset) / h_scale),)
    crop_window_center_in_pixel_coords += \
        (round((approximate_crop_window_center[1]-v_offset) / v_scale),)

    return crop_window_center_in_pixel_coords



def _calc_output_signal_axes_scales(input_signal, optional_params, bin_coords):
    num_axes = len(input_signal.data.shape)

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)

    input_signal_axes_scales = tuple(input_signal.axes_manager[idx].scale
                                     for idx
                                     in range(num_axes))

    if "pad_mode" in optional_params_core_attrs:
        output_signal_axes_scales = input_signal_axes_scales
    elif "num_bins" in optional_params_core_attrs:
        if "limits" in optional_params_core_attrs:
            output_signal_axes_scales = (input_signal_axes_scales[:-1]
                                         + (bin_coords[1]-bin_coords[0],))
        else:
            output_signal_axes_scales = (input_signal_axes_scales[:-2]
                                         + (bin_coords[1]-bin_coords[0],))
    else:
        output_signal_axes_scales = list(input_signal_axes_scales)

        if "block_dims" in optional_params_core_attrs:
            block_dims = optional_params_core_attrs["block_dims"]
            
            for idx in (-2, -1):
                output_signal_axes_scales[idx] *= \
                    block_dims[idx]
                
        else:
            for idx in (-2, -1):
                output_signal_axes_scales[idx] = \
                    optional_params_core_attrs["new_signal_space_scales"][idx]

        output_signal_axes_scales = tuple(output_signal_axes_scales)

    return output_signal_axes_scales



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalAzimuthalIntegrationParams(_cls_alias):
    r"""The set of optional parameters for the function
    :func:`empix.azimuthally_integrate`.

    The Python function :func:`empix.azimuthally_integrate` integrates
    azimuthally a given input 2D ``hyperspy`` signal. The Python function
    assumes that the input 2D ``hyperspy`` signal samples from a mathematical
    function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` which is piecewise
    continuous in :math:`u_{x}` and :math:`u_{y}`, where :math:`u_{x}` and
    :math:`u_{y}` are the horizontal and vertical coordinates in the signal
    space of the input signal, and :math:`\mathbf{m}` is a vector of integers
    representing the navigation indices of the input signal. The Python function
    approximates the azimuthal integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the azimuthal integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
        &S_{\mathbf{m}}\left(U_{r}=
        u_{r}\left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\int_{0}^{2\pi}du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: azimuthal_integral__1

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the azimuthal integration.

    Parameters
    ----------
    center : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``center`` is set to ``None``, then the reference point
        :math:`\left(c_{x},c_{y}\right)`, from which the radial distance is
        defined for the azimuthal integration, is set to the signal space
        coordinates corresponding to the center signal space pixel.  Otherwise,
        if ``center`` is set to a pair of floating-point numbers, then
        ``center[0]`` and ``center[1]`` specify :math:`c_{x}` and :math:`c_{y}`
        respectively, in the same units of the corresponding signal space axes
        of the input signal.
    radial_range : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``radial_range`` is set to ``None``, then the radial range, over
        which the azimuthal integration is performed, is from zero to the largest
        radial distance within the signal space boundaries of the input signal
        for all azimuthal angles. Otherwise, if ``radial_range`` is set to a
        pair of floating-point numbers, then ``radial_range[0]`` and
        ``radial_range[1]`` specify the minimum and maximum radial distances of
        the radial range respectively, in the same units of the horizontal and
        vertical axes respectively of the signal space of the input signal. Note
        that in this case ``radial_range`` must satisfy
        ``0<=radial_range[0]<radial_range[1]``. Moreover, the function
        represented by the input signal is assumed to be equal to zero
        everywhere outside of the signal space boundaries of said input signal.
    num_bins : `int` | `None`, optional
        ``num_bins`` must either be a positive integer or of the `NoneType`: if
        the former, then the dimension of the signal space of the output signal
        ``output_signal`` is set to ``num_bins``; if the latter, then the
        dimension of the signal space of ``output_signal`` is set to
        ``min(input_signal.data.shape[-2:])``, where ``input_signal`` is the
        input ``hyperspy`` signal.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Azimuthally Integrated " +
        input_signal.metadata.General.title``, where ``input_signal`` is the 
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("center", "radial_range", "num_bins", "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 center=\
                 _default_center,
                 radial_range=\
                 _default_radial_range,
                 num_bins=\
                 _default_num_bins,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def azimuthally_integrate(input_signal,
                          optional_params=_default_optional_params):
    r"""Integrate azimuthally a given input 2D ``hyperspy`` signal.

    This Python function assumes that the input 2D ``hyperspy`` signal samples
    from a mathematical function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)`
    which is piecewise continuous in :math:`u_{x}` and :math:`u_{y}`, where
    :math:`u_{x}` and :math:`u_{y}` are the horizontal and vertical coordinates
    in the signal space of the input signal, and :math:`\mathbf{m}` is a vector
    of integers representing the navigation indices of the input signal. The
    Python function approximates the azimuthal integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the azimuthal integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
        &S_{\mathbf{m}}\left(U_{r}=
        u_{r}\left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\int_{0}^{2\pi}du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: azimuthal_integral__2

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the azimuthal integration.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalAzimuthalIntegrationParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalAzimuthalIntegrationParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalAzimuthalIntegrationParams`, then the default
        values of the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.complex_signal1d.ComplexSignal1D`
        The output ``hyperspy`` signal that samples the azimuthal integral of
        the input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "azimuthally_integrate"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _azimuthally_integrate(**kwargs)

    return output_signal



def _azimuthally_integrate(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    
    kwargs = {"skip_validation_and_conversion": True,
              **optional_params_core_attrs}
    optional_params = OptionalAzimuthalIntegrationParams(**kwargs)

    output_signal = _azimuthally_average(input_signal, optional_params)
    
    bin_coords = _calc_bin_coords_from_signal(signal=output_signal)
    navigation_rank = len(output_signal.data.shape) - 1

    for idx, r_xy in enumerate(bin_coords):
        multi_dim_slice = tuple([slice(None)]*navigation_rank + [idx])
        output_signal.data[multi_dim_slice] *= 2*np.pi*r_xy

    return output_signal



def _calc_bin_coords_from_signal(signal):
    offset = signal.axes_manager[-1].offset
    scale = signal.axes_manager[-1].scale
    size = signal.axes_manager[-1].size
    bin_coords = np.arange(offset, offset + size*scale - 1e-10, scale)

    return bin_coords



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalAnnularAveragingParams(_cls_alias):
    r"""The set of optional parameters for the function
    :func:`empix.annularly_average`.

    The Python function :func:`empix.annularly_average` averages annularly a
    given input 2D ``hyperspy`` signal. The Python function assumes that the
    input 2D ``hyperspy`` signal samples from a mathematical function
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` which is piecewise continuous
    in :math:`u_{x}` and :math:`u_{y}`, where :math:`u_{x}` and :math:`u_{y}`
    are the horizontal and vertical coordinates in the signal space of the input
    signal, and :math:`\mathbf{m}` is a vector of integers representing the
    navigation indices of the input signal. The Python function approximates the
    azimuthal average of :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given
    the input signal. We define the annular average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
	&\overline{S}_{\mathbf{m}}\left(u_{r,i}\le U_{r}<u_{r,f}
        \left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\frac{1}{\pi\left(u_{r,f}^{2}-u_{r,i}^{2}\right)}
        \int_{u_{r,i}}^{u_{r,f}}du_{r}\,\int_{0}^{2\pi}du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: annular_average__1

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the annular averaging.

    Parameters
    ----------
    center : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``center`` is set to ``None``, then the reference point
        :math:`\left(c_{x},c_{y}\right)`, from which the radial distance is
        defined for the annular averaging, is set to the signal space
        coordinates corresponding to the center signal space pixel.  Otherwise,
        if ``center`` is set to a pair of floating-point numbers, then
        ``center[0]`` and ``center[1]`` specify :math:`c_{x}` and :math:`c_{y}`
        respectively, in the same units of the corresponding signal space axes
        of the input signal.
    radial_range : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``radial_range`` is set to ``None``, then the radial range, over
        which the annular averaging is performed, is from zero to the largest
        radial distance within the signal space boundaries of the input signal
        for all azimuthal angles. Otherwise, if ``radial_range`` is set to a
        pair of floating-point numbers, then ``radial_range[0]`` and
        ``radial_range[1]`` specify the minimum and maximum radial distances of
        the radial range respectively, in the same units of the horizontal and
        vertical axes respectively of the signal space of the input signal. Note
        that in this case ``radial_range`` must satisfy
        ``0<=radial_range[0]<radial_range[1]``. Moreover, the function
        represented by the input signal is assumed to be equal to zero
        everywhere outside of the signal space boundaries of said input signal.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Annularly Averaged " +
        input_signal.metadata.General.title``, where ``input_signal`` is the 
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("center", "radial_range", "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 center=\
                 _default_center,
                 radial_range=\
                 _default_radial_range,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def annularly_average(input_signal, optional_params=_default_optional_params):
    r"""Average annularly a given input 2D ``hyperspy`` signal.

    This Python function assumes that the input 2D ``hyperspy`` signal samples
    from a mathematical function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)`
    which is piecewise continuous in :math:`u_{x}` and :math:`u_{y}`, where
    :math:`u_{x}` and :math:`u_{y}` are the horizontal and vertical coordinates
    in the signal space of the input signal, and :math:`\mathbf{m}` is a vector
    of integers representing the navigation indices of the input signal. The
    Python function approximates the annular average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the annular average of :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)`
    as

    .. math ::
	&\overline{S}_{\mathbf{m}}\left(u_{r,i}\le U_{r}<u_{r,f}
        \left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\frac{1}{\pi\left(u_{r,f}^{2}-u_{r,i}^{2}\right)}
        \int_{u_{r,i}}^{u_{r,f}}du_{r}\,\int_{0}^{2\pi}du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: annular_average__2

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the annular averaging.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalAnnularAveragingParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalAnnularAveragingParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalAnnularAveragingParams`, then the default values 
        of the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy.signal.BaseSignal` | :class:`hyperspy._signals.complex_signal.ComplexSignal`
        The output ``hyperspy`` signal that samples the annular average of the
        input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "annularly_average"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _annularly_average(**kwargs)

    return output_signal



def _annularly_average(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    optional_params_core_attrs["num_bins"] = 2*min(input_signal.data.shape[-2:])

    kwargs = {"skip_validation_and_conversion": True,
              **optional_params_core_attrs}
    optional_params = OptionalAzimuthalIntegrationParams(**kwargs)
    
    output_signal = _azimuthally_integrate(input_signal, optional_params)

    r_xy_i, r_xy_f = optional_params_core_attrs["radial_range"]
    area_of_annulus = np.pi*(r_xy_f**2 - r_xy_i**2)
    
    r_xy_scale = output_signal.axes_manager[-1].scale

    output_signal = output_signal.sum(axis=-1)
    output_signal.data *= (r_xy_scale/area_of_annulus)

    return output_signal



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalAnnularIntegrationParams(_cls_alias):
    r"""The set of optional parameters for the function
    :func:`empix.annularly_integrate`.

    The Python function :func:`empix.annularly_integrate` integrates annularly a
    given input 2D ``hyperspy`` signal. The Python function assumes that the
    input 2D ``hyperspy`` signal samples from a mathematical function
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` which is piecewise continuous
    in :math:`u_{x}` and :math:`u_{y}`, where :math:`u_{x}` and :math:`u_{y}`
    are the horizontal and vertical coordinates in the signal space of the input
    signal, and :math:`\mathbf{m}` is a vector of integers representing the
    navigation indices of the input signal. The Python function approximates the
    azimuthal average of :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given
    the input signal. We define the annular average of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
        &S_{\mathbf{m}}\left(u_{r,i}\le U_{r}<u_{r,f}
        \left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\int_{u_{r,i}}^{u_{r,f}}du_{r}\,\int_{0}^{2\pi}
        du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: annular_integral__1

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`u_r` is defined for the annular integration.

    Parameters
    ----------
    center : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``center`` is set to ``None``, then the reference point
        :math:`\left(c_{x},c_{y}\right)`, from which the radial distance is
        defined for the annular integration, is set to the signal space
        coordinates corresponding to the center signal space pixel.  Otherwise,
        if ``center`` is set to a pair of floating-point numbers, then
        ``center[0]`` and ``center[1]`` specify :math:`c_{x}` and :math:`c_{y}`
        respectively, in the same units of the corresponding signal space axes
        of the input signal.
    radial_range : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``radial_range`` is set to ``None``, then the radial range, over
        which the annular integration is performed, is from zero to the largest
        radial distance within the signal space boundaries of the input signal
        for all azimuthal angles. Otherwise, if ``radial_range`` is set to a
        pair of floating-point numbers, then ``radial_range[0]`` and
        ``radial_range[1]`` specify the minimum and maximum radial distances of
        the radial range respectively, in the same units of the horizontal and
        vertical axes respectively of the signal space of the input signal. Note
        that in this case ``radial_range`` must satisfy
        ``0<=radial_range[0]<radial_range[1]``. Moreover, the function
        represented by the input signal is assumed to be equal to zero
        everywhere outside of the signal space boundaries of said input signal.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Annularly Integrated " +
        input_signal.metadata.General.title``, where ``input_signal`` is the 
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("center", "radial_range", "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 center=\
                 _default_center,
                 radial_range=\
                 _default_radial_range,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def annularly_integrate(input_signal, optional_params=_default_optional_params):
    r"""Integrate annularly a given input 2D ``hyperspy`` signal.

    This Python function assumes that the input 2D ``hyperspy`` signal samples
    from a mathematical function :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)`
    which is piecewise continuous in :math:`u_{x}` and :math:`u_{y}`, where
    :math:`u_{x}` and :math:`u_{y}` are the horizontal and vertical coordinates
    in the signal space of the input signal, and :math:`\mathbf{m}` is a vector
    of integers representing the navigation indices of the input signal. The
    Python function approximates the annular integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` given the input signal. We
    define the annular integral of
    :math:`F_{\mathbf{m}}\left(u_{x},u_{y}\right)` as

    .. math ::
	&S_{\mathbf{m}}\left(u_{r,i}\le U_{r}<u_{r,f}
        \left|0\le U_{\phi}<2\pi;c_{x},c_{y}\right.\right)
        \\&\quad=\int_{u_{r,i}}^{u_{r,f}}du_{r}\,\int_{0}^{2\pi}
        du_{\phi}\,u_{r}
        F_{\mathbf{m}}\left(c_{x}+u_{r}\cos\left(u_{\phi}\right),
        c_{y}+u_{r}\sin\left(u_{\phi}\right)\right),
        :label: annular_integral__2

    where :math:`\left(c_{x},c_{y}\right)` is the reference point from which the
    radial distance :math:`` is defined for the annular integration.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalAnnularIntegrationParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalAnnularIntegrationParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalAnnularIntegrationParams`, then the default values
        of the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy.signal.BaseSignal` | :class:`hyperspy._signals.complex_signal.ComplexSignal`
        The output ``hyperspy`` signal that samples the annular integral of the
        input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "annularly_integrate"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _annularly_integrate(**kwargs)

    return output_signal



def _annularly_integrate(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    optional_params_core_attrs["num_bins"] = 2*min(input_signal.data.shape[-2:])

    kwargs = {"skip_validation_and_conversion": True,
              **optional_params_core_attrs}
    optional_params = OptionalAzimuthalIntegrationParams(**kwargs)
    
    output_signal = _azimuthally_integrate(input_signal, optional_params)
    
    r_xy_scale = output_signal.axes_manager[-1].scale
    
    output_signal = output_signal.sum(axis=-1)
    output_signal.data *= r_xy_scale

    return output_signal



def _check_and_convert_limits(params):
    obj_name = "limits"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)
    
    current_func_name = "_check_and_convert_limits"

    if obj is not None:
        try:
            kwargs = {"obj": obj, "obj_name": obj_name}
            limits = czekitout.convert.to_pair_of_floats(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)

        if limits[0] == limits[1]:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise ValueError(err_msg)
    else:
        if input_signal is not None:
            u_coords = _calc_u_coords_1d(signal=input_signal)
            u_i = np.amin(u_coords)
            u_f = np.amax(u_coords)
            limits = (u_i, u_f)
        else:
            limits = obj

    return limits



def _calc_u_coords_1d(signal):
    offset = signal.axes_manager[-1].offset
    scale = signal.axes_manager[-1].scale
    size = signal.axes_manager[-1].size
    u_coords = offset + scale*np.arange(size)

    return u_coords



def _pre_serialize_limits(limits):
    obj_to_pre_serialize = limits
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_limits(serializable_rep):
    limits = serializable_rep

    return limits



def _check_and_convert_normalize(params):
    obj_name = "normalize"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    normalize = czekitout.convert.to_bool(**kwargs)

    return normalize



def _pre_serialize_normalize(normalize):
    obj_to_pre_serialize = normalize
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_normalize(serializable_rep):
    normalize = serializable_rep

    return normalize



_default_limits = None
_default_normalize = False



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalCumulative1dIntegrationParams(_cls_alias):
    r"""The set of optional parameters for the function
    :func:`empix.cumulatively_integrate_1d`.

    The Python function :func:`empix.cumulatively_integrate_1d` integrates
    cumulatively a given input 1D ``hyperspy`` signal. The Python function
    assumes that the input 1D ``hyperspy`` signal samples from a mathematical
    function :math:`F_{\mathbf{m}}\left(u\right)` which is piecewise continuous
    in :math:`u`, where :math:`u` is the signal space coordinate of the input
    signal, and :math:`\mathbf{m}` is a vector of integers representing the
    navigation indices of the input signal. The Python function approximates the
    cumulative integral of :math:`F_{\mathbf{m}}\left(u\right)` given the input
    signal. We define the cumulative integral of
    :math:`F_{\mathbf{m}}\left(u\right)` as

    .. math ::
        \text{CDF}_{\text{1D}}\left(u\right)&=\frac{1}{\Gamma}
        \int_{u_{i}}^{u}du^{\prime}\,F_{\mathbf{m}}\left(u^{\prime}\right),
        \\&\quad 
        u\in\left[\min\left(u_{i},u_{f}\right),
        \max\left(u_{i},u_{f}\right)\right],
        :label: cumulative_integral_1d__1

    where

    .. math ::
        \Gamma=\begin{cases}
        1, & \text{if }\mathcal{N}\le 10^{-10} \text{ or }
        \text{normalize}=\text{False},
        \\\left|\int_{u_{i}}^{u_{f}}du^{\prime}\,
        F_{\mathbf{m}}\left(u^{\prime}\right)\right|, & \text{otherwise},
        \end{cases}
        :label: Gamma_of_cumulative_integral_1d__1

    .. math ::
        \mathcal{N}=\left|\int_{u_{i}}^{u_{f}}du^{\prime}
        \,F_{\mathbf{m}}\left(u^{\prime}\right)\right|,
        :label: N_of_cumulative_integral_1d__1

    :math:`u_i` and :math:`u_f` specify the interval over which cumulative
    integration is performed, the interval being
    :math:`\left[\min\left(u_{i},u_{f}\right),
    \max\left(u_{i},u_{f}\right)\right]`, and ``normalize`` is an optional
    boolean parameter that determines whether normalization is enabled or not.

    Parameters
    ----------
    limits : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``limits`` is set to ``None``, then the cumulative integration is
        performed over the entire input signal, with :math:`u_i<u_f`. Otherwise,
        if ``limits`` is set to a pair of floating-point numbers, then
        ``limits[0]`` and ``limits[1]`` are :math:`u_i` and :math:`u_f`
        respectively, in the same units of the signal space coordinate
        :math:`u`. Note that the function represented by the input signal is
        assumed to be equal to zero everywhere outside of the bounds of said
        input signal.
    num_bins : `int` | `None`, optional
        ``num_bins`` must either be a positive integer or of the `NoneType`: if
        the former, then the dimension of the signal space of the output signal
        ``output_signal`` is set to ``num_bins``; if the latter, then the
        dimension of the signal space of ``output_signal`` is set to
        ``input_signal.data[-1]``, where ``input_signal`` is the input
        ``hyperspy`` signal.
    normalize : `bool`, optional
        The boolean optional parameter referenced in 
        Eq. :eq:`Gamma_of_cumulative_integral_1d__1`.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"CDF("+
        input_signal.metadata.General.title+")"``, where ``input_signal`` is the
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of 
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("limits", "num_bins", "normalize", "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 limits=\
                 _default_limits,
                 num_bins=\
                 _default_num_bins,
                 normalize=\
                 _default_normalize,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def cumulatively_integrate_1d(input_signal,
                              optional_params=_default_optional_params):
    r"""Integrate cumulatively a given input 1D ``hyperspy`` signal.

    This Python function assumes that the input 1D ``hyperspy`` signal samples
    from a mathematical function :math:`F_{\mathbf{m}}\left(u\right)` which is
    piecewise continuous in :math:`u`, where :math:`u` is the signal space
    coordinate of the input signal, and :math:`\mathbf{m}` is a vector of
    integers representing the navigation indices of the input signal. The Python
    function approximates the cumulative integral of
    :math:`F_{\mathbf{m}}\left(u\right)` given the input signal. We define the
    cumulative integral of :math:`F_{\mathbf{m}}\left(u\right)` as

    .. math ::
        \text{CDF}_{\text{1D}}\left(u\right)&=\frac{1}{\Gamma}
        \int_{u_{i}}^{u}du^{\prime}\,F_{\mathbf{m}}\left(u^{\prime}\right),
        \\&\quad 
        u\in\left[\min\left(u_{i},u_{f}\right),
        \max\left(u_{i},u_{f}\right)\right],
        :label: cumulative_integral_1d__2

    where

    .. math ::
        \Gamma=\begin{cases}
        1, & \text{if }\mathcal{N}\le 10^{-10} \text{ or }
        \text{normalize}=\text{False},
        \\\left|\int_{u_{i}}^{u_{f}}du^{\prime}\,
        F_{\mathbf{m}}\left(u^{\prime}\right)\right|, & \text{otherwise},
        \end{cases}
        :label: Gamma_of_cumulative_integral_1d__2

    .. math ::
        \mathcal{N}=\left|\int_{u_{i}}^{u_{f}}du^{\prime}
        \,F_{\mathbf{m}}\left(u^{\prime}\right)\right|,
        :label: N_of_cumulative_integral_1d__2

    :math:`u_i` and :math:`u_f` specify the interval over which cumulative
    integration is performed, the interval being
    :math:`\left[\min\left(u_{i},u_{f}\right),
    \max\left(u_{i},u_{f}\right)\right]`, and ``normalize`` is an optional
    boolean parameter that determines whether normalization is enabled or not.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.complex_signal1d.ComplexSignal1D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalCumulative1dIntegrationParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalCumulative1dIntegrationParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalCumulative1dIntegrationParams`, then the default 
        values of the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal1d.Signal1D` | :class:`hyperspy._signals.complex_signal1d.ComplexSignal1D`
        The output ``hyperspy`` signal that samples the cumulative integral of 
        the input signal ``input_signal``. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "cumulatively_integrate_1d"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _cumulatively_integrate_1d(**kwargs)

    return output_signal



def _cumulatively_integrate_1d(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    limits = optional_params_core_attrs["limits"]
    num_bins = optional_params_core_attrs["num_bins"]
    normalize = optional_params_core_attrs["normalize"]
    title = optional_params_core_attrs["title"]

    u_coords = \
        _calc_u_coords_1d(signal=input_signal)
    beg_u_coord_idx, end_u_coord_idx = \
        _calc_beg_and_end_u_coord_indices(u_coords, limits)

    navigation_dims = input_signal.data.shape[:-1]
    output_signal_data_shape = navigation_dims + (num_bins,)
    output_signal_data = np.zeros(output_signal_data_shape,
                                  dtype=input_signal.data.dtype)

    num_patterns = int(np.prod(navigation_dims))
    for pattern_idx in range(num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        input_signal_datasubset = input_signal.data[navigation_indices]
            
        kwargs = \
            {"input_signal_datasubset": input_signal_datasubset,
             "u_coords": u_coords,
             "beg_u_coord_idx": beg_u_coord_idx,
             "end_u_coord_idx": end_u_coord_idx,
             "limits": limits,
             "num_bins": num_bins,
             "normalize": normalize}
        bin_coords, output_signal_datasubset = \
            _cumulatively_integrate_input_signal_datasubset(**kwargs)
        output_signal_data[navigation_indices] = \
            output_signal_datasubset
        
    kwargs = {"data": output_signal_data,
              "metadata": input_signal.metadata.as_dictionary()}
    if np.isrealobj(output_signal_data):
        output_signal = hyperspy.signals.Signal1D(**kwargs)
    else:
        output_signal = hyperspy.signals.ComplexSignal1D(**kwargs)
    output_signal.metadata.set_item("General.title", title)
        
    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params,
              "bin_coords": bin_coords,
              "output_signal": output_signal}
    _update_output_signal_axes(**kwargs)

    return output_signal



def _calc_beg_and_end_u_coord_indices(u_coords, limits):
    d_u = u_coords[1]-u_coords[0]
    
    idx_1 = np.abs(u_coords-min(limits)).argmin()
    idx_1 = max(idx_1-1, 0) if (d_u > 0) else min(idx_1+1, u_coords.size-1)
    
    idx_2 = np.abs(u_coords-max(limits)).argmin()
    idx_2 = min(idx_2+1, u_coords.size-1) if d_u > 0 else max(idx_2-1, 0)
    
    beg_u_coord_idx = min(idx_1, idx_2)
    end_u_coord_idx = max(idx_1, idx_2)

    return beg_u_coord_idx, end_u_coord_idx



def _cumulatively_integrate_input_signal_datasubset(input_signal_datasubset,
                                                    u_coords,
                                                    beg_u_coord_idx,
                                                    end_u_coord_idx,
                                                    limits,
                                                    num_bins,
                                                    normalize):
    d_u = u_coords[1]-u_coords[0]
    x = u_coords[beg_u_coord_idx:end_u_coord_idx+1]
    y = input_signal_datasubset[beg_u_coord_idx:end_u_coord_idx+1]

    if d_u < 0:
        x = x[::-1]
        y = y[::-1]

    kwargs = {"x": x,
              "y": y,
              "kind": "cubic",
              "copy": False,
              "bounds_error": False,
              "fill_value": 0,
              "assume_sorted": True}
    F = scipy.interpolate.interp1d(**kwargs)

    u_i, u_f = limits
    bin_coords = np.linspace(u_i, u_f, num_bins)
    F_data = F(bin_coords)

    output_signal_datasubset = (bin_coords[1]-bin_coords[0]) * np.cumsum(F_data)

    tol = 1e-10
    N = abs(output_signal_datasubset[-1].item())
    normalize = (not bool((N <= tol) + (normalize == False)))
    Gamma = normalize*(N-1.0) + 1.0

    output_signal_datasubset /= Gamma

    return bin_coords, output_signal_datasubset



def _check_and_convert_window_dims(params):
    obj_name = "window_dims"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)
    
    current_func_name = "_check_and_convert_window_dims"

    if obj is not None:
        try:
            kwargs = {"obj": obj, "obj_name": obj_name}
            window_dims = czekitout.convert.to_pair_of_positive_ints(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)
    else:
        if input_signal is not None:
            N_v, N_h = input_signal.data.shape[-2:]
            window_dims = (N_h, N_v)
        else:
            window_dims = obj

    return window_dims



def _pre_serialize_window_dims(window_dims):
    obj_to_pre_serialize = window_dims
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_window_dims(serializable_rep):
    window_dims = serializable_rep

    return window_dims



def _check_and_convert_pad_mode(params):
    obj_name = "pad_mode"
    obj = params[obj_name]

    kwargs = {"obj": obj, "obj_name": obj_name}
    pad_mode = czekitout.convert.to_str_from_str_like(**kwargs)

    kwargs["accepted_strings"] = ("no-padding", "wrap", "zeros")
    czekitout.check.if_one_of_any_accepted_strings(**kwargs)

    return pad_mode



def _pre_serialize_pad_mode(pad_mode):
    obj_to_pre_serialize = pad_mode
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_pad_mode(serializable_rep):
    pad_mode = serializable_rep

    return pad_mode



def _check_and_convert_apply_symmetric_mask(params):
    obj_name = "apply_symmetric_mask"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    apply_symmetric_mask = czekitout.convert.to_bool(**kwargs)

    return apply_symmetric_mask



def _pre_serialize_apply_symmetric_mask(apply_symmetric_mask):
    obj_to_pre_serialize = apply_symmetric_mask
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_apply_symmetric_mask(serializable_rep):
    apply_symmetric_mask = serializable_rep

    return apply_symmetric_mask



_default_window_dims = None
_default_pad_mode = "no-padding"
_default_apply_symmetric_mask = False



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalCroppingParams(_cls_alias):
    r"""The set of optional parameters for the function :func:`empix.crop`.

    The Python function :func:`empix.crop` applies a series of optional
    transformations to a given input 2D ``hyperspy`` signal. Let us denote the
    input 2D ``hyperspy`` signal by :math:`F_{\mathbf{m}; l_x, l_y}`, where
    :math:`l_x` and :math:`l_y` are integers indexing the sampled horizontal and
    vertical coordinates respectively in the signal space of the input signal,
    and :math:`\mathbf{m}` is a vector of integers representing the navigation
    indices of the input signal. The Python function effectively does the
    following:

    1. Copies the input signal and optionally pads the copy along the horizontal
    and vertical axes in signal space according to the parameter ``pad_mode``;

    2. Constructs a cropping window in the signal space of the (optionally
    padded) copy of the input signal, with the cropping window dimensions being
    determined by the parameter ``window_dims``;

    3. Shifts the center of the cropping window to coordinates determined by the
    parameter ``center``;

    4. Shifts the center of the cropping window again to the coordinates of the
    pixel closest to the aforementioned coordinates in the previous step;

    5. Crops the (optionally padded) copy of the input signal along the
    horizontal and vertical dimensions of the signal space according to the
    placement of the cropping window in the previous two steps;

    6. Optionally applies a symmetric mask to the cropped signal resulting from
    the previous step according to the parameter ``apply_symmetric_mask``.

    See the description below of the optional parameters for more details.

    Parameters
    ----------
    center : `array_like` (`float`, shape=(2,)) | `None`, optional
        If ``center`` is set to ``None``, then the center of the cropping window
        is set to the signal space coordinates corresponding to the pixel that
        is ``(h_dim+1)//2 -1`` pixels to the right of the upper left corner in
        signal space, and ``(v_dim+1)//2-1`` pixels below the same corner, where
        ``h_dim`` and ``v_dim`` are the horizontal and vertical dimensions of
        the signal space. Otherwise, if ``center`` is set to a pair of
        floating-point numbers, then ``center[0]`` and ``center[1]`` specify the
        horizontal and vertical signal space coordinates of the center of the
        cropping window prior to the subpixel shift to the nearest pixel, in the
        same units of the corresponding axes of the input signal.

        We define the center of the cropping window to be ``(N_W_h+1)//2 - 1``
        pixels to the right of the upper left corner of the cropping window, and
        ``(N_W_v+1)//2 - 1`` pixels below the same corner, where ``N_W_h`` and
        ``N_W_v`` are the horizontal and vertical dimensions of the cropping 
        window in units of pixels.
    window_dims : `array_like` (`int`, shape=(2,)) | `None`, optional
        If ``window_dims`` is set to ``None``, then the dimensions of the
        cropping window are set to the dimensions of the signal space of the
        input signal.  Otherwise, if ``window_dims`` is set to a pair of
        positive integers, then ``window_dims[0]`` and ``window_dims[1]``
        specify the horizontal and vertical dimensions of the cropping window in
        units of pixels.
    pad_mode : ``"no-padding"`` | ``"wrap"`` | ``"zeros"``, optional
        If ``pad_mode`` is set to ``"no-padding"``, then no padding is performed
        prior to the crop. If ``pad_mode`` is set to ``"wrap"``, then the copy
        of the input signal is effectively padded along the horizontal and
        vertical axes in signal space by tiling the copy both horizontally and
        vertically in signal space such that the cropping window lies completely
        within the signal space boundaries of the resulting padded signal upon
        performing the crop. If ``pad_mode`` is set to ``"zeros"``, then the
        copy of the input signal is effectively padded with zeros such that the
        cropping window lies completely within the signal space boundaries of
        the resulting padded signal upon performing the crop.
    apply_symmetric_mask : `bool`, optional
        If ``apply_symmetric_mask`` is set to ``True`` and ``pad_mode`` to
        ``"zeros"``, then for every signal space pixel in the cropped signal
        that has a value of zero due to padding and a corresponding pixel with
        coordinates equal to the former after a rotation of 180 degrees about
        the center of the cropped signal, the latter i.e. the aforementioned
        corresponding pixel is effectively set to zero. The effective procedure
        is equivalent to applying a symmetric mask. Otherwise, no mask is
        effectively applied after cropping.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Cropped "+
        input_signal.metadata.General.title``, where ``input_signal`` is the
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("center",
                        "window_dims",
                        "pad_mode",
                        "apply_symmetric_mask",
                        "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 center=\
                 _default_center,
                 window_dims=\
                 _default_window_dims,
                 pad_mode=\
                 _default_pad_mode,
                 apply_symmetric_mask=\
                 _default_apply_symmetric_mask,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def crop(input_signal, optional_params=_default_optional_params):
    r"""Crop a given input 2D ``hyperspy`` signal.

    This Python function applies a series of optional transformations to a given
    input 2D ``hyperspy`` signal. Let us denote the input 2D ``hyperspy`` signal
    by :math:`F_{\mathbf{m}; l_x, l_y}`, where :math:`l_x` and :math:`l_y` are
    integers indexing the sampled horizontal and vertical coordinates
    respectively in the signal space of the input signal, and :math:`\mathbf{m}`
    is a vector of integers representing the navigation indices of the input
    signal. The Python function effectively does the following:

    1. Copies the input signal and optionally pads the copy along the horizontal
    and vertical axes in signal space according to the parameter ``pad_mode``;

    2. Constructs a cropping window in the signal space of the (optionally
    padded) copy of the input signal, with the cropping window dimensions being
    determined by the parameter ``window_dims``;

    3. Shifts the center of the cropping window to coordinates determined by the
    parameter ``center``;

    4. Shifts the center of the cropping window again to the coordinates of the
    pixel closest to the aforementioned coordinates in the previous step;

    5. Crops the (optionally padded) copy of the input signal along the
    horizontal and vertical dimensions of the signal space according to the
    placement of the cropping window in the previous two steps;

    6. Optionally applies a symmetric mask to the cropped signal resulting from
    the previous step according to the parameter ``apply_symmetric_mask``.

    See the description below of the optional parameters for more details.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalCroppingParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalCroppingParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalCroppingParams`, then the default values of the
        optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The output ``hyperspy`` signal that results from the applied
        transformations, described above. Note that the metadata of the input 
        signal is copied over to the output signal, with the title being 
        overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "crop"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _crop(**kwargs)

    return output_signal



def _crop(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    title = optional_params_core_attrs["title"]

    func_alias = _calc_input_signal_datasubset_cropping_params
    input_signal_datasubset_cropping_params = func_alias(input_signal,
                                                         optional_params)
    
    navigation_dims = input_signal.data.shape[:-2]
    num_patterns = int(np.prod(navigation_dims))

    current_func_name = "_crop"

    for pattern_idx in range(0, num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        input_signal_datasubset = input_signal.data[navigation_indices]
            
        kwargs = {"input_signal_datasubset": \
                  input_signal_datasubset,
                  "input_signal_datasubset_cropping_params": \
                  input_signal_datasubset_cropping_params}
        output_signal_datasubset = _crop_input_signal_datasubset(**kwargs)

        if pattern_idx == 0:
            output_signal_data_shape = (navigation_dims
                                        + output_signal_datasubset.shape)
            output_signal_data = np.zeros(output_signal_data_shape,
                                          dtype=input_signal.data.dtype)

            if np.prod(output_signal_data.shape) == 0:
                err_msg = globals()[current_func_name+"_err_msg_1"]
                raise ValueError(err_msg)

        output_signal_data[navigation_indices] = output_signal_datasubset
        
    kwargs = {"data": output_signal_data,
              "metadata": input_signal.metadata.as_dictionary()}
    if np.isrealobj(output_signal_data):
        output_signal = hyperspy.signals.Signal2D(**kwargs)
    else:
        output_signal = hyperspy.signals.ComplexSignal2D(**kwargs)
    output_signal.metadata.set_item("General.title", title)

    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params,
              "bin_coords": None,
              "output_signal": output_signal}
    _update_output_signal_axes(**kwargs)

    return output_signal



def _calc_input_signal_datasubset_cropping_params(input_signal,
                                                  optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    approximate_crop_window_center = optional_params_core_attrs["center"]
    crop_window_dims = optional_params_core_attrs["window_dims"]
    pad_mode = optional_params_core_attrs["pad_mode"]
    apply_symmetric_mask = optional_params_core_attrs["apply_symmetric_mask"]

    func_alias = _calc_crop_window_center_in_pixel_coords
    kwargs = {"input_signal": input_signal,
              "approximate_crop_window_center": approximate_crop_window_center}
    crop_window_center_in_pixel_coords = func_alias(**kwargs)

    kwargs = \
        {"crop_window_dims": \
         crop_window_dims,
         "crop_window_center_in_pixel_coords": \
         crop_window_center_in_pixel_coords,
         "pad_mode": \
         pad_mode,
         "input_signal": \
         input_signal,
         "apply_symmetric_mask": \
         apply_symmetric_mask}
    multi_dim_slice_for_cropping, multi_dim_slice_for_masking = \
        _calc_multi_dim_slices_for_cropping_and_masking(**kwargs)

    if pad_mode == "zeros":
        mask_to_apply_for_crop = np.ones(crop_window_dims[::-1], dtype=bool)
        mask_to_apply_for_crop[multi_dim_slice_for_masking] = False
    else:
        mask_to_apply_for_crop = None
    
    input_signal_datasubset_cropping_params = {"multi_dim_slice_for_cropping": \
                                               multi_dim_slice_for_cropping,
                                               "mask_to_apply_for_crop": \
                                               mask_to_apply_for_crop}

    return input_signal_datasubset_cropping_params



def _calc_multi_dim_slices_for_cropping_and_masking(
        crop_window_dims,
        crop_window_center_in_pixel_coords,
        pad_mode,
        input_signal,
        apply_symmetric_mask):
    num_spatial_dims = len(crop_window_dims)

    multi_dim_slice_for_cropping = tuple()
    multi_dim_slice_for_masking = tuple()
    
    for spatial_dim_idx in range(num_spatial_dims):
        start = (crop_window_center_in_pixel_coords[spatial_dim_idx]
                 - ((crop_window_dims[spatial_dim_idx]+1)//2 - 1))
        
        stop = start + crop_window_dims[spatial_dim_idx]
        
        if pad_mode == "no-padding":
            start = max(start, 0)
            stop = min(stop, input_signal.data.shape[-(spatial_dim_idx+1)])

        single_dim_slice_for_cropping = slice(start, stop)
        multi_dim_slice_for_cropping = ((single_dim_slice_for_cropping,)
                                        + multi_dim_slice_for_cropping)

        diff_1 = 0-single_dim_slice_for_cropping.start
        diff_2 = (single_dim_slice_for_cropping.stop
                  - input_signal.data.shape[-(spatial_dim_idx+1)])

        if apply_symmetric_mask:
            mask_frame_width_1 = max(diff_1, diff_2, 0)
            mask_frame_width_2 = mask_frame_width_1
        else:
            mask_frame_width_1 = max(diff_1, 0)
            mask_frame_width_2 = max(diff_2, 0)

        start = mask_frame_width_1
        stop = crop_window_dims[spatial_dim_idx] - mask_frame_width_2

        single_dim_slice_for_masking = slice(start, stop)
        multi_dim_slice_for_masking = ((single_dim_slice_for_masking,)
                                       + multi_dim_slice_for_masking)

    return multi_dim_slice_for_cropping, multi_dim_slice_for_masking



def _crop_input_signal_datasubset(input_signal_datasubset,
                                  input_signal_datasubset_cropping_params):
    multi_dim_slice_for_cropping = \
        input_signal_datasubset_cropping_params["multi_dim_slice_for_cropping"]
    mask_to_apply_for_crop = \
        input_signal_datasubset_cropping_params["mask_to_apply_for_crop"]

    num_spatial_dims = len(input_signal_datasubset.shape)

    cropped_input_signal_datasubset = input_signal_datasubset
    for spatial_dim_idx in range(num_spatial_dims):
        single_dim_slice_for_cropping = \
            multi_dim_slice_for_cropping[-(spatial_dim_idx+1)]
        
        indices = np.arange(single_dim_slice_for_cropping.start,
                            single_dim_slice_for_cropping.stop,
                            dtype="int")
        
        kwargs = {"a": cropped_input_signal_datasubset,
                  "indices": indices,
                  "axis": 1-spatial_dim_idx,
                  "mode": "wrap"}
        cropped_input_signal_datasubset = np.take(**kwargs)
    
    if mask_to_apply_for_crop is not None:
        cropped_input_signal_datasubset *= (~mask_to_apply_for_crop)

    return cropped_input_signal_datasubset



def _check_and_convert_block_dims(params):
    obj_name = "block_dims"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    block_dims = czekitout.convert.to_pair_of_positive_ints(**kwargs)
    
    return block_dims



def _pre_serialize_block_dims(block_dims):
    obj_to_pre_serialize = block_dims
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_block_dims(serializable_rep):
    block_dims = serializable_rep

    return block_dims



def _check_and_convert_padding_const(params):
    obj_name = "padding_const"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    padding_const = czekitout.convert.to_float(**kwargs)

    return padding_const



def _pre_serialize_padding_const(padding_const):
    obj_to_pre_serialize = padding_const
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_padding_const(serializable_rep):
    padding_const = serializable_rep

    return padding_const



def _check_and_convert_downsample_mode(params):
    obj_name = "downsample_mode"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    downsample_mode = czekitout.convert.to_str_from_str_like(**kwargs)

    kwargs["accepted_strings"] = ("sum", "mean", "median", "amin", "amax")
    czekitout.check.if_one_of_any_accepted_strings(**kwargs)

    return downsample_mode



def _pre_serialize_downsample_mode(downsample_mode):
    obj_to_pre_serialize = downsample_mode
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_downsample_mode(serializable_rep):
    downsample_mode = serializable_rep

    return downsample_mode



_default_block_dims = (2, 2)
_default_padding_const = 0
_default_downsample_mode = "sum"



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalDownsamplingParams(_cls_alias):
    r"""The set of optional parameters for the function 
    :func:`empix.downsample`.

    The Python function :func:`empix.downsample` copies a given input 2D
    ``hyperspy`` signal and downsamples the copy along the axes in signal space.
    The Python function effectively does the following: 

    1. Groups the pixels of the copy of the input signal into so-called
    downsampling blocks along the axes in signal space, with dimensions
    determined by the parameter ``block_dims``, padding the copy with a constant
    value of ``padding_const`` in the case that either the horizontal or
    vertical dimensions of the signal space of the original input signal are not
    divisible by the corresponding dimensions of the downsampling blocks.

    2. For each downsampling block, the Python function calls a ``numpy``
    function determined by the parameter ``downsample_mode``, wherein the input
    is the array data of the downsampling block, and the output is the value of
    the corresponding pixel of the downsampled signal.

    Parameters
    ----------
    block_dims : `array_like` (`int`, shape=(2,)), optional
        ``block_dims[0]`` and ``block_dims[1]`` specify the horizontal and
        vertical dimensions of the downsampling blocks in units of pixels.
    padding_const : `float`, optional
        ``padding_const`` is the padding constant to be applied in the case that
        either the horizontal or vertical dimensions of the signal space of the
        original input signal are not divisible by the corresponding dimensions
        of the downsampling blocks.
    downsample_mode : ``"sum"`` | ``"mean"`` | ``"median"`` | ``"amin"`` | ``"amax"``, optional
        ``downsample_mode == numpy_func.__name__`` where ``numpy_func`` is the 
        ``numpy`` function to be applied to the downsampling blocks.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Downsampled "+
        input_signal.metadata.General.title``, where ``input_signal`` is the
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("block_dims",
                        "padding_const",
                        "downsample_mode",
                        "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 block_dims=\
                 _default_block_dims,
                 padding_const=\
                 _default_padding_const,
                 downsample_mode=\
                 _default_downsample_mode,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def downsample(input_signal, optional_params=_default_optional_params):
    r"""Downsample a given input 2D ``hyperspy`` signal.

    This Python function copies a given input 2D ``hyperspy`` signal and
    downsamples the copy along the axes in signal space.  The Python function
    effectively does the following:

    1. Groups the pixels of the copy of the input signal into so-called
    downsampling blocks along the axes in signal space, with dimensions
    determined by the parameter ``block_dims``, padding the copy with a constant
    value of ``padding_const`` in the case that either the horizontal or
    vertical dimensions of the signal space of the original input signal are not
    divisible by the corresponding dimensions of the downsampling blocks.

    2. For each downsampling block, the Python function calls a ``numpy``
    function determined by the parameter ``downsample_mode``, wherein the input
    is the array data of the downsampling block, and the output is the value of
    the corresponding pixel of the downsampled signal.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalDownsamplingParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalDownsamplingParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalDownsamplingParams`, then the default values of
        the optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The output ``hyperspy`` signal that results from the downsampling. Note 
        that the metadata of the input signal is copied over to the output 
        signal, with the title being overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "downsample"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _downsample(**kwargs)

    return output_signal



def _downsample(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    title = optional_params_core_attrs["title"]

    navigation_dims = input_signal.data.shape[:-2]
    num_patterns = int(np.prod(navigation_dims))

    for pattern_idx in range(0, num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        input_signal_datasubset = input_signal.data[navigation_indices]
            
        kwargs = {"input_signal_datasubset": input_signal_datasubset,
                  "optional_params": optional_params}
        output_signal_datasubset = _downsample_input_signal_datasubset(**kwargs)

        if pattern_idx == 0:
            output_signal_data_shape = (navigation_dims
                                        + output_signal_datasubset.shape)
            output_signal_data = np.zeros(output_signal_data_shape,
                                          dtype=input_signal.data.dtype)

        output_signal_data[navigation_indices] = output_signal_datasubset
        
    kwargs = {"data": output_signal_data,
              "metadata": input_signal.metadata.as_dictionary()}
    if np.isrealobj(output_signal_data):
        output_signal = hyperspy.signals.Signal2D(**kwargs)
    else:
        output_signal = hyperspy.signals.ComplexSignal2D(**kwargs)
    output_signal.metadata.set_item("General.title", title)

    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params,
              "bin_coords": None,
              "output_signal": output_signal}
    _update_output_signal_axes(**kwargs)

    return output_signal



def _downsample_input_signal_datasubset(input_signal_datasubset,
                                        optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    block_dims = optional_params_core_attrs["block_dims"]
    padding_const = optional_params_core_attrs["padding_const"]
    downsample_mode = optional_params_core_attrs["downsample_mode"]
    
    kwargs = {"image": input_signal_datasubset,
              "block_size": block_dims[::-1],
              "cval": padding_const,
              "func": getattr(np, downsample_mode)}
    downsampled_input_signal_datasubset = skimage.measure.block_reduce(**kwargs)

    return downsampled_input_signal_datasubset



def _check_and_convert_new_signal_space_sizes(params):
    obj_name = "new_signal_space_sizes"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)
    
    current_func_name = "_check_and_convert_new_signal_space_sizes"

    if obj is not None:
        try:
            func_alias = czekitout.convert.to_pair_of_positive_ints
            kwargs = {"obj": obj, "obj_name": obj_name}
            new_signal_space_sizes = func_alias(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)
    else:
        if input_signal is not None:
            N_v, N_h = input_signal.data.shape[-2:]
            new_signal_space_sizes = (N_h, N_v)
        else:
            new_signal_space_sizes = obj

    return new_signal_space_sizes



def _pre_serialize_new_signal_space_sizes(new_signal_space_sizes):
    obj_to_pre_serialize = new_signal_space_sizes
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_new_signal_space_sizes(serializable_rep):
    new_signal_space_sizes = serializable_rep

    return new_signal_space_sizes



def _check_and_convert_new_signal_space_scales(params):
    obj_name = "new_signal_space_scales"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)
    
    current_func_name = "_check_and_convert_new_signal_space_scales"

    if obj is not None:
        try:
            func_alias = czekitout.convert.to_pair_of_floats
            kwargs = {"obj": obj, "obj_name": obj_name}
            new_signal_space_scales = func_alias(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)

        if np.prod(new_signal_space_scales) == 0:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise ValueError(err_msg)
    else:
        if input_signal is not None:
            new_signal_space_scales = (input_signal.axes_manager[-2].scale,
                                       input_signal.axes_manager[-1].scale)
        else:
            new_signal_space_scales = obj

    return new_signal_space_scales



def _pre_serialize_new_signal_space_scales(new_signal_space_scales):
    obj_to_pre_serialize = new_signal_space_scales
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_new_signal_space_scales(serializable_rep):
    new_signal_space_scales = serializable_rep

    return new_signal_space_scales



def _check_and_convert_new_signal_space_offsets(params):
    obj_name = "new_signal_space_offsets"
    obj = params[obj_name]

    param_name = "input_signal"
    input_signal = params.get(param_name, None)
    
    current_func_name = "_check_and_convert_new_signal_space_offsets"

    if obj is not None:
        try:
            func_alias = czekitout.convert.to_pair_of_floats
            kwargs = {"obj": obj, "obj_name": obj_name}
            new_signal_space_offsets = func_alias(**kwargs)
        except:
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)
    else:
        if input_signal is not None:
            new_signal_space_offsets = (input_signal.axes_manager[-2].offset,
                                        input_signal.axes_manager[-1].offset)
        else:
            new_signal_space_offsets = obj

    return new_signal_space_offsets



def _pre_serialize_new_signal_space_offsets(new_signal_space_offsets):
    obj_to_pre_serialize = new_signal_space_offsets
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_new_signal_space_offsets(serializable_rep):
    new_signal_space_offsets = serializable_rep

    return new_signal_space_offsets



def _check_and_convert_spline_degrees(params):
    obj_name = "spline_degrees"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    spline_degrees = czekitout.convert.to_pair_of_positive_ints(**kwargs)

    current_func_name = "_check_and_convert_spline_degrees"

    if (spline_degrees[0] > 5) or (spline_degrees[1] > 5):
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise ValueError(err_msg)

    return spline_degrees



def _pre_serialize_spline_degrees(spline_degrees):
    obj_to_pre_serialize = spline_degrees
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_spline_degrees(serializable_rep):
    spline_degrees = serializable_rep

    return spline_degrees



def _check_and_convert_interpolate_polar_cmpnts(params):
    obj_name = "interpolate_polar_cmpnts"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    interpolate_polar_cmpnts = czekitout.convert.to_bool(**kwargs)

    return interpolate_polar_cmpnts



def _pre_serialize_interpolate_polar_cmpnts(interpolate_polar_cmpnts):
    obj_to_pre_serialize = interpolate_polar_cmpnts
    serializable_rep = obj_to_pre_serialize
    
    return serializable_rep



def _de_pre_serialize_interpolate_polar_cmpnts(serializable_rep):
    interpolate_polar_cmpnts = serializable_rep

    return interpolate_polar_cmpnts



_default_new_signal_space_sizes = None
_default_new_signal_space_scales = None
_default_new_signal_space_offsets = None
_default_spline_degrees = (3, 3)
_default_interpolate_polar_cmpnts = True



_cls_alias = fancytypes.PreSerializableAndUpdatable
class OptionalResamplingParams(fancytypes.PreSerializableAndUpdatable):
    r"""The set of optional parameters for the function :func:`empix.resample`.

    The Python function :func:`empix.resample` copies a given input 2D
    ``hyperspy`` signal and resamples the copy along the axes in signal space by
    interpolating the original input signal using bivariate spines. Effectively,
    :func:`empix.resample` resamples the input signal.

    Parameters
    ----------
    new_signal_space_sizes : array_like` (`int`, shape=(2,)) | `None`, optional
        If ``new_signal_space_sizes`` is set to ``None``, then
        ``output_signal.data.shape`` will be equal to
        ``input_signal.data.shape``, where ``input_signal`` is the input signal,
        and ``output_signal`` is the output signal to result from the
        resampling. Otherwise, if ``new_signal_space_sizes`` is set to a pair of
        positive integers, then ``output_signal.data.shape[-1]`` and
        ``output_signal.data.shape[-2]`` will be equal to
        ``new_signal_space_sizes[0]`` and ``new_signal_space_sizes[1]``
        respectively.
    new_signal_space_scales : `array_like` (`float`, shape=(2,)) | `None`, optional
        Continuing from above, if ``new_signal_space_scales`` is set to
        ``None``, then ``output_signal.axes_manager[-1].scale`` and
        ``output_signal.axes_manager[-2].scale`` will be equal to
        ``input_signal.axes_manager[-1].scale`` and
        ``input_signal.axes_manager[-2].scale`` respectively. If
        ``new_signal_space_scales`` is set to a pair of non-zero floating-point
        numbers, then ``output_signal.axes_manager[-1].scale`` and
        ``output_signal.axes_manager[-2].scale`` will be equal to
        ``new_signal_space_scales[0]`` and ``new_signal_space_scales[1]``
        respectively. Otherwise, an error is raised.
    new_signal_space_offsets : `array_like` (`float`, shape=(2,)) | `None`, optional
        Continuing from above, if ``new_signal_space_offsets`` is set to
        ``None``, then ``output_signal.axes_manager[-1].offset`` and
        ``output_signal.axes_manager[-2].offset`` will be equal to
        ``input_signal.axes_manager[-1].offset`` and
        ``input_signal.axes_manager[-2].offset`` respectively. Otherwise, if
        ``new_signal_space_offsets`` is set to a pair of floating-point numbers,
        then ``output_signal.axes_manager[-1].offset`` and
        ``output_signal.axes_manager[-2].offset`` will be equal to
        ``new_signal_space_offsets[0]`` and ``new_signal_space_offsets[1]``
        respectively.
    spline_degrees : `array_like` (`int`, shape=(2,)), optional
        ``spline_degrees[0]`` and ``spline_degrees[1]`` are the horizontal and
        vertical degrees of the bivariate splines used to interpolate the input
        signal. Note that ``spline_degrees`` is expected to satisfy both
        ``1<=spline_degrees[0]<=5`` and ``1<=spline_degrees[1]<=5``.
    interpolate_polar_cmpnts : `bool`, optional
        If ``interpolate_polar_cmpnts`` is set to ``True``, then the polar
        components of the input signal are separately interpolated. Otherwise,
        if ``interpolate_polar_cmpnts`` is set to ``False``, then the real and
        imaginary components of the input signal are separately interpolated.
        Note that if the input signal is real-valued, then this parameter is
        effectively ignored.
    title : `str` | `None`, optional
        If ``title`` is set to ``None``, then the title of the output signal
        ``output_signal`` is set to ``"Resampled "+
        input_signal.metadata.General.title``, where ``input_signal`` is the
        input ``hyperspy`` signal.  Otherwise, if ``title`` is a `str`, then the
        ``output_signal.metadata.General.title`` is set to the value of
        ``title``.
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameter
        ``skip_validation_and_conversion``, where each `dict` key ``key`` is a
        different constructor parameter name, excluding the name
        ``"skip_validation_and_conversion"``, and
        ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of the
        constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.

    """
    ctor_param_names = ("new_signal_space_sizes",
                        "new_signal_space_scales",
                        "new_signal_space_offsets",
                        "spline_degrees",
                        "interpolate_polar_cmpnts",
                        "title")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs

    

    def __init__(self,
                 new_signal_space_sizes=\
                 _default_new_signal_space_sizes,
                 new_signal_space_scales=\
                 _default_new_signal_space_scales,
                 new_signal_space_offsets=\
                 _default_new_signal_space_offsets,
                 spline_degrees=\
                 _default_spline_degrees,
                 interpolate_polar_cmpnts=\
                 _default_interpolate_polar_cmpnts,
                 title=\
                 _default_title,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



def resample(input_signal, optional_params=_default_optional_params):
    r"""Resample a given input 2D ``hyperspy`` signal via interpolation.

    This Python function copies a given input 2D ``hyperspy`` signal and
    resamples the copy along the axes in signal space by interpolating the
    original input signal using bivariate spines. Effectively,
    :func:`empix.resample` resamples the input signal.

    Parameters
    ----------
    input_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The input ``hyperspy`` signal.
    optional_params : :class:`empix.OptionalResamplingParams` | `None`, optional
        The set of optional parameters. See the documentation for the class
        :class:`empix.OptionalResamplingParams` for details. If
        ``optional_params`` is set to ``None``, rather than an instance of
        :class:`empix.OptionalResamplingParams`, then the default values of the
        optional parameters are chosen.

    Returns
    -------
    output_signal : :class:`hyperspy._signals.signal2d.Signal2D` | :class:`hyperspy._signals.complex_signal2d.ComplexSignal2D`
        The output ``hyperspy`` signal that results from the resampling. Note 
        that the metadata of the input signal is copied over to the output 
        signal, with the title being overwritten.

    """
    params = locals()
    params["action_to_apply_to_input_signal"] = "resample"
    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    del kwargs["action_to_apply_to_input_signal"]
    output_signal = _resample(**kwargs)

    return output_signal



def _resample(input_signal, optional_params):
    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    title = optional_params_core_attrs["title"]

    func_alias = _calc_input_signal_datasubset_resampling_params
    input_signal_datasubset_resampling_params = func_alias(input_signal,
                                                           optional_params)

    navigation_dims = input_signal.data.shape[:-2]
    num_patterns = int(np.prod(navigation_dims))

    for pattern_idx in range(0, num_patterns):
        navigation_indices = np.unravel_index(pattern_idx, navigation_dims)
        input_signal_datasubset = input_signal.data[navigation_indices]
            
        kwargs = {"input_signal_datasubset": \
                  input_signal_datasubset,
                  "input_signal_datasubset_resampling_params": \
                  input_signal_datasubset_resampling_params}
        output_signal_datasubset = _resample_input_signal_datasubset(**kwargs)

        if pattern_idx == 0:
            output_signal_data_shape = (navigation_dims
                                        + output_signal_datasubset.shape)
            output_signal_data = np.zeros(output_signal_data_shape,
                                          dtype=input_signal.data.dtype)

        output_signal_data[navigation_indices] = output_signal_datasubset
        
    kwargs = {"data": output_signal_data,
              "metadata": input_signal.metadata.as_dictionary()}
    if np.isrealobj(output_signal_data):
        output_signal = hyperspy.signals.Signal2D(**kwargs)
    else:
        output_signal = hyperspy.signals.ComplexSignal2D(**kwargs)
    output_signal.metadata.set_item("General.title", title)

    kwargs = {"input_signal": input_signal,
              "optional_params": optional_params,
              "bin_coords": None,
              "output_signal": output_signal}
    _update_output_signal_axes(**kwargs)

    return output_signal



def _calc_input_signal_datasubset_resampling_params(input_signal,
                                                    optional_params):
    old_sizes = [input_signal.axes_manager[idx].size for idx in (-2, -1)]
    old_scales = [input_signal.axes_manager[idx].scale for idx in (-2, -1)]
    old_offsets = [input_signal.axes_manager[idx].offset for idx in (-2, -1)]

    optional_params_core_attrs = optional_params.get_core_attrs(deep_copy=False)
    new_sizes = optional_params_core_attrs["new_signal_space_sizes"]
    new_scales = optional_params_core_attrs["new_signal_space_scales"]
    new_offsets = optional_params_core_attrs["new_signal_space_offsets"]

    h_old = np.sign(old_scales[0]) * (old_offsets[0]
                                      + old_scales[0]*np.arange(old_sizes[0]))
    v_old = np.sign(old_scales[1]) * (old_offsets[1]
                                      + old_scales[1]*np.arange(old_sizes[1]))
    
    h_new = np.sign(old_scales[0]) * (new_offsets[0]
                                      + new_scales[0]*np.arange(new_sizes[0]))
    v_new = np.sign(old_scales[1]) * (new_offsets[1]
                                      + new_scales[1]*np.arange(new_sizes[1]))
    
    s_h_new = int(np.sign(h_new[1]-h_new[0]))
    s_v_new = int(np.sign(v_new[1]-v_new[0]))
    
    h_new = np.sort(h_new)
    v_new = np.sort(v_new)

    spline_degrees = \
        optional_params_core_attrs["spline_degrees"]
    interpolate_polar_cmpnts = \
        optional_params_core_attrs["interpolate_polar_cmpnts"]

    input_signal_datasubset_resampling_params = \
        {"h_old": h_old,
         "v_old": v_old,
         "h_new": h_new,
         "v_new": v_new,
         "s_h_new": int(np.sign(h_new[1]-h_new[0])),
         "s_v_new": int(np.sign(v_new[1]-v_new[0])),
         "spline_degrees": spline_degrees,
         "interpolate_polar_cmpnts": interpolate_polar_cmpnts}

    return input_signal_datasubset_resampling_params



def _resample_input_signal_datasubset(
        input_signal_datasubset,
        input_signal_datasubset_resampling_params):
    kwargs = \
        {"x": input_signal_datasubset_resampling_params["v_old"],
         "y": input_signal_datasubset_resampling_params["h_old"],
         "z": None,
         "bbox": [None, None, None, None],
         "kx": input_signal_datasubset_resampling_params["spline_degrees"][1],
         "ky": input_signal_datasubset_resampling_params["spline_degrees"][0],
         "s": 0}

    v_new = \
        input_signal_datasubset_resampling_params["v_new"]
    h_new = \
        input_signal_datasubset_resampling_params["h_new"]
    polar_cmpnts_are_to_be_interpolated = \
        input_signal_datasubset_resampling_params["interpolate_polar_cmpnts"]

    if np.isrealobj(input_signal_datasubset):
        kwargs["z"] = input_signal_datasubset
        method_alias = scipy.interpolate.RectBivariateSpline(**kwargs)
        resampled_input_signal_datasubset = method_alias(v_new, h_new)
    else:
        cmpnts = tuple()
        np_funcs = ((np.abs, np.angle)
                    if polar_cmpnts_are_to_be_interpolated
                    else (np.real, np.imag))

        for np_func in np_funcs:
            kwargs["z"] = np_func(input_signal_datasubset)
            method_alias = scipy.interpolate.RectBivariateSpline(**kwargs)
            cmpnts += (method_alias(v_new, h_new),)

        resampled_input_signal_datasubset = (cmpnts[0] * np.exp(1j*cmpnts[1])
                                             if (np_funcs[0] == np.abs)
                                             else cmpnts[0] + 1j*cmpnts[1])

    s_h_new = input_signal_datasubset_resampling_params["s_h_new"]
    s_v_new = input_signal_datasubset_resampling_params["s_v_new"]
    
    resampled_input_signal_datasubset[:, :] = \
        resampled_input_signal_datasubset[::s_v_new, ::s_h_new]

    return resampled_input_signal_datasubset



###########################
## Define error messages ##
###########################

_check_and_convert_center_err_msg_1 = \
    ("The object ``center`` must be `NoneType` or a pair of real numbers.")
_check_and_convert_center_err_msg_2 = \
    ("The object ``center`` must specify a point within the boundaries of the "
     "input ``hyperspy`` signal.")

_check_and_convert_radial_range_err_msg_1 = \
    ("The object ``radial_range`` must be `NoneType` or a pair of non-negative "
     "real numbers satisfying ``radial_range[0]<radial_range[1]``.")

_check_and_convert_num_bins_err_msg_1 = \
    ("The object ``num_bins`` must be `NoneType` or a positive `int`.")

_check_and_convert_limits_err_msg_1 = \
    ("The object ``limits`` must be `NoneType` or a pair of distinct real "
     "numbers.")

_check_and_convert_window_dims_err_msg_1 = \
    ("The object ``window_dims`` must be `NoneType` or a pair of positive "
     "integers.")

_crop_err_msg_1 = \
    ("The object ``optional_params`` specifies a crop that yields an output "
     "``hyperspy`` signal with zero elements.")

_check_and_convert_downsample_mode_err_msg_1 = \
    ("The object ``downsample_mode`` must be either ``'sum'``, ``'mean'``, "
     "``'median'``, ``'amin'``, or ``'amax'``.")

_downsample_err_msg_1 = \
    ("The object ``optional_params`` must be `NoneType` or an instance of the "
     "class `OptionalDownsamplingParams`.")

_check_and_convert_new_signal_space_sizes_err_msg_1 = \
    ("The object ``new_signal_space_sizes`` must be `NoneType` or a pair of "
     "positive integers.")

_check_and_convert_new_signal_space_scales_err_msg_1 = \
    ("The object ``new_signal_space_scales`` must be `NoneType` or a pair of "
     "non-zero real numbers.")

_check_and_convert_new_signal_space_offsets_err_msg_1 = \
    ("The object ``new_signal_space_offsets`` must be `NoneType` or a pair of "
     "real numbers.")

_check_and_convert_spline_degrees_err_msg_1 = \
    ("The object ``spline_degrees`` must be a pair of positive integers where "
     "each integer is less than or equal to ``5``.")
