import matplotlib.pyplot as plt
import networkx as nx
from os import walk
from itertools import combinations
import random as rd
from random import random
import time
from os import system, name
import warnings

warnings.filterwarnings("ignore")


# define our clear function
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def plot_graph(g):
    pos = nx.spring_layout(g)
    nx.draw_networkx(g, pos)
    plt.title('Random Graph')
    plt.show()


def edge_relation(n, p):
    vertex = set([v for v in range(n)])
    edge = set()
    for combination in combinations(vertex, 2):
        prob = random()
        if prob < p:
            edge.add(combination)
    g = nx.Graph()
    g.add_nodes_from(vertex)
    g.add_edges_from(edge)
    plot_graph(g)
    return g


def read_graph(path):
    k = nx.read_gml(path)
    print(nx.info(k))
    vertex = set(nx.nodes(k))
    edge = set(nx.edges(k))
    g = nx.Graph()
    g.add_nodes_from(vertex)
    g.add_edges_from(edge)
    print("Finished Reading Graph")
    print()
    return g


def read_hospitals(filename):
    hospitals = []
    f = open(filename, "r")
    for line in f:
        if (line[0] != '#'):
            hospitals.append(int(line))
    hospitals = [str(h) for h in hospitals]
    return hospitals


def create_hospitals(num, vertices):
    hospital_list = []
    while len(hospital_list) < num:
        hop = str((rd.randrange(0, vertices, 1)))
        if hop in hospital_list:
            continue
        hospital_list.append(hop)
    return hospital_list


def choose_graph():
    while True:
        print()
        print("Choose your graph: ")
        print("1. Pre-defined Graph")
        print("2. Real Road Network")
        print("3. Generate a Random Graph")
        print("4. Exit")
        try:
            choice = int(input())
        except ValueError:
            continue
        if choice > 4 or choice < 1:
            print("Please choose a valid option")
            continue
        return choice


def choose_hospital():
    while True:
        print("1. Use existing hospital list")
        print("2. Generate random hospitals")
        print("3. Back")
        try:
            choice = int(input())
        except ValueError:
            continue
        if 1 <= choice <= 3:
            return choice


def get_files(path):
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
    return files


def choose_file(files, path):
    while True:
        print()
        print("Enter your file choice:")
        print()
        for i in range(len(files)):
            print(i + 1, ". ", files[i])
        print("Enter 0 to go back")
        try:
            choice = int(input())
        except ValueError:
            continue
        if 1 <= choice <= len(files):
            return path + "\\" + files[choice - 1]
        elif choice == 0:
            return 0
        else:
            print("Please enter a valid choice")


def choose_algorithm():
    while True:
        print()
        print("Choose your task: ")
        print("1. Find the nearest hospital")
        print("2. Find the nearest hospital (Time complexity doesn't depend on h)")
        print("3. Find the 2 nearest hospitals")
        print("4. Find k nearest hospitals")
        print("5. Back")
        try:
            choice = int(input())
        except ValueError:
            continue
        if 1 <= choice <= 5:
            return choice
        else:
            print("Please enter a valid choice")


