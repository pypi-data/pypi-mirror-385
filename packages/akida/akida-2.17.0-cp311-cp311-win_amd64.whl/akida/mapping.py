import akida
from enum import Enum

from .core import LayerType


class MapMode(Enum):
    """ Mapping mode

    Define the strategy for the hardware mapping.
    """
    AllNps = 1
    """ Maximize HW ressources (number of NPs used) with minimum HW passes."""
    HwPr = 2
    """ Maximize HW ressources (number of NPs used) with maximum HW passes.
    This mode provides the potential for higher-performances"""
    Minimal = 3
    """ Minimize HW ressources"""


def _get_layer_mapped(model):
    return sum(1 for layer in model.layers if layer.mapping is not None)


def _get_model_pass(model):
    nb_pass = 0
    for seq in model.sequences:
        nb_pass += len(seq.passes)
    return nb_pass


def _get_model_seq(model):
    return len(model.sequences)


def _get_model_nps(model):
    hrc_layers = [LayerType.InputConvolutional, LayerType.InputConv2D]

    nb_nps = 0
    for seq in model.sequences:
        for current_pass in seq.passes:
            for layer in current_pass.layers:
                # The layer is mapped on NPs but not on HRC
                if layer.parameters.layer_type not in hrc_layers and layer.mapping is not None:
                    nb_nps += len(layer.mapping.nps)

    return nb_nps


def _map_criteria_from_model(model):
    # Obtain the mapping criteria
    return dict(layer_mapped=_get_layer_mapped(model),
                seq_number=_get_model_seq(model),
                pass_number=_get_model_pass(model),
                np_used=_get_model_nps(model))


def _is_better_map(map_criteria_ref, map_criteria_cur, consider_pass_nb=True):
    # Better if we can map now
    if map_criteria_ref is None:
        # ref model does not map
        return True
    elif map_criteria_cur is None:
        # ref model map but not cur model
        return False

    # Returns if a current model has a better mapping than a reference model
    nb_layer_mapped_ref = map_criteria_ref["layer_mapped"]
    nb_layer_mapped_cur = map_criteria_cur["layer_mapped"]

    # Better if more layers mapped
    if nb_layer_mapped_ref != nb_layer_mapped_cur:
        return nb_layer_mapped_ref < nb_layer_mapped_cur

    nb_seq_ref = map_criteria_ref["seq_number"]
    nb_seq_cur = map_criteria_cur["seq_number"]

    # Better with low seq number
    if nb_seq_cur != nb_seq_ref:
        return nb_seq_cur < nb_seq_ref

    if consider_pass_nb:
        np_pass_ref = map_criteria_ref["pass_number"]
        np_pass_cur = map_criteria_cur["pass_number"]
        if np_pass_cur != np_pass_ref:
            # Better if less passes
            return np_pass_cur < np_pass_ref

    nb_nps_ref = map_criteria_ref["np_used"]
    nb_nps_cur = map_criteria_cur["np_used"]
    # Better if we use more NPs
    return nb_nps_ref <= nb_nps_cur


def _map_search(model, device, hw_only, min_pass, constraints):
    # Needs constraints to move the max filter number
    if constraints is None:
        constraints = akida.MapConstraints(device)

    initial_split_neurons = constraints.cnp_max_filters
    best_map_criteria = None

    # check if it is possible to find a better mapping
    if any(layer.splittable for layer in model.layers):
        # Obtains the reference mapped model, using the minimal hardware ressources
        try:
            model._map(device, hw_only=hw_only, constraints=constraints)
            best_map_criteria = _map_criteria_from_model(model)
        except Exception:
            pass

        min_split_neurons = 0
        max_split_neurons = constraints.cnp_max_filters
        cur_split_neurons = max_split_neurons
        best_split_neurons = cur_split_neurons

        while min_split_neurons + 2 <= max_split_neurons:
            cur_split_neurons = int((min_split_neurons + max_split_neurons) / 2)
            assert cur_split_neurons > 0
            constraints.cnp_max_filters = cur_split_neurons
            try:
                model._map(device, hw_only=hw_only, constraints=constraints)
                cur_map_criteria = _map_criteria_from_model(model)
            except Exception:
                cur_map_criteria = None

            if _is_better_map(best_map_criteria, cur_map_criteria, min_pass):
                best_map_criteria = cur_map_criteria
                best_split_neurons = cur_split_neurons
                max_split_neurons = cur_split_neurons
            else:
                min_split_neurons = cur_split_neurons

    # Apply best mapping found if we success to map
    if best_map_criteria:
        constraints.cnp_max_filters = best_split_neurons
    else:
        constraints.cnp_max_filters = initial_split_neurons
    model._map(device, hw_only=hw_only, constraints=constraints)
