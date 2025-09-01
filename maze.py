from dataclasses import dataclass
import random
import matplotlib.pyplot as plt
import networkx as nx

plt.ion()   # turn on interactive mode
fig, ax = plt.subplots()

@dataclass
class Node:
    x: int
    y: int

edge_dict = dict()
size = 25

start_y, start_x = 0, 0

graph = [Node(y,x) for x in range(size) for y in range(size)]
visited = [[False for _ in range(size)] for _ in range(size)]

def get_new_neighbors(y,x):
    nbs = []

    # up
    if y-1 >= 0:
        if not visited[y-1][x]:
            nbs.append((y-1, x))
    
    # down
    if y+1 < size:
        if not visited[y+1][x]:
            nbs.append((y+1, x))

    # left
    if x-1 >= 0:
        if not visited[y][x-1]:
            nbs.append((y, x-1))

    # right
    if x+1 < size:
        if not visited[y][x+1]:
            nbs.append((y, x+1))
    
    return nbs

def search(y,x):
    visited[y][x] = True
    edge_dict[(y,x)] = []

    # plot_edges(edge_dict)
    nbs = get_new_neighbors(y,x)

    if not nbs:
        return
    
    random.shuffle(nbs)

    while nbs:
        nb = (ny,nx) = nbs[0]
        if not visited[ny][nx]: 
            edge_dict[(y,x)].append(nb)
            search(ny, nx)
            nbs = get_new_neighbors(y,x)
            random.shuffle(nbs)
    
    return

def plot_edges(edge_dict):
    ax.clear()
    G = nx.Graph()

    for node, neighbors in edge_dict.items():
        for nb in neighbors:
            G.add_edge(node, nb)

    pos = { (y,x):(x,-y) for (y,x) in G.nodes }
    nx.draw(G, pos, with_labels=True, node_size=400,
            node_color="skyblue", font_size=8, font_weight="bold", ax=ax)
    plt.draw()

def plot_maze_from_edges(edge_dict, size):
    passages = set()
    for a, nbs in edge_dict.items():
        for b in nbs:
            passages.add(tuple(sorted((a, b))))

    def connected(a, b):
        return tuple(sorted((a, b))) in passages

    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect("equal")

    # --- interior walls ---
    for y in range(size):
        for x in range(size):
            if x+1 < size and not connected((y,x),(y,x+1)):
                ax.plot([x+1,x+1],[y,y+1], color="black", lw=2)

            if y+1 < size and not connected((y,x),(y+1,x)):
                ax.plot([x,x+1],[y+1,y+1], color="black", lw=2)

    # top
    for x in range(size):
        ax.plot([x,x+1],[0,0], color="black", lw=2)
    
    # left
    for y in range(size):
        if not (y == 0):  # open at 0,0
            ax.plot([0,0],[y,y+1], color="black", lw=2)
    
    # right
    for y in range(size):
        if not (y == size-1):  # open at bottom right
            ax.plot([size,size],[y,y+1], color="black", lw=2)
    
    # bottom
    for x in range(size):
        ax.plot([x,x+1],[size,size], color="black", lw=2)

    ax.set_xlim(0,size)
    ax.set_ylim(size,0)
    ax.axis("off")
    plt.show()

search(start_y, start_x)
plot_maze_from_edges(edge_dict, size)
input()