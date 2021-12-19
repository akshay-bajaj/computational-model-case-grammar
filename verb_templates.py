import data
import random
import data_and_stats_methods
import json

with open("model_parameters.json") as parameters:
    model_parameter_dict = json.load(parameters)
verb_list = model_parameter_dict["verb-list"]
del model_parameter_dict


# How can constructions be created?
# All possible instances initialised to not privilege one construction over another? X << verb >> Y and Y << verb >> X
# then they can be chosen at random initially and each given a score
# How can all possible combinations be initialised initially?


class Verb:
    """
    A class to represent agents' internal representation for verb templates
    ...
    :ivar action_verb: a string to store the operational action verb in the current sentence
    :vartype action_verb: str

    :
    Attributes
    ___________
    action_verb : str
        a string to store the operational action verb in the current sentence

    Methods
    ___________
    parse_sentence_guess(*args)
        parses a variable length sentence contained in *args and maps words to meaning space based on
        guess when ambiguity exists

    """

    def __init__(self, *args):
        # common variables
        self.action_verb = None
        self.sentence = []

        # Variables for speaker-role to utilised and use internal representation to linguistic representation
        self.verb_subject = None
        self.verb_object1 = None
        self.verb_object2 = None

        self.item1 = None
        self.item2 = None

        self.location1 = None
        self.location2 = None

        # Variables for listener-role to utilise when parsing sentence and later compare to internal representation
        # self.unprocessed = []

        self.verb_subject_parsed = None
        self.verb_object1_parsed = None
        self.verb_object2_parsed = None

        self.item1_parsed = None
        self.item2_parsed = None

        self.location1_parsed = None
        self.location2_parsed = None

        # These variables are dictionaries used to store all markers with their normalised score for each marker for
        # the given role format is {'ko' = 0.3, 'ne' = 0.6}
        # self.case_verb_subject = {"no-marker": 1}
        # self.case_verb_object1 = {"no-marker": 1}
        # self.case_verb_subject = {"no-marker": 1}
        # self.case_verb_object2 = {"no-marker": 1}
        #
        # self.case_item1 = {"no-marker": 1}
        # self.case_item2 = {"no-marker": 1}
        # self.case_location1 = {"no-marker": 1}
        # self.case_location2 = {"no-marker": 1}

        self.case_marker_used_verb_subject = None
        self.case_marker_used_verb_object1 = None
        self.case_marker_used_verb_object2 = None

        self.case_marker_used_item1 = None
        self.case_marker_used_item2 = None
        self.case_marker_used_location1 = None
        self.case_marker_used_location2 = None

        self.case_marker_verb_subject_parsed = None
        self.case_marker_verb_object1_parsed = None
        self.case_marker_verb_object2_parsed = None

        self.case_marker_item1_parsed = None
        self.case_marker_item2_parsed = None
        self.case_marker_location1_parsed = None
        self.case_marker_location2_parsed = None

    # Called at the end of a single game, language_game_outcome = 0 for communication failure,
    # language_game_outcome = 1 for success
    # current role - 0 for speaker, 1 for listener. Will adjust probability for all involved markers based on outcome
    def incorporate_game_outcome(self, outcome, current_role, agent_object):
        with open("model_parameters.json") as parameters:
            model_parameter_dict = json.load(parameters)
        prob_adjust_value = model_parameter_dict["probAdjustValue"]
        del model_parameter_dict
        del parameters
        # Listener probability adjustment
        if current_role == 1:
            if self.case_marker_verb_subject_parsed:
                agent_object.case_verb_subject = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_subject,
                    self.case_marker_verb_subject_parsed,
                    outcome, prob_adjust_value,
                    current_role)
            if self.case_marker_verb_object1_parsed:
                agent_object.case_verb_object1 = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_object1,
                    self.case_marker_verb_object1_parsed,
                    outcome, prob_adjust_value,
                    current_role)
            if self.case_marker_verb_object2_parsed:
                agent_object.case_verb_object2 = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_object2,
                    self.case_marker_verb_object2_parsed,
                    outcome, prob_adjust_value,
                    current_role)

            if self.case_marker_item1_parsed:
                agent_object.case_item1 = data_and_stats_methods.incorporate_outcome(agent_object.case_item1,
                                                                                     self.case_marker_item1_parsed,
                                                                                     outcome, prob_adjust_value,
                                                                                     current_role)
            if self.case_marker_item2_parsed:
                agent_object.case_item2 = data_and_stats_methods.incorporate_outcome(agent_object.case_item2,
                                                                                     self.case_marker_item2_parsed,
                                                                                     outcome, prob_adjust_value,
                                                                                     current_role)

            if self.case_marker_location1_parsed:
                agent_object.case_location1 = data_and_stats_methods.incorporate_outcome(agent_object.case_location1,
                                                                                         self.case_marker_location1_parsed,
                                                                                         outcome, prob_adjust_value,
                                                                                         current_role)
            if self.case_marker_location2_parsed:
                agent_object.case_location2 = data_and_stats_methods.incorporate_outcome(agent_object.case_location2,
                                                                                         self.case_marker_location2_parsed,
                                                                                         outcome, prob_adjust_value,
                                                                                         current_role)
        # Speaker probability adjustment
        elif current_role == 0:
            if self.case_marker_used_verb_subject:
                agent_object.case_verb_subject = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_subject,
                    self.case_marker_used_verb_subject,
                    outcome, prob_adjust_value,
                    current_role)
            if self.case_marker_used_verb_object1:
                agent_object.case_verb_object1 = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_object1,
                    self.case_marker_used_verb_object1,
                    outcome, prob_adjust_value,
                    current_role)
            if self.case_marker_used_verb_object2:
                agent_object.case_verb_object2 = data_and_stats_methods.incorporate_outcome(
                    agent_object.case_verb_object2,
                    self.case_marker_used_verb_object2,
                    outcome, prob_adjust_value,
                    current_role)

            if self.case_marker_used_item1:
                agent_object.case_item1 = data_and_stats_methods.incorporate_outcome(agent_object.case_item1,
                                                                                     self.case_marker_used_item1,
                                                                                     outcome,
                                                                                     prob_adjust_value, current_role)
            if self.case_marker_used_item2:
                agent_object.case_item2 = data_and_stats_methods.incorporate_outcome(agent_object.case_item2,
                                                                                     self.case_marker_used_item2,
                                                                                     outcome,
                                                                                     prob_adjust_value, current_role)

            if self.case_marker_used_location1:
                agent_object.case_location1 = data_and_stats_methods.incorporate_outcome(agent_object.case_location1,
                                                                                         self.case_marker_used_location1,
                                                                                         outcome,
                                                                                         prob_adjust_value,
                                                                                         current_role)
            if self.case_marker_used_location2:
                agent_object.case_location2 = data_and_stats_methods.incorporate_outcome(agent_object.case_location2,
                                                                                         self.case_marker_used_location2,
                                                                                         outcome,
                                                                                         prob_adjust_value,
                                                                                         current_role)

    # Listener methods
    # Categorise sentence in lexical categories and see case markers used
    def categorise_sentence(self):
        list_of_names = []
        list_of_name_markers = []
        list_of_items = []
        list_of_item_markers = []
        list_of_locations = []
        list_of_location_markers = []
        sentence_index = 0

        while sentence_index < len(self.sentence):
            current_word = self.sentence[sentence_index]
            if (sentence_index + 1) != len(self.sentence):
                next_word = self.sentence[sentence_index + 1]
            else:
                next_word = 'no-marker'

            if current_word in data.namesAndObjects.list_of_names:
                list_of_names.append(current_word)
                if (next_word in data.namesAndObjects.list_of_names) or (
                        next_word in data.namesAndObjects.list_of_items) or (
                        next_word in data.namesAndObjects.list_of_locations) or (next_word == self.action_verb):
                    list_of_name_markers.append('no-marker')
                    sentence_index += 1
                else:
                    list_of_name_markers.append(next_word)
                    sentence_index += 2

            elif current_word in data.namesAndObjects.list_of_items:
                list_of_items.append(current_word)
                if (next_word in data.namesAndObjects.list_of_names) or (
                        next_word in data.namesAndObjects.list_of_items) or (
                        next_word in data.namesAndObjects.list_of_locations) or (next_word == self.action_verb):
                    list_of_item_markers.append('no-marker')
                    sentence_index += 1
                else:
                    list_of_item_markers.append(next_word)
                    sentence_index += 2

            elif current_word in data.namesAndObjects.list_of_locations:
                list_of_locations.append(current_word)
                if (next_word in data.namesAndObjects.list_of_names) or (
                        next_word in data.namesAndObjects.list_of_items) or (
                        next_word in data.namesAndObjects.list_of_locations) or (next_word == self.action_verb):
                    list_of_location_markers.append('no-marker')
                    sentence_index += 1
                else:
                    list_of_location_markers.append(next_word)
                    sentence_index += 2
            elif current_word == self.action_verb:
                sentence_index += 1

        return list_of_names, list_of_items, list_of_locations, list_of_name_markers, list_of_item_markers, \
               list_of_location_markers

    def parse_sentence(self, agent_object):
        list_of_names, list_of_items, list_of_locations, list_of_name_markers, list_of_item_markers, \
            list_of_location_markers = self.categorise_sentence()

        index = 0
        while index < len(list_of_names):
            if (list_of_name_markers[index] in agent_object.case_verb_subject) and not self.verb_subject_parsed:
                self.verb_subject_parsed = list_of_names[index]
                self.case_marker_verb_subject_parsed = list_of_name_markers[index]
                index += 1

            elif (list_of_name_markers[index] in agent_object.case_verb_object1) and not self.verb_object1_parsed:
                self.verb_object1_parsed = list_of_names[index]
                self.case_marker_verb_object1_parsed = list_of_name_markers[index]
                index += 1

            elif (list_of_name_markers[index] in agent_object.case_verb_object2) and not self.verb_object2_parsed:
                self.verb_object2_parsed = list_of_names[index]
                self.case_marker_verb_object2_parsed = list_of_name_markers[index]
                index += 1
            #     When a new case marker is encountered
            else:
                if not self.verb_subject_parsed:
                    self.verb_subject_parsed = list_of_names[index]
                    self.case_marker_verb_subject_parsed = list_of_name_markers[index]
                    index += 1
                elif not self.verb_object1_parsed:
                    self.verb_object1_parsed = list_of_names[index]
                    self.case_marker_verb_object1_parsed = list_of_name_markers[index]
                    index += 1
                elif not self.verb_object2_parsed:
                    self.verb_object2_parsed = list_of_names[index]
                    self.case_marker_verb_object2_parsed = list_of_name_markers[index]
                    index += 1

        index = 0
        while index < len(list_of_items):
            if (list_of_item_markers[index] in agent_object.case_item1) and not self.item1_parsed:
                self.item1_parsed = list_of_items[index]
                self.case_marker_item1_parsed = list_of_item_markers[index]
                index += 1

            elif (list_of_item_markers[index] in agent_object.case_item2) and not self.item2_parsed:
                self.item2_parsed = list_of_items[index]
                self.case_marker_item2_parsed = list_of_item_markers[index]
                index += 1
            else:
                if not self.item1_parsed:
                    self.item1_parsed = list_of_items[index]
                    self.case_marker_item1_parsed = list_of_item_markers[index]
                    index += 1
                elif not self.item2_parsed:
                    self.item2_parsed = list_of_items[index]
                    self.case_marker_item2_parsed = list_of_item_markers[index]
                    index += 1

        index = 0
        while index < len(list_of_locations):
            if (list_of_location_markers[index] in agent_object.case_location1) and not self.location1_parsed:
                self.location1_parsed = list_of_locations[index]
                self.case_marker_location1_parsed = list_of_location_markers[index]
                index += 1

            elif (list_of_location_markers[index] in agent_object.case_location2) and not self.location2_parsed:
                self.location2_parsed = list_of_locations[index]
                self.case_marker_location2_parsed = list_of_location_markers[index]
                index += 1
            else:
                if not self.location1_parsed:
                    self.location1_parsed = list_of_locations[index]
                    self.case_marker_location1_parsed = list_of_location_markers[index]
                    index += 1
                elif not self.location2_parsed:
                    self.location2_parsed = list_of_locations[index]
                    self.case_marker_location2_parsed = list_of_location_markers[index]
                    index += 1

    # Common methods used in both contexts

    # This stays as is CORRECT
    # 2. Check if parsed values from sentence match with values known from the global event truth
    def check_agreement(self):
        """
        Checks if the parsed values and meaning representation known from world event agree

        :param self: Contains internal meaning representation and values parsed from sentence

        :return: Boolean value for agree {0} or disagree {1}
        """
        if self.verb_subject != self.verb_subject_parsed or self.verb_object1 != self.verb_object1_parsed \
                or self.verb_object2 != self.verb_object2_parsed or self.location1 != self.location1_parsed \
                or self.location2 != self.location2_parsed or self.item1 != self.item1_parsed \
                or self.item2 != self.item2_parsed:
            return 0
        else:
            return 1

    # TODO change the variables here
    # 3. Reset all transient values at the end of iteration
    def reset_transient_values(self):
        self.sentence = []
        self.verb_subject = None
        self.verb_object1 = None
        self.verb_object2 = None
        self.item1 = None
        self.item2 = None
        self.location1 = None
        self.location2 = None

        self.verb_subject_parsed = None
        self.verb_object1_parsed = None
        self.verb_object2_parsed = None
        self.item1_parsed = None
        self.item2_parsed = None
        self.location1_parsed = None
        self.location2_parsed = None

        self.case_marker_used_verb_subject = None
        self.case_marker_used_verb_object1 = None
        self.case_marker_used_verb_object2 = None
        self.case_marker_used_item1 = None
        self.case_marker_used_item2 = None
        self.case_marker_used_location1 = None
        self.case_marker_used_location2 = None

        self.case_marker_verb_subject_parsed = None
        self.case_marker_verb_object1_parsed = None
        self.case_marker_verb_object2_parsed = None
        self.case_marker_item1_parsed = None
        self.case_marker_item2_parsed = None
        self.case_marker_location1_parsed = None
        self.case_marker_location2_parsed = None

    # Speaker role methods:
    # This stays as is CORRECT
    # 2. initially used to set parameters based on external world event
    def set_parameters_from_world_event(self, world_event_object):
        self.verb_subject = world_event_object.name1
        self.verb_object1 = world_event_object.name2
        self.verb_object2 = world_event_object.name3

        self.item1 = world_event_object.item1
        self.item2 = world_event_object.item2
        self.location1 = world_event_object.location1
        self.location2 = world_event_object.location2

    # 3. create_sentence() creates a randomised sentence structure to simulate lexical language
    def create_sentence(self, agent_object):
        if self.verb_subject:
            self.sentence.append(self.verb_subject)
        if self.verb_object1:
            self.sentence.append(self.verb_object1)
        if self.verb_object2:
            self.sentence.append(self.verb_object2)

        if self.location1:
            self.sentence.append(self.location1)
        if self.location2:
            self.sentence.append(self.location2)

        if self.item1:
            self.sentence.append(self.item1)
        if self.item2:
            self.sentence.append(self.item2)
        if self.action_verb:
            self.sentence.append(self.action_verb)
        self.sentence = random.sample(self.sentence, len(self.sentence))
        self.apply_case_marker_correction(agent_object)

    # 5. If a case marker is needed to be added, sentence is amended by passing the marker to be used and the
    # sentence component to be marked (verb_subject/item1 etc)
    def apply_case_marker_correction(self, agent_object):
        length_of_sentence = len(self.sentence)
        index = 0
        while index < length_of_sentence:
            if self.sentence[index] == self.action_verb:
                index += 1

            elif self.sentence[index] == self.verb_subject:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_verb_subject)
                # add marker to list of used markers
                self.case_marker_used_verb_subject = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.verb_object1:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_verb_object1)
                self.case_marker_used_verb_object1 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.verb_object2:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_verb_object2)
                self.case_marker_used_verb_object2 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.item1:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_item1)
                self.case_marker_used_item1 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.item2:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_item2)
                self.case_marker_used_item2 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.location1:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_location1)
                self.case_marker_used_location1 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

            elif self.sentence[index] == self.location2:
                selected_marker = data_and_stats_methods.select_marker(agent_object.case_location2)
                self.case_marker_used_location2 = selected_marker
                if selected_marker != 'no-marker':
                    self.sentence.insert(index + 1, selected_marker)
                    index += 2
                    length_of_sentence += 1
                    del selected_marker
                else:
                    index += 1

    # print_utterance displays the composed sentence on the screen. Only used for testing purposes
    def print_utterance(self):
        if self.verb_subject:
            if not self.item1 and not self.location1 and not self.verb_object1:
                print(self.verb_subject, self.action_verb)
            elif self.item1 and not self.location1 and not self.verb_object1:
                print(self.verb_subject, self.action_verb, self.item1)
            elif self.location1 and not self.item1 and not self.verb_object1:
                # print(self.action, self.agent1, 'to', self.location)
                print(self.action_verb, self.verb_subject, self.location1)
            elif self.location1 and self.item1 and not self.verb_object1:
                # print(self.agent1, self.action, self.object, 'to', self.location)
                print(self.verb_subject, self.action_verb, self.item1, self.location1)
            elif self.item1 and self.verb_object1 and not self.location1:
                print(self.verb_subject, self.action_verb, self.item1, self.verb_object1)
                # print(self.agent1, self.action, self.object, 'to', self.agent2)
            elif self.item1 and self.location1 and self.verb_object1:
                print(self.verb_subject, self.action_verb, self.item1, self.location1, self.verb_object1)
                # print(self.agent1, self.action, self.object, 'to', self.location, 'for', self.agent2)
        elif self.item1:
            if not self.verb_subject and not self.location1:
                print(self.action_verb, self.item1)
            elif self.location1 and not self.verb_subject:
                print(self.action_verb, self.item1, self.location1)
        # if self.unprocessed:
        #     print("Unprocessed string", self.unprocessed)

    # To-do methods

    # 1. A method to call to apply the right construction to improve communication success
    # 2. Choose between word order serialisation and using case markers probabilistically
    # 3. Apply correction based on feedback to update score for a specific construction
    # ...this value update should contain a score based on time decay for choosing between
    # word order serialisation & case markers
    # def incorporate_assertion(self, asserted_value):

    # Following two methods are redundant and possibly not required
    # def label_unprocessed(self):
    #     for stuff in self.unprocessed:
    #         if stuff in data.namesAndObjects.list_of_names:
    #             self.unprocessed_labeled[stuff] = "name"
    #         elif stuff in data.namesAndObjects.list_of_locations:
    #             self.unprocessed_labeled[stuff] = "location"
    #         elif stuff in data.namesAndObjects.list_of_items:
    #             self.unprocessed_labeled[stuff] = "object"
    #         else:
    #             self.unprocessed_labeled[stuff] = "unknown"

    # def interpret_sentence(self):
    #     for things in self.sentence:
    #         if things in data.namesAndObjects.list_of_names:
    #             self.processed_names.append(things)
    #         elif things in data.namesAndObjects.list_of_items:
    #             self.processed_objects.append(things)
    #         elif things in data.namesAndObjects.list_of_locations:
    #             self.processed_locations.append(things)

    # def compare_sentence(self):
    #     for word in self.sentence:
    #         if word in data.namesAndObjects.list_of_names and not self.verb_subject_parsed:
    #             self.verb_subject_parsed = word
    #         elif word in data.namesAndObjects.list_of_names and not self.verb_object1_parsed:
    #             self.verb_object1_parsed = word
    #         elif word in data.namesAndObjects.list_of_items and not self.item1_parsed:
    #             self.item1_parsed = word
    #         elif word in data.namesAndObjects.list_of_locations and not self.location1_parsed:
    #             self.location1_parsed = word
    #         else:
    #             self.unprocessed_parsed.append(word)


class Move(Verb):
    # Agent, Object, Location, Agent2
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Move"

    def print_utterance(self):
        super().print_utterance()


class Give(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Give"

    def print_utterance(self):
        super().print_utterance()


class Take(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Take"

    def print_utterance(self):
        super().print_utterance()


class Touch(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Touch"

    def print_utterance(self):
        super().print_utterance()


class Drop(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Drop"

    def print_utterance(self):
        super().print_utterance()


class Lift(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Lift"

    def print_utterance(self):
        super().print_utterance()


class Put(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Put"

    def print_utterance(self):
        super().print_utterance()


class Bring(Verb):
    def __init__(self, *args):
        super().__init__(*args)
        self.action_verb = "Bring"

    def print_utterance(self):
        super().print_utterance()
