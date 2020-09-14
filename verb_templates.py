import data
import random

verb_list = ["Move", "Give", "Take", "Touch", "Drop", "Lift", "Put", "Bring"]


# How can constructions be created?
# All possible instances initialised to not privilege one construction over another? X << verb >> Y and Y << verb >> X
# then they can be chosen at random initially and each given a score
# How can all possible combinations be initialised initially?
class Verb:

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
        self.unprocessed = []

        self.verb_subject_parsed = None
        self.verb_object1_parsed = None
        self.verb_object2_parsed = None

        self.item1_parsed = None
        self.item2_parsed = None

        self.location1_parsed = None
        self.location2_parsed = None

        # These variables are dictionaries used to store all markers with their normalised score for each marker for the given role
        # format is {'ko' = 0.3, 'ne' = 0.6}
        self.case_verb_subject = {}
        self.case_verb_object1 = {}
        self.case_verb_object2 = {}

        self.case_item1 = {}
        self.case_item2 = {}
        self.case_location1 = {}
        self.case_location2 = {}
        self.case_markers_used = {}
        self.unprocessed_parsed = []

        # These might not be required but keeping for now
        self.processed_names = []
        self.processed_objects = []
        self.processed_locations = []
        # self.unprocessed_labeled = {}

    # Common methods used in both contexts

    # 1. Parse a sentence to solve predicate variable inequality at random to simulate a 'guess'
    def parse_sentence_guess(self, *args):
        list_of_names = []
        list_of_items = []
        list_of_locations = []

        for things in args:
            for word in things:
                if word in data.namesAndObjects.list_of_names:
                    list_of_names.append(word)

                elif word in data.namesAndObjects.list_of_items:
                    list_of_items.append(word)

                elif word in data.namesAndObjects.list_of_locations:
                    list_of_locations.append(word)

                # elif word == self.action_verb:
                #     continue
                else:
                    self.unprocessed_parsed.append(word)

            # update values of self.subject, self.object1 etc to parsed values
            while list_of_names:
                if not self.verb_subject_parsed:
                    self.verb_subject_parsed = random.choice(list_of_names)
                    list_of_names.remove(self.verb_subject_parsed)

                elif not self.verb_object1_parsed:
                    self.verb_object1_parsed = random.choice(list_of_names)
                    list_of_names.remove(self.verb_object1_parsed)

                elif not self.verb_object2_parsed:
                    self.verb_object2_parsed = random.choice(list_of_names)
                    list_of_names.remove(self.verb_object2_parsed)

            while list_of_items:
                if not self.item1_parsed:
                    self.item1_parsed = random.choice(list_of_items)
                    list_of_items.remove(self.item1_parsed)

                else:
                    self.item2_parsed = random.choice(list_of_items)
                    list_of_items.remove(self.item2_parsed)

            while list_of_locations:
                if not self.location1_parsed:
                    self.location1_parsed = random.choice(list_of_locations)
                    list_of_locations.remove(self.location1_parsed)
                else:
                    self.location2_parsed = random.choice(list_of_locations)
                    list_of_locations.remove(self.location2_parsed)

    # 2. Check if parsed values from sentence match with values known from the global event truth
    def check_agreement(self):
        if self.verb_subject != self.verb_subject_parsed or self.verb_object1 != self.verb_object1_parsed or self.verb_object2 != self.verb_object2_parsed or self.location1 != self.location1_parsed or self.location2 != self.location2_parsed or self.item1 != self.item1_parsed or self.item2 != self.item2_parsed:
            return 0
        else:
            return 1

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
        self.unprocessed = []
        self.verb_subject_parsed = None
        self.verb_object1_parsed = None
        self.verb_object2_parsed = None
        self.item1_parsed = None
        self.item2_parsed = None
        self.location1_parsed = None
        self.location2_parsed = None
        self.case_markers_used = {}
        self.unprocessed_parsed = []

    # Speaker role methods:
    # 1. Create a new marker for a role when ambiguity detected and no markers exist in the dictionary
    # Returns a two alphabet string value
    def create_new_case_marker(self):
        alphabets = 'abcdefghijklmnopqrstuvwxyz'
        random_case_marker = "".join(random.sample(alphabets, 2))
        return random_case_marker

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
    def create_sentence(self):
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
        # if self.action_verb:
        #     self.sentence.append(self.action_verb)
        self.sentence = random.sample(self.sentence, len(self.sentence))

    # 4. If check agreement is false, locate the roles which have potential for ambiguity and returns them in a list
    def find_ambiguous_roles(self):
        ambiguous_roles = []
        if self.verb_subject != self.verb_subject_parsed:
            ambiguous_roles.append("verb_subject")
        if self.verb_object1 != self.verb_object1_parsed:
            ambiguous_roles.append("verb_object1")
        if self.verb_object2 != self.verb_object2_parsed:
            ambiguous_roles.append("verb_object2")

        if self.location1 != self.location1_parsed:
            ambiguous_roles.append("location1")
        if self.location2 != self.location2_parsed:
            ambiguous_roles.append("location2")

        if self.item1 != self.item1_parsed:
            ambiguous_roles.append("item1")
        if self.item2 != self.item2_parsed:
            ambiguous_roles.append("item2")
        return ambiguous_roles

    # 5. If a case marker is needed to be added, sentence is amended by passing the marker to be used and the
    # sentence component to be marked (verb_subject/item1 etc)
    def apply_case_marker_correction(self, marker, component_to_mark):
        for index in range(len(self.sentence)):
            if self.sentence[index] == eval("self." + component_to_mark):
                self.sentence.insert(index + 1, marker)

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
        if self.unprocessed:
            print("Unprocessed string", self.unprocessed)

    # return_object returns saved values in the obj class
    # action_verb, subject, item1, object1, location1, unprocessed string
    # needs to be deleted or generalised
    def return_object(self):
        return self.action_verb, self.verb_subject, self.item1, self.verb_object1, self.location1, self.unprocessed

    # To-do methods

    # 1. A method to call to apply the right construction to improve communication success
    # 2. Choose between word order serialisation and using case markers probabilistically
    # 3. Apply correction based on feedback to update score for a specific construction
    # ...this value update should contain a score based on time decay for choosing between
    # word order serialisation & case markers
    # def incorporate_assertion(self, asserted_value):


    # Following two methods are redundant and possibly not required
    def label_unprocessed(self):
        for stuff in self.unprocessed:
            if stuff in data.namesAndObjects.list_of_names:
                self.unprocessed_labeled[stuff] = "name"
            elif stuff in data.namesAndObjects.list_of_locations:
                self.unprocessed_labeled[stuff] = "location"
            elif stuff in data.namesAndObjects.list_of_items:
                self.unprocessed_labeled[stuff] = "object"
            else:
                self.unprocessed_labeled[stuff] = "unknown"

    def interpret_sentence(self):
        for things in self.sentence:
            if things in data.namesAndObjects.list_of_names:
                self.processed_names.append(things)
            elif things in data.namesAndObjects.list_of_items:
                self.processed_objects.append(things)
            elif things in data.namesAndObjects.list_of_locations:
                self.processed_locations.append(things)

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