def algorithm_A(node):
    global shortest_path
    if node in shortest_path:  # If node's nearest hospital is found
        return
    elif node in hospitals:  # If node is hospital, then no need to find the nearest hospital
        shortest_path[node] = [node]
        return

    else:
        connection_node = None
        min_cost = float('inf')
        queue = []
        explored_nodes = {}  # Marking the nodes as visited and keeping a track of their parent

        queue.append(node)
        explored_nodes[node] = [0, None]

        while len(queue) > 0:
            cur_node = queue.pop(0)
            if cur_node in hospitals:  # If node is a hospital Then retrieve path
                retrieve_path(cur_node, explored_nodes)
                break

            # If the cost of expansion is greater than the candidate for nearest hospital then retrieve path
            elif explored_nodes[cur_node][0] > min_cost and connection_node is not None:
                retrieve_path(connection_node, explored_nodes)
                break

            # If the node's nearest hospital has been found, set the hospital as a candidate hospital and record the
            # distance
            elif cur_node in shortest_path:
                if len(shortest_path[cur_node]) - 1 + explored_nodes[cur_node][0] < min_cost:
                    min_cost = len(shortest_path[cur_node]) - 1 + explored_nodes[cur_node][0]
                    connection_node = cur_node
                else:
                    continue

            # Else perform normal Breadth First Search
            else:
                for neighbor in graph[cur_node]:
                    if neighbor in explored_nodes:
                        continue
                    explored_nodes[neighbor] = [explored_nodes[cur_node][0] + 1, cur_node]
                    queue.append(neighbor)

        # If the candidate hospital is the only hospital connected to the node
        if connection_node is not None and node not in shortest_path:
            retrieve_path(connection_node, explored_nodes)

        # If the no hospital is connected to the node
        elif connection_node is None and node not in shortest_path:
            shortest_path[node] = []


def retrieve_path(node, expanded_nodes):
    # If node's shortest path has not been found then it is a hospital and set its path as [node]
    if node not in shortest_path:
        shortest_path[node] = [node]
    # Retrieve the paths until we reach the source node (Parent is None)
    while expanded_nodes[node][1] is not None:
        shortest_path[expanded_nodes[node][1]] = [expanded_nodes[node][1]] + shortest_path[node]
        node = expanded_nodes[node][1]


def print_path(shortest_path, algo):
    file_out = "output\\output_" + algo + ".txt"
    print(shortest_path)
    output = open(file_out, "w")
    for node in shortest_path:
        path = shortest_path[node]
        path_length = len(shortest_path[node]) - 1
        if path_length == -1:
            string = "Node " + node + " has no hospital connected to it"
            output.write(string + "\n")
            print("Node ", node, " has no hospital connected to it")
            continue
        path = '-'.join(path)
        string = "Shortest Path length for Node " + node + " is: " + str(path_length)
        output.write(string + "\n")
        print("Shortest Path length for Node ", node, " is: ", path_length)
        string = "Shortest Path is: " + path
        output.write(string + "\n")
        print("Shortest Path is: ", path)
    if algo == 'B':
        for node in graph:
            if node not in shortest_path:
                print("Node: ", node, " has no hospital connected to it")
    output.close()


def algorithm_B(adjacency_list, hospitals):
    visited_nodes = []
    queue = []
    path = {}
    for h in hospitals:  # Enqueue all hospitals
        if h not in adjacency_list:
            continue
        queue.append(h)
        visited_nodes.append(h)  # Mark hospital as visited
        path[h] = [h]

    while len(queue) > 0:
        node = queue.pop(0)
        for neighbour in adjacency_list[node]:
            if neighbour in hospitals:  # If neighbour is hospital, continue next iteration
                continue
            elif neighbour in visited_nodes:  # If neighbour has been visited, continue next iteration
                continue
            else:
                visited_nodes.append(neighbour)  # Mark neighbour as visited
                queue.append(neighbour)  # Enqueue neighbour
                path[neighbour] = [neighbour] + path[node]  # Store shortest path
    return path


def print_info(nearest_hospitals, k, algo):
    global graph
    file_out = "output\\output_" + algo + ".txt"
    output = open(file_out, "w")
    for node in nearest_hospitals:
        if node in hospitals:
            continue
        hospital_list = ', '.join(nearest_hospitals[node])
        if len(nearest_hospitals[node]) < k:
            string = "Node: " + node + " doesnt have " + str(k) + " hospitals connected to it"
            output.write(string + "\n")
            print("Node: ", node, " doesnt have ", k, " hospitals connected to it")
            string = "The closest hospitals are: " + hospital_list
            output.write(string + "\n")
            print("The closest hospitals are: ", hospital_list)

        else:
            string = "The top " + str(k) + " closest hospitals to Node: " + node + " are: " + hospital_list
            print("The top ", k, " closest hospitals to Node: ", node, " are: ", hospital_list)
            output.write(string + "\n")
    for node in graph:
        if node not in nearest_hospitals:
            print("Node: ", node, " has no hospital connected to it")

    output.close()


