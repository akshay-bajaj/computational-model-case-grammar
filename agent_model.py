from mesa import Agent, Model
from mesa.time import BaseScheduler
import random

import data_and_stats_methods
import verb_templates
import matplotlib.pyplot as plt
import json
import data

global sentences
global conversation_index
global active_agents
global sentence_communicated
agreement_matrix = []
global language_game_success

global incorporate_outcome_for_speaker


# Objects of this class can be initialised for every iteration of world
# They are initialised by random generated number of names, number of objects and no of locations in the event
# They set names in variables that represent shared internal representation between agents for a world event
class CreateWorldEvent:
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
        for name_index in range(len(name)):
            list_of_names.append(name[name_index])
            if not self.name1:
                self.name1 = name[name_index]
            elif not self.name2:
                self.name2 = name[name_index]
            else:
                self.name3 = name[name_index]

            # locals()["name" + str(i + 1)] = name[i] # Event names saved as variables name1, name2 etc

        item = dataobj.random_object_generator(dataobj, no_of_items)
        for item_index in range(len(item)):
            list_of_items.append(item[item_index])
            if not self.item1:
                self.item1 = item[item_index]
            else:
                self.item2 = item[item_index]

        location = dataobj.random_surface_generator(dataobj, no_of_location)
        for location_index in range(len(location)):
            list_of_locations.append(location[location_index])
            if not self.location1:
                self.location1 = location[location_index]
            else:
                self.location2 = location[location_index]


class ConversationAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agree = False
        self.age = 0
        # Initial cognitive abilities of the agents which are same for all agents in the beginning
        self.move_model_obj = verb_templates.Move()
        self.give_model_obj = verb_templates.Give()
        self.take_model_obj = verb_templates.Take()
        self.touch_model_obj = verb_templates.Touch()
        self.drop_model_obj = verb_templates.Drop()
        self.lift_model_obj = verb_templates.Lift()
        self.put_model_obj = verb_templates.Put()
        self.bring_model_obj = verb_templates.Bring()
        self.unique_id = unique_id

        self.case_verb_object1 = {"no-marker": 1}
        self.case_verb_subject = {"no-marker": 1}
        self.case_verb_object2 = {"no-marker": 1}

        self.case_item1 = {"no-marker": 1}
        self.case_item2 = {"no-marker": 1}
        self.case_location1 = {"no-marker": 1}
        self.case_location2 = {"no-marker": 1}

    def encode_json(self):
        agent_data = {"subject": self.case_verb_subject.copy(), "obj1": self.case_verb_object1.copy(), "obj2": self.case_verb_object2.copy(),
                      "item1": self.case_item1.copy(), "item2": self.case_item2.copy(), "location1": self.case_location1.copy(),
                      "location2": self.case_location2.copy()}
        return agent_data.copy()

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

    def step(self):
        # For agent to understand its activation context
        # global speaker_listener_toggle
        # Tracks agreement over iterations as binary values in a list
        global agreement_matrix
        # Contains event structure shared context between both agents as a common object
        global world_event_object
        # Variable contains status of current iteration being success(1)/failure(0)
        global language_game_success
        # Contains the string communicated from speaker to listener
        global sentence_communicated
        # Flag for first/second context for speaker
        # global first_turn_speaker
        global conversation_index
        # incorporate_success flag turns to 1 when success has happened and has to be used to adjust probability
        global incorporate_outcome_for_speaker

        # Check if it is the speaker context. This code block contains speaker tasks for the first iteration of speaker.
        if conversation_index == 0:
            active_verb_object = self.get_active_verb_object()
            # Values of subject, object etc reflect world event
            active_verb_object.set_parameters_from_world_event(world_event_object)
            active_verb_object.create_sentence(self)
            sentence_communicated = " ".join(active_verb_object.sentence)
            conversation_index += 1

        elif conversation_index == 1:
            active_verb_object = self.get_active_verb_object()

            active_verb_object.set_parameters_from_world_event(world_event_object)
            active_verb_object.sentence = sentence_communicated.split()
            active_verb_object.parse_sentence(self)
            game_outcome_local = active_verb_object.check_agreement()
            language_game_success = game_outcome_local

            # Incorporate outcome for listener
            active_verb_object.incorporate_game_outcome(language_game_success, 1, self)
            active_verb_object.reset_transient_values()
            conversation_index += 1

        # Speaker
        elif conversation_index > 1 and (conversation_index % 2) == 0:
            active_verb_object = self.get_active_verb_object()
            # incorporate outcome for speaker context here
            if incorporate_outcome_for_speaker == 1:
                active_verb_object.incorporate_game_outcome(language_game_success, 0, self)
                active_verb_object.reset_transient_values()
            else:
                active_verb_object.set_parameters_from_world_event(world_event_object)
                active_verb_object.create_sentence(self)
                sentence_communicated = " ".join(active_verb_object.sentence)
                conversation_index += 1
        # Listener
        elif conversation_index > 1 and (conversation_index % 2) != 0:
            active_verb_object = self.get_active_verb_object()
            active_verb_object.set_parameters_from_world_event(world_event_object)
            active_verb_object.sentence = sentence_communicated.split()
            active_verb_object.parse_sentence(self)
            game_outcome_local = active_verb_object.check_agreement()
            language_game_success = game_outcome_local
            active_verb_object.incorporate_game_outcome(language_game_success, 1, self)
            active_verb_object.reset_transient_values()
            conversation_index += 1


