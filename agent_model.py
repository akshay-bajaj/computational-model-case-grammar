import data
from mesa import Agent, Model
from mesa.time import BaseScheduler
import random
import verb_templates
import matplotlib.pyplot as plt

global active_agents
global speaker_listener_toggle
global sentence_communicated
global first_turn_speaker
agreement_matrix = []
global language_game_success


# TODO Track data over iterations and plot it
# TODO add verb name to sentence


class CreateWorldEvent:
    # Objects of this class can be initialised for every iteration of world
    # They are initialised by random generated number of names, number of objects and no of locations in the event
    # They set names in variables that represent shared internal representation between agents for a world event
    def __init__(self, no_of_names, no_of_items, no_of_location):
        dataobj = data.namesAndObjects

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
        # Initial cognitive abilities of the agents which are same for all agents in the beginning
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
        elif active_event == 'Give':
            return self.give_model_obj
        elif active_event == 'Take':
            return self.take_model_obj
        elif active_event == 'Touch':
            return self.touch_model_obj
        elif active_event == 'Drop':
            return self.drop_model_obj
        elif active_event == 'Lift':
            return self.lift_model_obj
        elif active_event == 'Put':
            return self.put_model_obj
        elif active_event == 'Bring':
            return self.bring_model_obj

    def incorporate_game_outcome_speaker(self):
        active_verb_object = self.get_active_verb_object()
        if language_game_success:
            # Locate what the markers were marking and increase score by 0.1 in the relevant section
            for marker in active_verb_object.case_markers_used.keys():
                relevant_case_dict = eval('active_verb_object.' + active_verb_object.case_markers_used[marker])
                relevant_case_dict[marker] += 0.1
                # Lateral inhibition decreases scores of all other markers for the same role by 0.1
                for case_markers in relevant_case_dict.keys():
                    if case_markers != marker:
                        relevant_case_dict[case_markers] -= 0.1
        # Else if language game failed, do nothing
        # Reset all transient values for speaker at end of iteration
        active_verb_object.reset_transient_values()

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

        # Check if it is the speaker context. This code block contains speaker tasks for the first iteration of speaker.
        if speaker_listener_toggle != 1:
            print("Speaker first context")
            speaker_listener_toggle = 1
            active_verb_object = self.get_active_verb_object()
            # Values of subject, object etc reflect world event
            active_verb_object.set_parameters_from_world_event(world_event_object)
            active_verb_object.create_sentence()
            # Self diagnostic by speaker is required to detect possible ambiguity
            # The speaker parses its own sentence as a first step
            active_verb_object.parse_sentence_guess(active_verb_object.sentence)
            # Check if current sentence could possibly contain ambiguity
            internal_self_diagnostic_speaker = active_verb_object.check_agreement()

            # If ambiguity is detected, find locations of ambiguity and perform correction
            if internal_self_diagnostic_speaker == 0:
                ambiguous_roles = active_verb_object.find_ambiguous_roles()

                # TODO Ask hk if existing markers for roles should be applied de-facto even if ambiguity isn't found
                #  so they converge better
                # Check individual roles for existing markers
                if "verb_subject" in ambiguous_roles:
                    # If there is no marker, create a new random marker and set score to 0.1
                    if not active_verb_object.case_verb_subject:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_subject[chosen_marker] = 0.1

                    # Instance when existing markers exist, choose one with the highest value
                    else:
                        chosen_marker = max(active_verb_object.case_verb_subject,
                                            key=active_verb_object.case_verb_subject.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_subject")
                    # Add to case_markers_used dictionary
                    active_verb_object.case_markers_used[chosen_marker] = 'case_verb_subject'

                if "verb_object1" in ambiguous_roles:
                    if not active_verb_object.case_verb_object1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_object1[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_verb_object1,
                                            key=active_verb_object.case_verb_object1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_object1")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_verb_object1'

                if "verb_object2" in ambiguous_roles:
                    if not active_verb_object.case_verb_object2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_verb_object2[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_verb_object2,
                                            key=active_verb_object.case_verb_object2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "verb_object2")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_verb_object2'

                # Similarly for 'items' in the world
                if "item1" in ambiguous_roles:
                    if not active_verb_object.case_item1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_item1[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_item1,
                                            key=active_verb_object.case_item1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "item1")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_item1'
                if "item2" in ambiguous_roles:
                    if not active_verb_object.case_item2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_item2[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_item2,
                                            key=active_verb_object.case_item2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "item2")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_item2'
                # For locations
                if "location1" in ambiguous_roles:
                    if not active_verb_object.case_location1:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_location1[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_location1,
                                            key=active_verb_object.case_location1.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "location1")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_location1'
                if "location2" in ambiguous_roles:
                    if not active_verb_object.case_location2:
                        chosen_marker = active_verb_object.create_new_case_marker()
                        active_verb_object.case_location2[chosen_marker] = 0.1
                    else:
                        chosen_marker = max(active_verb_object.case_location2,
                                            key=active_verb_object.case_location2.get)
                    active_verb_object.apply_case_marker_correction(chosen_marker, "location2")
                    active_verb_object.case_markers_used[chosen_marker] = 'case_location2'
            # communicate sentence as a global variable for access to listener
            sentence_communicated = active_verb_object.sentence

        # This code block contains listener context. It should also add any unprocessed markers
        # to the dictionary of markers.
        elif speaker_listener_toggle == 1 and first_turn_speaker:
            # Find the corresponding internal representation for the action-verb
            active_verb_object = self.get_active_verb_object()
            # Assign actual values based on world event
            active_verb_object.set_parameters_from_world_event(world_event_object)

            active_verb_object.parse_sentence_guess(sentence_communicated)

            parsing_success_agreement = active_verb_object.check_agreement()
            ambiguous_roles = active_verb_object.find_ambiguous_roles()

            # Language game was a success
            if parsing_success_agreement:
                # TODO ask HK if I should change the logic of sentence parsing if it detects markers and adjust
                #  scores again for the listener and add new markers to the list
                # augment confidence scores
                language_game_success = 1

            # language game was a failure
            else:
                # Check if number of markers found equal number of unsolved variable inequalities
                if len(ambiguous_roles) == len(active_verb_object.unprocessed_parsed):
                    # Attempt to repair
                    # Loop over markers that are unprocessed_parsed
                    # TODO implement manual index for parsing markers in active_verb_object.unprocessed_parsed:
                    for marker in active_verb_object.unprocessed_parsed:
                        # loop over roles that were found to be ambiguous
                        for ambiguous_role in ambiguous_roles:
                            # loop over sentence to find where the marker is
                            for i in range(len(sentence_communicated)):
                                # Iterate to current marker in the sentence
                                if sentence_communicated[i] == marker:
                                    # Check if 1. Preceding word in sentence is the same role as current ambiguous role
                                    if sentence_communicated[i - 1] == eval('active_verb_object.' + ambiguous_role):
                                        # eval('active_verb_object.case_' + ambiguous_role)['aa'] = 0.3
                                        # eval('active_verb_object.case_' + ambiguous_role)['bb'] = 0.4
                                        # Check if marker already exists in marker dict. for current role
                                        if marker in eval('active_verb_object.case_' + ambiguous_role).keys():
                                            relevant_marker_path = eval("active_verb_object.case_" + ambiguous_role)
                                            relevant_marker_path[marker] += 0.1
                                            # Lateral inhibition of other markers
                                            for case_markers in relevant_marker_path.keys():
                                                if case_markers != marker:
                                                    relevant_marker_path[case_markers] -= 0.1
                                            # Remove current amb. role from list because variable equality solved
                                            ambiguous_roles.remove(ambiguous_role)
                                            break

                                        # If marker does not already exist for the relevant role, add it to dictionary
                                        else:
                                            current_case_dictionary = "active_verb_object.case_" + ambiguous_role
                                            relevant_marker_path = eval(current_case_dictionary)
                                            relevant_marker_path[marker] = 0.1
                                            for case_markers in relevant_marker_path.keys():
                                                if case_markers != marker:
                                                    relevant_marker_path[case_markers] -= 0.1
                                            ambiguous_roles.remove(ambiguous_role)
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
            # Reset all transient values for listener
            active_verb_object.reset_transient_values()
            print("listener context complete")
            first_turn_speaker = False

        # This code block contains speaker context after it receives feedback and should modify scores
        elif not first_turn_speaker and speaker_listener_toggle == 1:
            self.incorporate_game_outcome_speaker()


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

    def step(self):
        self.schedule.step()
        print("\n")


no_of_agents = input("Input the number of agents \n")
no_of_iterations = input("Input the number of iterations to run the model (multiples of 10) \n")
Language_Model = ConversationModel(int(no_of_agents))

for times_to_iter in range(int(no_of_iterations)):
    language_game_success = 0
    sentence_communicated = []
    first_turn_speaker = True
    print("\n")
    speaker_listener_toggle = 0
    active_agents = random.sample(range(int(no_of_agents)), 2)
    print(active_agents)

    # Change this to new class CreateWorldEvent object
    random_no_of_names = random.randint(1, 3)
    random_no_of_items = random.randint(0, 2)
    random_no_of_locations = random.randint(0, 2)
    world_event_object = CreateWorldEvent(random_no_of_names, random_no_of_items, random_no_of_locations)
    # world_event_object = CreateWorldEvent(2, 1, 2)

    # list_of_names, list_of_items, list_of_locations = create_world_event(2, 1, 1)
    # Global shared context of the event w/ shared internal representation by both agents

    for agent in active_agents:
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[agent])
    Language_Model.step()
    # Remove active agents from schedule for next iteration
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[0]])
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[1]])
    # add speaker for second context
    Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_agents[0]])
    Language_Model.step()
    Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_agents[0]])

# avg = sum(agreement_matrix) / len(agreement_matrix)
# percent_agreement = avg * 100
# print("Percentage of times that agents agreed is", int(percent_agreement))
communicative_success = []
iteration_index = []
for index in range(len(agreement_matrix)//10):
    m = index * 10
    n = m + 9
    summation = sum(agreement_matrix[m:n])
    communicative_success.append(summation/(n - m))
    iteration_index.append(m)
    print(summation)

# print(communicative_success)
plt.plot(iteration_index, communicative_success)
plt.xlabel("Language games count")
plt.ylabel("Communicative success")
plt.show()