def algorithm_C_D(adjacency_list, hospitals, k):
    nearest_hospitals = {}
    visited_nodes = []
    queue = []

    # Enqueue all the hospitals and mark them as visited
    for node in hospitals:
        if node not in adjacency_list:
            continue
        entry = (node, node)
        queue.append(entry)
        visited_nodes.append(entry)

    while len(queue) > 0:
        node = queue.pop(0)
        for neighbor in adjacency_list[node[0]]:
            entry = (neighbor, node[1])
            # If its the first time reaching that node, set its list to empty list
            if neighbor not in nearest_hospitals:
                nearest_hospitals[neighbor] = []
            # If k nearest hospitals have been found then don't enqueue the node again
            if len(nearest_hospitals[neighbor]) == k:
                continue
            # If the (Node id, Hospital id) pair has not been visited then enqueue and mark as visited.
            # Append the hospital into the hospital list of node
            if entry not in visited_nodes:
                visited_nodes.append(entry)
                nearest_hospitals[neighbor].append(node[1])
                queue.append(entry)
    return nearest_hospitals


while True:
    graph_choice = choose_graph()
    if graph_choice == 4:
        print("Exiting Application")
        break

    else:
        clear()
        while True:
            flag = False
            file_choice = -1
            if graph_choice == 1:
                file = 'predefined graphs'
                available_graphs = get_files(file)
                file_choice = choose_file(available_graphs, file)
            elif graph_choice == 2:
                file = 'real road networks'
                available_graphs = get_files(file)
                file_choice = choose_file(available_graphs, file)
            else:
                while True:
                    try:
                        n = int(input('Enter number of nodes: '))
                        p = float(input('Enter probability: '))
                        break
                    except ValueError:
                        continue

            if file_choice == 0:
                clear()
                break
            elif file_choice == -1:
                nx.write_gml(edge_relation(n, p), 'random_graph.txt')
                graph = nx.to_dict_of_lists(read_graph('random_graph.txt'))
            else:
                graph = nx.to_dict_of_lists(read_graph(file_choice))
            clear()
            while True:
                hospital_choice = choose_hospital()
                if hospital_choice == 3:
                    if file_choice == -1:
                        flag = True
                    clear()
                    break
                elif hospital_choice == 1:
                    hospitals = read_hospitals("Hospitals.txt")
                else:
                    try:
                        hos = int(input("Enter the number of hospitals to generate: "))
                    except ValueError:
                        print("Error input... Creating 3 hospitals by default")
                        hos = 3
                    hospitals = create_hospitals(hos, len(graph))
                    print("The hospitals are: \n", hospitals)
                    enter = input("Press enter to continue")
                clear()
                while True:
                    algorithm_choice = choose_algorithm()
                    if algorithm_choice == 5:
                        clear()
                        break
                    elif algorithm_choice == 1:
                        shortest_path = {}
                        print(hospitals)
                        for node in graph:
                            algorithm_A(node)
                        print_path(shortest_path, 'A')

                    elif algorithm_choice == 2:
                        result = algorithm_B(graph, hospitals)
                        print_path(result, 'B')

                    elif algorithm_choice == 3:
                        result = algorithm_C_D(graph, hospitals, 2)
                        print_info(result, 2, 'C')
                    elif algorithm_choice == 4:
                        try:
                            k = int(input("Enter the number of hospitals to find for each node: "))
                        except ValueError:
                            print("Using k = 2 as default value")
                        print(hospitals)
                        result = algorithm_C_D(graph, hospitals, k)
                        print_info(result, k, 'D')

            if flag:
                break

time.sleep(2)