# Model of the world with 'no_of_agents_local' agents
class ConversationModel(Model):
    # Model with 'no_of_agents_local' initial agents

    def __init__(self, no_of_agents_local, no_of_population_nodes):
        self.num_agents = no_of_agents_local
        self.schedule = BaseScheduler(self)
        self.list_of_agent_objects = []
        self.no_of_population_nodes = no_of_population_nodes

        for population_node in range(self.no_of_population_nodes):
            agents_in_node = []
            for agent_index in range(self.num_agents):
                agent = ConversationAgent(agent_index, self)
                agents_in_node.append(agent)
            self.list_of_agent_objects.append(agents_in_node)

    def step(self):
        self.schedule.step()


def increment_age(Language_Model):
    for agent in Language_Model.list_of_agent_objects:
        agent.age += 1


def return_population_nodes(population_nodes, intergroup_probability):
    if random.random() < intergroup_probability:
        active_population_node1 = (random.sample(range(population_nodes), 1)[0])
        active_population_node2 = (random.sample(range(population_nodes), 1)[0])
        while active_population_node2 == active_population_node1:
            active_population_node2 = (random.sample(range(population_nodes), 1)[0])
    else:
        active_population_node1 = (random.sample(range(population_nodes), 1)[0])
        active_population_node2 = active_population_node1
    return active_population_node1, active_population_node2


def check_agent_deletion(Language_Model, no_of_agents, asmr, age_index):
    for agent_index in range(len(Language_Model.list_of_agent_objects)):
        for prob_index in range(len(age_index)):
            # locate the probability of death for current agent's age
            if age_index[prob_index] > Language_Model.list_of_agent_objects[agent_index].age:
                probability_of_death = asmr[prob_index]
                break
        if random.random() < probability_of_death:
            # Remove the agent from list of agents in the world to simulate death
            print("Agent is dead", Language_Model.list_of_agent_objects[agent_index].unique_id, "at age",
                  Language_Model.list_of_agent_objects[agent_index].age)
            del Language_Model.list_of_agent_objects[agent_index]
            # Create new agent
            new_agent = ConversationAgent((Language_Model.list_of_agent_objects[len(Language_Model.list_of_agent_objects) - 1].unique_id + 1), Language_Model)
            Language_Model.list_of_agent_objects.append(new_agent)
            # print("New agent added with id", new_agent.unique_id)
    unique_id_of_agents = []
    for agent_index in range(len(Language_Model.list_of_agent_objects)):
        unique_id_of_agents.append(Language_Model.list_of_agent_objects[agent_index].unique_id)
    # print("Current agents alive are", unique_id_of_agents)


