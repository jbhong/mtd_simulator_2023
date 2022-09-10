import simpy
from mtdnetwork.network.targetnetwork import Network as TargetNetwork
from mtdnetwork.network.time_network import TimeNetwork
from mtdnetwork.event.mtd_event import mtd_trigger_action
from mtdnetwork.constants import ATTACKER_THRESHOLD
from mtdnetwork.event.attack_event import Adversary

# Simulation time in seconds
SIM_TIME = 1000
# parameters for network layer capacity and application layer capacity
NL_CAPACITY = 1
AL_CAPACITY = 1


def create_network(env):
    target_network = TargetNetwork(total_nodes=200, total_endpoints=20, total_subnets=20, total_layers=5,
                                   target_layer=2)
    graph = target_network.get_graph_copy()
    colour_map = target_network.get_colourmap()
    pos = target_network.get_pos()
    node_per_layer = target_network.get_node_per_layer()
    users_list = target_network.get_users_list()
    users_per_host = target_network.get_users_per_host()
    time_network = TimeNetwork(env, graph, pos, colour_map, 200, 20, 20, 5, node_per_layer, users_list, users_per_host)
    return time_network


def run_sim():

    # set up event execution environment
    env = simpy.Environment()

    # initialise network to perform MTD strategies
    time_network = create_network(env)

    # set up dataframe for collecting event data
    mtd_operation_record = []
    attack_operation_record = []

    # triggering adversary
    adversary = Adversary(env=env, network=time_network, attack_threshold=ATTACKER_THRESHOLD,
                          attack_operation_record=attack_operation_record)

    # triggering mtd events
    env.process(mtd_trigger_action(env=env, network=time_network,
                                   adversary=adversary, mtd_operation_record=mtd_operation_record))

    # Execute!
    env.run(until=SIM_TIME)

    return mtd_operation_record, attack_operation_record


if __name__ == "__main__":
    run_sim()
