import random
import json
import gzip


# Methods for external usage from agent_model
# 1. Method probabilistically selects markers from dictionary and returns a str marker key
def select_marker(markers_dict_local):
    """
    This function returns a probabilistically selected marker each time a marker has to be selected by an agent
    :param markers_dict_local: case marker dictionary with probability distribution over the markers
    :return: string format, probabilistically selected marker from dictionary
    """
    markers_keys = list(markers_dict_local.keys())
    markers_values = list(markers_dict_local.values())
    selected_marker = random.choices(markers_keys, weights=markers_values)
    selected_marker = "".join(selected_marker)
    return selected_marker


# 2. At the end of an iteration, this function is called to save trial data to file
def log_output_for_trial_to_file(output_filename, data_to_write):
    json_str = json.dumps(data_to_write) + "\n"  # 2. string (i.e. JSON)
    json_bytes = json_str.encode('utf-8')
    with gzip.open(output_filename, "x") as json_file:
        json_file.write(json_bytes)


def log_output_for_trial_to_file_in_parts(output_filename, data_to_write, part):
    json_str = json.dumps(data_to_write) + "\n"  # 2. string (i.e. JSON)
    json_bytes = json_str.encode('utf-8')
    with gzip.open(output_filename, "x") as json_file:
        json_file.write(json_bytes)


# 3. Call after game trial to update probability for marker dictionary
def incorporate_outcome(markers_dict_local, marker_used, outcome_local, prob_adjust_value, current_role):
    markers_dict_local = truncate_dictionary(markers_dict_local, marker_used, prob_adjust_value / 2)

    if outcome_local == 1:
        if marker_used in markers_dict_local.keys():
            # If prob of marker used + probability adjust value is less than or equal to 1, add the value
            if (markers_dict_local[marker_used] + prob_adjust_value) <= 1:
                initial_value_marker_used = markers_dict_local[marker_used]
                markers_dict_local[marker_used] += prob_adjust_value
                # reduce probability of other markers proportional to their current probability
                for key in list(markers_dict_local.keys()):
                    if key != marker_used:
                        numerator = prob_adjust_value * markers_dict_local[key]
                        denominator = 1 - initial_value_marker_used
                        if markers_dict_local[key] - (numerator / denominator) >= 0:
                            markers_dict_local[key] -= numerator / denominator
            else:
                # when adding probability adjustment to used marker will be > 1
                for key in list(markers_dict_local.keys()):
                    # set used marker's probability to 1
                    if key == marker_used:
                        markers_dict_local[key] = 1
                    # delete every other marker from the dictionary
                    else:
                        del (markers_dict_local[key])
        else:
            add_new_marker(markers_dict_local, marker_used)

    elif outcome_local == 0:
        if len(markers_dict_local) == 1:
            if current_role == 0:
                new_marker = create_new_case_marker()
                add_new_marker(markers_dict_local, new_marker)
        else:
            if marker_used in markers_dict_local.keys():
                if (markers_dict_local[marker_used] - prob_adjust_value) >= 0:
                    initial_value_marker_used = markers_dict_local[marker_used]
                    markers_dict_local[marker_used] -= prob_adjust_value
                    # increase prob of all other markers proportionately
                    for key in list(markers_dict_local.keys()):
                        if key != marker_used:
                            numerator = prob_adjust_value * markers_dict_local[key]
                            denominator = 1 - initial_value_marker_used
                            if markers_dict_local[key] + (numerator / denominator) <= 1:
                                markers_dict_local[key] += numerator / denominator
                            else:
                                markers_dict_local[key] = 1
                                for k in list(markers_dict_local.keys()):
                                    if k != key:
                                        del (markers_dict_local[k])
                                break
    if sum(markers_dict_local.values()) != 1:
        sum_of_markers = sum(markers_dict_local.values())
        for key, value in markers_dict_local.items():
            markers_dict_local[key] = value / sum_of_markers
    return markers_dict_local


# 4. Add a new marker when encountered as listener or when speaker first creates it
def add_new_marker(markers_dict_local, new_marker_local):
    prob_new_marker = 1 / (len(markers_dict_local.keys()) + 1)
    # adjust probabilities for existing markers
    for key in list(markers_dict_local.keys()):
        markers_dict_local[key] = (1 - prob_new_marker) * markers_dict_local[key]
    # add the new value to the dict if sum of all is 1
    # if sum(markers_dict_local.values()) == 1:
    markers_dict_local[new_marker_local] = prob_new_marker
    return markers_dict_local


# Methods used internally
# 1. Called by incorporate_outcome() before incorporating scores
def truncate_dictionary(markers_dict_truncated, marker_used, threshold):
    """
    :param markers_dict_truncated: the original case marker dictionary with associated values
    :param marker_used:
    :param threshold: all markers with probability below the threshold are truncated
    :return: returns the case marker dictionary with probabilities below the threshold truncated
    """
    for key in list(markers_dict_truncated.keys()):
        if markers_dict_truncated[key] < threshold and marker_used != key:
            value_to_delete = markers_dict_truncated[key]
            del (markers_dict_truncated[key])
            original_sum_probabilities = sum(markers_dict_truncated.values())
            for k in list(markers_dict_truncated.keys()):
                numerator = markers_dict_truncated[k] * value_to_delete
                markers_dict_truncated[k] += numerator / original_sum_probabilities
    if sum(markers_dict_truncated.values()) != 1:
        sum_of_markers = sum(markers_dict_truncated.values())
        for key, value in markers_dict_truncated.items():
            markers_dict_truncated[key] = value / sum_of_markers
    return markers_dict_truncated


# 2. Create a new marker for a role
# Returns a two alphabet string value
def create_new_case_marker():
    alphabets = 'abcdefghijklmnopqrstuvwxyz'
    random_case_marker = "".join(random.sample(alphabets, 2))
    return random_case_marker