def agent_simulation(simulation_count, output_file, Language_Model, model_parameter_dict):
    global agreement_matrix
    global world_event_object
    global language_game_success
    global conversation_index
    global sentence_communicated
    global incorporate_outcome_for_speaker
    global sentences

    agreement_local_simulation = []

    no_of_iterations = model_parameter_dict["noOfIterations"]
    intergroup_probability = model_parameter_dict["probOfIntergroupCommunication"]
    intergroup_probability_after_maturity = model_parameter_dict["probOfIntergroupCommunicationAfterConvergence"]
    for times_to_iter in range(no_of_iterations):
        if times_to_iter % 10000 == 0:
            print(times_to_iter)
        if population_reconstitution and times_to_iter % iterations_in_one_year == 0:
            check_agent_deletion(Language_Model, no_of_agents, asmr, age_index)
            increment_age(Language_Model)

        random_no_of_names: int = random.randint(model_parameter_dict['noOfNamesRange'][0],
                                                 model_parameter_dict['noOfNamesRange'][1])
        random_no_of_items: int = random.randint(model_parameter_dict['noOfItemsRange'][0],
                                                 model_parameter_dict['noOfItemsRange'][1])
        random_no_of_locations: int = random.randint(model_parameter_dict['noOfLocationsRange'][0],
                                                     model_parameter_dict['noOfLocationsRange'][1])
        sentences = []

        language_game_success = 0
        conversation_index = 0
        incorporate_outcome_for_speaker = 0
        active_population_node1, active_population_node2 = return_population_nodes(population_nodes, intergroup_probability)
        active_agents = random.sample(range(no_of_agents), 2)
        # Global shared context of the event w/ shared internal representation by both agents
        world_event_object = CreateWorldEvent(random_no_of_names, random_no_of_items, random_no_of_locations)

        # Activate first agent for speaker role
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
        Language_Model.step()
        Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
        # Activate second agent for listener role
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node2][active_agents[1]])
        Language_Model.step()
        Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node2][active_agents[1]])
        sentences.append(sentence_communicated)
        # Activate speaker to incorporate game outcome
        incorporate_outcome_for_speaker = 1
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
        Language_Model.step()
        Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
        incorporate_outcome_for_speaker = 0
        # If communication failed, try to re-communicate up to retry_communication_count times
        if language_game_success == 0:
            for i in range(retry_communication_count):
                Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
                Language_Model.step()
                Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
                # Activate second agent again as listener to reattempt communication
                Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node2][active_agents[1]])
                Language_Model.step()
                Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node2][active_agents[1]])
                incorporate_outcome_for_speaker = 1
                Language_Model.schedule.add(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
                Language_Model.step()
                Language_Model.schedule.remove(Language_Model.list_of_agent_objects[active_population_node1][active_agents[0]])
                incorporate_outcome_for_speaker = 0
                sentences.append(sentence_communicated)
                if language_game_success == 1:
                    break
        agreement_local_simulation.append(language_game_success)
        length_last_ten_percent = int(0.1 * len(agreement_local_simulation))
        success_percent_last_ten = int(sum(agreement_local_simulation[-length_last_ten_percent:]) / len(agreement_local_simulation[-length_last_ten_percent:]) * 100)
        if intergroup_probability != intergroup_probability_after_maturity and len(agreement_local_simulation) > 1000 and success_percent_last_ten >= 98:
            intergroup_probability = intergroup_probability_after_maturity
            print("intergroup probability changed to", intergroup_probability, "at game count", times_to_iter)
        if write_dictionary:
            agent_data = {}
            for population_iter in range(population_nodes):
                agent_data_temp = {}
                for agent_iter in range(no_of_agents):
                    agent_data_temp[agent_iter] = Language_Model.list_of_agent_objects[population_iter][agent_iter].encode_json().copy()
                agent_data[population_iter] = agent_data_temp

        # call to data logger:
        if times_to_iter == 0:
            if write_dictionary:
                data_to_add_to_trials = {"iteration": times_to_iter, "outcome": language_game_success,
                                         "active-agents": active_agents,
                                         "sentences": sentences, "agent-state": agent_data,
                                         "population-nodes": [active_population_node1, active_population_node2]}
                del agent_data
            else:
                data_to_add_to_trials = {"iteration": times_to_iter, "outcome": language_game_success,
                                         "active-agents": active_agents,
                                         "sentences": sentences,
                                         "population-nodes": [active_population_node1, active_population_node2]}
            existing_data = {"model_parameters": model_parameter_dict, "trials": []}
            existing_data["trials"].append(data_to_add_to_trials.copy())

        else:
            if write_dictionary:
                data_to_add_to_trials = {"iteration": times_to_iter, "outcome": language_game_success,
                                         "active-agents": active_agents,
                                         "sentences": sentences, "agent-state": agent_data,
                                         "population-nodes": [active_population_node1, active_population_node2]}
                del agent_data
            else:
                data_to_add_to_trials = {"iteration": times_to_iter, "outcome": language_game_success,
                                         "active-agents": active_agents,
                                         "sentences": sentences,
                                         "population-nodes": [active_population_node1, active_population_node2]}
            if times_to_iter % 100 == 0:
                existing_data["trials"].append(data_to_add_to_trials.copy())
            del data_to_add_to_trials
        if times_to_iter % 10000 == 0 and times_to_iter > 0:
            part = times_to_iter / 10000
            part = str(int(part))
            filename = output_file.replace(".json", "part-" + part + ".json")
            print('saving file part ', part, 'at iteration ', times_to_iter)
            data_and_stats_methods.log_output_for_trial_to_file_in_parts(filename, existing_data, part)
            existing_data["trials"] = []
    part = int(times_to_iter / 10000) + 1
    part = str(part)
    filename = output_file.replace(".json", "part-" + part + ".json")
    print('saving file part ', part, 'at iteration ', times_to_iter)
    data_and_stats_methods.log_output_for_trial_to_file_in_parts(filename, existing_data, part)
    # print(agreement_local_simulation)
    # data_and_stats_methods.log_output_for_trial_to_file(output_file, existing_data)
    agreement_matrix.append(agreement_local_simulation)
    avg = sum(agreement_local_simulation) / len(agreement_local_simulation)
    percent_agreement = avg * 100
    print("Percentage of times that agents agreed is", int(percent_agreement))
    communicative_success = []
    iteration_index = []
    for index in range(len(agreement_local_simulation) // rolling_window):
        m = index * rolling_window
        n = m + (rolling_window - 1)
        summation = sum(agreement_local_simulation[m:n])
        communicative_success.append(summation / (n - m))
        iteration_index.append(m)
    print(communicative_success)
    return communicative_success, iteration_index

if __name__ == '__main__':
    with open("model_parameters.json") as parameters:
        model_parameter_dict = json.load(parameters)
    no_of_agents = model_parameter_dict["noOfAgents"]
    prob_adjust_value = model_parameter_dict["probAdjustValue"]
    retry_communication_count = model_parameter_dict["retryCommunicationCount"]
    write_dictionary = model_parameter_dict["writeDictionaryStates"]
    rolling_window = model_parameter_dict["rollingWidowSuccess"]
    population_reconstitution = model_parameter_dict["reconstitutePopulation"]
    asmr = model_parameter_dict["ageSpecificMortalityRate"]
    age_index = model_parameter_dict["ageRange"]
    iterations_in_one_year = model_parameter_dict["iterationsInOneYear"]
    population_nodes = model_parameter_dict["numberOfPopulationClusters"]

    simulation_count = model_parameter_dict["simulationRunCount"]
    output_filename = model_parameter_dict['nameOfOutputFile']
    del parameters
    success_matrix = []
    iteration_matrix = []

    for simulation in range(simulation_count):
        print(simulation, 'th run of the simutation')
        Language_Model = ConversationModel(int(no_of_agents), int(population_nodes))
        output_file = output_filename + str(simulation) + '.json.gz'
        communicative_success, iteration_index = agent_simulation(simulation, output_file, Language_Model, model_parameter_dict)
        success_matrix.append(communicative_success)
        iteration_matrix.append(iteration_index)
    mean_outcome = []
    for trial_count in range(len(success_matrix[0])):
        mean = 0
        for simulation_outcome in range(len(success_matrix)):
            mean += success_matrix[simulation_outcome][trial_count]
        mean = mean / len(success_matrix)
        mean_outcome.append(mean)
    plt.plot(iteration_matrix[0], mean_outcome)
    plt.xlabel("Language game count")
    plt.ylabel("Communicative success")
    plt.show()
