import pygame
import sys
import time

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
MARGIN = 2  # space between blocks
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (12, 53, 71)

basic = WHITE  # empty block color
start = GREEN  # starting block color
end = RED  # ending block color
wall = DARK_BLUE  # walls color
pth = YELLOW  # found path color
visited = CYAN  # visited blocks color

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN.fill(BLACK)
pygame.draw.rect(
    SCREEN, GREY, (20, 20, SCREEN_WIDTH - 52 - MARGIN, SCREEN_HEIGHT - 40 - MARGIN)
)
pygame.display.set_caption("Algorithm Visualization")


class Block:
    """Class that represents one single block from the grid"""

    def __init__(self, x, y, block_size):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.color = basic

    def draw(self):
        """Draws the block on the screen"""
        pygame.draw.rect(
            SCREEN, self.color, (self.x, self.y, self.block_size, self.block_size)
        )

    def set_color(self, color):
        """Changes the color of the block and animates it"""
        if self.color != wall and self.color != start and self.color != end:
            self.color = color
            animate(
                color,
                ((self.x) + self.block_size / 2, (self.y) + self.block_size / 2),
                self.block_size,
            )
        elif self.color == wall and color == basic:
            self.color = color
            animate(
                color,
                ((self.x) + self.block_size / 2, (self.y) + self.block_size / 2),
                self.block_size,
            )


class Grid:
    """Class that represents the whole grid of blocks"""

    def __init__(self, block_size):
        self.block_size = block_size
        self.blocks = []
        self.r = 0  # rows
        self.c = 0  # columns
        # initiliazing empty grid
        for i in range(20, SCREEN_WIDTH - 40, self.block_size + MARGIN):
            self.blocks.append([])
            for j in range(20, SCREEN_HEIGHT - 20, self.block_size + MARGIN):
                square = Block(i, j, self.block_size)
                self.blocks[self.r].append(square)
                if self.r == 0:
                    self.c += 1
            self.r += 1

        # start block
        self.blocks[int(self.r / 7)][int(self.c / 7)].set_color(start)

        # end block
        self.blocks[int(self.r / 1.5)][int(self.c / 1.5)].set_color(end)

    def draw(self):
        """Draws the grid on the screen"""
        for blocks in self.blocks:
            for block in blocks:
                block.draw()

    def find_position(self, mouse_x, mouse_y):
        """Returns block position in the 2d array (blocks) by given mouse coordinates"""
        i = 0
        for blocks in self.blocks:
            j = 0
            for block in blocks:
                if (
                    mouse_x > block.x
                    and mouse_x < block.x + self.block_size
                    and mouse_y > block.y
                    and mouse_y < block.y + self.block_size
                ):
                    return i, j
                j += 1
            i += 1
        return i, j

    def path(self, lst):
        """Sets the color of the found path"""
        for node in lst:
            self.blocks[node[0]][node[1]].set_color(pth)


class Node:
    def __init__(self, position, parent):
        self.position = position
        self.parent = parent
        self.g = 0  # Distance to start node
        self.h = 0  # Distance to goal node
        self.f = 0  # Total cost

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Sort nodes
    def __lt__(self, other):
        return self.f < other.f


def animate(color, center, block_size):
    """Animates the filling of a block"""
    step = 1
    while step < block_size / 2:
        pygame.draw.circle(SCREEN, color, center, step)
        step += 1
        time.sleep(0.01)
        pygame.display.update()


def add_to_open(open, neighbor):
    """checks if a neighbor should be added to open list"""
    for node in open:
        if neighbor == node and neighbor.f >= node.f:
            return False
    return True


