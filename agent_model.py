import data
from mesa import Agent, Model
from mesa.time import BaseScheduler
import random
import verb_templates

global active_agents
global speaker_listener_toggle
agreement_matrix = []


class CreateWorldEvent():
    # Objects of this class can be initialised for every iteration of world
    # They are initialised by random generated number of names, number of objects and no of locations in the event
    # They set names in variables that represent shared internal representation between agents for a world event
    def __init__(self, no_of_names, no_of_items, no_of_location):
        dataobj = data.namesAndObjects

        event_selected = random.sample(verb_templates.verb_list, 1)  # Select the action verb event at random
        event_selected = event_selected[0]

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

        move_model_obj = verb_templates.Move()
        give_model_obj = verb_templates.Give()
        take_model_obj = verb_templates.Take()
        touch_model_obj = verb_templates.Touch()
        drop_model_obj = verb_templates.Drop()
        lift_model_obj = verb_templates.Lift()
        put_model_obj = verb_templates.Put()
        bring_model_obj = verb_templates.Bring()

    def step(self):
        global active_agents
        global speaker_listener_toggle
        global agreement_matrix
        global returned_object
        self.first_turn_speaker = True
        agreement = 0
        check = False

        # if (active_agents[0] == self.unique_id or active_agents[1] == self.unique_id) and flag != 1:
        # if (active_agents[0] == self.unique_id or active_agents[1] == self.unique_id):
            # no_of_calls += 1
            # event_selected = random.sample(verb_templates.verb_list, 1)
            # event_selected = event_selected[0]

        print(self.unique_id)

        # Check if it is the speaker context. This code block contains speaker tasks for the first iteration of speaker.
        # Need to-do a mechanism for generation, tracking and using markers when required.
        if speaker_listener_toggle != 1:
            speaker_listener_toggle = 1
            # TODO commented below fix logic
            # returned_object.create_sentence()

        # if active_agents[0] == self.unique_id:
        #     print("agent", self.unique_id, "said \n", ' '.join(returned_object.sentence))

        # This code block contains listener context. It should also add any unprocessed markers to the dictionary of markers.
        elif speaker_listener_toggle == 1 and self.first_turn_speaker is True:
        # elif active_agents[1] == self.unique_id:
        # TODO fix logic below commented
        #     agreement = returned_object.check_agreement()
            print(agreement)
            agreement_matrix.append(agreement)
            check = True
            self.first_turn_speaker = False

        # This code block contains speaker context after it receives feedback and should modify scores
        if agreement and check:
            print("agent", active_agents[0], "said \n", ' '.join(returned_object.sentence))
            print("Agent", active_agents[1], "understands what is said")
        elif not agreement and check:
            print("agent", active_agents[0], "said \n", ' '.join(returned_object.sentence))
            print("Agent", active_agents[1], "does not understands what is said")


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


Language_Model = ConversationModel(10)
for times_to_iter in range(3):
    print("\n")
    speaker_listener_toggle = 0
    active_agents = random.sample(range(10), 2)
    active_agents.append(active_agents[0])
    # print(active_agents)

    # Change this to new class CreateWorldEvent object
    # TODO randomise the values of number of names, items and locations
    world_event_object = CreateWorldEvent(0, 0, 0)
    # list_of_names, list_of_items, list_of_locations = create_world_event(2, 1, 1)
    #Global shared context of the event w/ shared internal representation by both agents

    for things in active_agents:
        Language_Model.schedule.add(Language_Model.list_of_agent_objects[things])
    # print(Language_Model.schedule.agents[0])
    Language_Model.step()
    # Language_Model.schedule

avg = sum(agreement_matrix) / len(agreement_matrix)
percent_agreement = avg * 100
print("Percentage of times that agents agreed is", percent_agreement)
