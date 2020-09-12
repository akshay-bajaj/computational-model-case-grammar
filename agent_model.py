import data
from mesa import Agent, Model
from mesa.time import BaseScheduler
import random
import verb_templates

global active_agents
global speaker_listener_toggle
global sentence_communicated
global first_turn_speaker
agreement_matrix = []
global language_game_success


class CreateWorldEvent:
    # Objects of this class can be initialised for every iteration of world
    # They are initialised by random generated number of names, number of objects and no of locations in the event
    # They set names in variables that represent shared internal representation between agents for a world event
    def __init__(self, no_of_names, no_of_items, no_of_location):
        dataobj = data.namesAndObjects
        #
        # event_selected = random.sample(verb_templates.verb_list, 1)  # Select the action verb event at random
        # event_selected = event_selected[0]

        list_of_names = []
        list_of_items = []
        list_of_locations = []
        self.name1 = None
        self.name2 = None
        self.name3 = None
        self.item1 = None
        self.item2 = None
        self.location1 = None
        self.location2 = None
        self.event_selected = random.sample(verb_templates.verb_list, 1)[0]

        name = dataobj.random_name_generator(dataobj, no_of_names)
        for i in range(len(name)):
            list_of_names.append(name[i])
            if not self.name1:
                self.name1 = name[i]
            elif not self.name2:
                self.name2 = name[i]
            else:
                self.name3 = name[i]

            # locals()["name" + str(i + 1)] = name[i] # Event names saved as variables name1, name2 etc

        item = dataobj.random_object_generator(dataobj, no_of_items)
        for i in range(len(item)):
            list_of_items.append(item[i])
            if not self.item1:
                self.item1 = item[i]
            else:
                self.item2 = item[i]

        location = dataobj.random_surface_generator(dataobj, no_of_location)
        for i in range(len(location)):
            list_of_locations.append(location[i])
            if not self.location1:
                self.location1 = location[i]
            else:
                self.location2 = location[i]


class ConversationAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agree = False
        # Initial cognitive linguistic abilities of the agents which are same for all agents in the beginning
        self.move_model_obj = verb_templates.Move()
        self.give_model_obj = verb_templates.Give()
        self.take_model_obj = verb_templates.Take()
        self.touch_model_obj = verb_templates.Touch()
        self.drop_model_obj = verb_templates.Drop()
        self.lift_model_obj = verb_templates.Lift()
        self.put_model_obj = verb_templates.Put()
        self.bring_model_obj = verb_templates.Bring()

    # Looks at world event object to decide which action-verb schema to deploy
    def get_active_verb_object(self):
        active_event = world_event_object.event_selected
        if active_event == 'Move':
            return self.move_model_obj
        if active_event == 'Give':
            return self.give_model_obj
        if active_event == 'Take':
            return self.take_model_obj
        if active_event == 'Touch':
            return self.touch_model_obj
        if active_event == 'Drop':
            return self.drop_model_obj
        if active_event == 'Lift':
            return self.lift_model_obj
        if active_event == 'Put':
            return self.put_model_obj
        if active_event == 'Bring':
            return self.bring_model_obj

    def step(self):
        # For agent to understand its activation context
        global speaker_listener_toggle
        # Tracks agreement over iterations as binary values in a list
        global agreement_matrix
        # Contains event structure shared context between both agents as a common object
        global world_event_object
        # Variable contains status of current iteration being success(1)/failure(0)
        global language_game_success
        # Contains the string communicated from speaker to listener
        global sentence_communicated
        # Flag for first/second context for speaker
        global first_turn_speaker

        print(self.unique_id)

        # Check if it is the speaker context. This code block contains speaker tasks for the first iteration of speaker.
        if speaker_listener_toggle != 1:
            print("Speaker first context")
            speaker_listener_toggle = 1
            active_verb_object = self.get_active_verb_object()
            active_verb_object.set_parameters_from_world_event(world_event_object)  # Values of subject, object etc
            # reflect world event
            active_verb_object.create_sentence()
            # Self diagnostic by speaker is required to detect possible ambiguity
            # The speaker parses its own sentence as a first step
            active_verb_object.parse_sentence_guess(active_verb_object.sentence)
            # Check if current sentence could possibly contain ambiguity
            internal_self_diagnostic_speaker = active_verb_object.check_agreement()

            # If ambiguity is detected, find locations of ambiguity and perform correction
            if internal_self_diagnostic_speaker == 0:
                ambiguous_roles = active_verb_object.find_ambiguous_roles()

                # Check individual roles for existing markers
                if "verb_subject" in ambiguous_roles:
                    # If there is no marker, create a new random marker and set score to 0.5
                    if not active_verb_object.case_verb_subject:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_subject[chosen_marker] = 0.5

                    # Instance when existing markers exist, choose one with the highest value
                    else:
                        chosen_marker = max(active_verb_object.case_verb_subject,
                                            key=active_verb_object.case_verb_subject.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_subject")

                if "verb_object1" in ambiguous_roles:
                    if not active_verb_object.case_verb_object1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_object1[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_verb_object1,
                                            key=active_verb_object.case_verb_object1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_object1")

                if "verb_object2" in ambiguous_roles:
                    if not active_verb_object.case_verb_object2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_object2[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_verb_object2,
                                            key=active_verb_object.case_verb_object2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_object2")

                # Similarly for 'items' in the world
                if "item1" in ambiguous_roles:
                    if not active_verb_object.case_item1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_item1[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_item1,
                                            key=active_verb_object.case_item1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "item1")
                if "item2" in ambiguous_roles:
                    if not active_verb_object.case_item2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_item2[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_item2,
                                            key=active_verb_object.case_item2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "item2")
            #     For locations
                if "location1" in ambiguous_roles:
                    if not active_verb_object.case_location1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_location1[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_location1,
                                            key=active_verb_object.case_location1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "location1")
                if "location2" in ambiguous_roles:
                    if not active_verb_object.case_location2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_location2[chosen_marker] = 0.5
                    else:
                        chosen_marker = max(active_verb_object.case_location2,
                                            key=active_verb_object.case_location2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "location2")
            # communicate sentence as a global variable for access to listener
            sentence_communicated = active_verb_object.sentence

        # This code block contains listener context. It should also add any unprocessed markers
        # to the dictionary of markers.
        elif speaker_listener_toggle == 1 and first_turn_speaker:

            # Find the corresponding internal representation for the action-verb
            active_verb_object = self.get_active_verb_object()
            # Assign actual values based on world event
            active_verb_object.set_parameters_from_world_event(world_event_object)
            # TODO change the logic of sentence parsing if it detects markers
            active_verb_object.parse_sentence_guess(sentence_communicated)

            parsing_success_agreement = active_verb_object.check_agreement()
            ambiguous_roles = active_verb_object.find_ambiguous_roles()

            # Language game was a success
            if parsing_success_agreement:
                # TODO Check if unprocessed markers exist and add the case markers to respective roles or
                # augment confidence scores
                language_game_success = 1

            # language game was a failure
            # TODO verify this logic
            else:
                # Check if number of markers found equal number of unsolved variable inequalities
                if len(ambiguous_roles) == len(active_verb_object.unprocessed_parsed):
                    # Attempt to repair
                    # Loop over markers that are unprocessed_parsed
                    for marker in active_verb_object.unprocessed_parsed:
                        # loop over roles that were found to be ambiguous
                        for ambiguous_role in ambiguous_roles:
                            # loop over sentence to find where the marker is
                            for i in range(len(sentence_communicated)):
                                # Iterate to current marker in the sentence
                                if sentence_communicated[i] == marker:
                                    # Check if 1. marker exists in dictionary for current ambiguous role
                                    # 2. Preceding word in sentence is the same role as current ambiguous role
                                    if sentence_communicated[i-1] == eval('active_verb_object.' + ambiguous_role):
                                        # Check if marker already exists in marker dict. for current role
                                        if marker in eval('active_verb_object.case_' + ambiguous_role):
                                            # current_case_dictionary = "active_verb_object.case_" + ambiguous_role
                                            # relevant_marker_path = eval(current_case_dictionary)
                                            relevant_marker_path = eval("active_verb_object.case_" + ambiguous_role)
                                            relevant_marker_path[marker] += 0.1
                                            # Remove current amb. role from list because variable equality solved
                                            ambiguous_roles.remove(ambiguous_role)
                                            # remove the marker from unprocessed list because it is successfully parsed
                                            # active_verb_object.unprocessed_parsed.remove(marker)
                                            break

                                        # TODO implement lateral inhibition for other markers
                                        # If marker does not already exist for the relevant role
                                        else:
                                            current_case_dictionary = "active_verb_object.case_" + ambiguous_role
                                            relevant_marker_path = eval(current_case_dictionary)
                                            relevant_marker_path[marker] = 0.5
                                            ambiguous_roles.remove(ambiguous_role)
                                            # active_verb_object.unprocessed_parsed.remove(marker)
                                            break
                                    else:
                                        break
                                            # add the marker to dictionary
                    if len(ambiguous_roles) == 0:
                        language_game_success = 1
                else:
                    # Communicate failure since repair could not be made
                    language_game_success = 0

            agreement_matrix.append(language_game_success)

            print("listener context")

            first_turn_speaker = False

        # This code block contains speaker context after it receives feedback and should modify scores
        else:
            print("Speaker second context")
        # if agreement and check:
        #     print("agent", active_agents[0], "said \n", ' '.join(returned_object.sentence))
        #     print("Agent", active_agents[1], "understands what is said")
        # elif not agreement and check:
        #     print("agent", active_agents[0], "said \n", ' '.join(returned_object.sentence))
        #     print("Agent", active_agents[1], "does not understands what is said")


# Model of the world with 'N' agents
class ConversationModel(Model):
    # Model with 'N' initial agents
    # Schedule is RandomActivation - A scheduler which activates each agent once per step,
    # in random order, with the order reshuffled every step.

    def __init__(self, N):
        self.num_agents = N
        self.schedule = BaseScheduler(self)
        self.list_of_agent_objects = []

        for i in range(self.num_agents):
            a = ConversationAgent(i, self)
            self.list_of_agent_objects.append(a)
        # print(self.b)
            # self.schedule.add(a)

    def step(self):
        self.schedule.step()
        print("\n")


Language_Model = ConversationModel(10)
for times_to_iter in range(20):
    language_game_success = 0
    sentence_communicated = []
    first_turn_speaker = True
    print("\n")
    speaker_listener_toggle = 0
    active_agents = random.sample(range(10), 2)
    # active_agents.append(active_agents[0])
    print(active_agents)

    # Change this to new class CreateWorldEvent object
    # TODO randomise the values of number of names, items and locations
    world_event_object = CreateWorldEvent(3, 2, 1)
    # list_of_names, list_of_items, list_of_locations = create_world_event(2, 1, 1)
    #Global shared context of the event w/ shared internal representation by both agents

    for things in active_agents:
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[things])
    Language_Model.step()
    # Remove active agents from schedule for next iteration
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[0]])
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[1]])
    # add speaker for second context
    Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_agents[0]])
    Language_Model.step()
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[0]])
#     TODO clear all temporary values in active agents at the end of iteration



avg = sum(agreement_matrix) / len(agreement_matrix)
percent_agreement = avg * 100
print("Percentage of times that agents agreed is", percent_agreement)