def a_star(grid, start, end):
    """A-star algorithm implementation"""
    # open and closed nodes
    open_nodes = []
    closed_nodes = []

    # Create a start node and an goal node
    start_node = Node(start, None)
    goal_node = Node(end, None)

    # Add the start node
    open_nodes.append(start_node)

    # Loop until the open list is empty
    while len(open_nodes) > 0:
        for event in pygame.event.get():
            # Checks for quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Sort the open list to get the node with the lowest cost first
        open_nodes.sort()

        # Get the node with the lowest cost
        current_node = open_nodes.pop(0)

        # Add the current node to the closed list
        (i, j) = current_node.position
        grid.blocks[i][j].set_color(visited)
        pygame.display.update(grid.blocks[i][j].draw())
        closed_nodes.append(current_node)

        # Check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            # Return reversed path
            return path[::-1]

        # Unzip the current node position
        (x, y) = current_node.position

        # Get neighbors
        neighbors = []
        if x - 1 >= 0:
            neighbors.append((x - 1, y))
        if x + 1 < grid.r:
            neighbors.append((x + 1, y))
        if y - 1 >= 0:
            neighbors.append((x, y - 1))
        if y + 1 < grid.c:
            neighbors.append((x, y + 1))

        # Loop neighbors
        for next in neighbors:
            # Get value from grid
            grid_value = grid.blocks[next[0]][next[1]]

            # Check if the node is a wall
            if grid_value.color == wall:
                continue

            # Create a neighbor node
            neighbor = Node(next, current_node)

            # Check if the neighbor is in the closed list
            if neighbor in closed_nodes:
                continue

            # Generate heuristics (Manhattan distance)
            neighbor.g = abs(neighbor.position[0] - start_node.position[0]) + abs(
                neighbor.position[1] - start_node.position[1]
            )
            neighbor.h = abs(neighbor.position[0] - goal_node.position[0]) + abs(
                neighbor.position[1] - goal_node.position[1]
            )
            neighbor.f = neighbor.g + neighbor.h

            # Check if neighbor is in open list and if it has a lower f value
            if add_to_open(open_nodes, neighbor) == True:
                open_nodes.append(neighbor)


def breadth_first_search(grid, start, end):
    """Breadth-First Search algorithm implementation"""
    # open and closed nodes
    open_nodes = []
    closed_nodes = []

    # Create a start node and an goal node
    start_node = Node(start, None)
    goal_node = Node(end, None)

    # Add the start node
    open_nodes.append(start_node)

    # Loop until the open list is empty
    while len(open_nodes) > 0:
        for event in pygame.event.get():
            # Checks for quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get the first node (FIFO)
        current_node = open_nodes.pop(0)

        # Add the current node to the closed list
        (i, j) = current_node.position
        grid.blocks[i][j].set_color(visited)
        grid.blocks[i][j].draw()
        pygame.display.update()
        closed_nodes.append(current_node)

        # Check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            # Return reversed path
            return path[::-1]

        # Unzip the current node position
        (x, y) = current_node.position

        # Get neighbors
        neighbors = []
        if x - 1 >= 0:
            neighbors.append((x - 1, y))
        if x + 1 < grid.r:
            neighbors.append((x + 1, y))
        if y - 1 >= 0:
            neighbors.append((x, y - 1))
        if y + 1 < grid.c:
            neighbors.append((x, y + 1))

        # Loop neighbors
        for next in neighbors:
            # Get value from grid
            grid_value = grid.blocks[next[0]][next[1]]

            # Check if the node is a wall
            if grid_value.color == wall:
                continue

            # Create a neighbor node
            neighbor = Node(next, current_node)

            # Check if the neighbor is in the closed list
            if neighbor in closed_nodes:
                continue

            # Everything is green, add the node if it's not closed
            if neighbor not in open_nodes:
                open_nodes.append(neighbor)


def main():
    block_size = 20
    clock = pygame.time.Clock()
    grid = Grid(block_size)

    # Start of the game cycle
    while True:
        grid.draw()
        for event in pygame.event.get():
            # Checks for quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Checks for clicking of mouse buttons (0 - left, 2 - right)
            if pygame.mouse.get_pressed()[0]:
                mousePosition = pygame.mouse.get_pos()
                pos = grid.find_position(mousePosition[0], mousePosition[1])
                if pos[0] < len(grid.blocks) and pos[1] < len(grid.blocks):
                    grid.blocks[pos[0]][pos[1]].set_color(wall)

            elif pygame.mouse.get_pressed()[2]:
                mousePosition = pygame.mouse.get_pos()
                pos = grid.find_position(mousePosition[0], mousePosition[1])
                if pos[0] < len(grid.blocks) and pos[1] < len(grid.blocks):
                    grid.blocks[pos[0]][pos[1]].set_color(basic)

            if event.type == pygame.KEYDOWN:
                # 'r' resets the board
                if event.key == pygame.K_r:
                    grid = Grid(block_size)
                # 'b' runs Breadth-first search algorithm
                if event.key == pygame.K_b:
                    grid.path(
                        breadth_first_search(
                            grid,
                            (int(grid.r / 7), int(grid.c / 7)),
                            (int(grid.r / 1.5), int(grid.c / 1.5)),
                        )
                    )
                # 'a' runs A-star algorithm
                if event.key == pygame.K_a:
                    grid.path(
                        a_star(
                            grid,
                            (int(grid.r / 7), int(grid.c / 7)),
                            (int(grid.r / 1.5), int(grid.c / 1.5)),
                        )
                    )

        pygame.display.update()

        # Updates the screen and sets fps
        clock.tick(60)
        pygame.display.flip()


if __name__ == "__main__":
    main()