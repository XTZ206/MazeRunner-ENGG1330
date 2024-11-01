from blocks import Block, get_block

class Sprite:
    def __init__(self, win, height, width, blocks):
        self.win = win
        self.height = height
        self.width = width
        self.blocks = blocks
    
    def draw(self):
        raise NotImplementedError

class MovableSprite(Sprite):
    def move(self, dy, dx):
        if dy == 0 and dx == 0:
            return False
        elif not self.maze.check_route(self.y + dy, self.x + dx):
            return False
        
        else:
            self.y += dy
            self.x += dx
            return True

class Maze(Sprite):
    def __init__(self, win, height, width, blocks, start, end):
        super().__init__(win, height, width, blocks)
        self.start = start
        self.end = end

    def check_inrange(self, y, x):
        return 0 <= y < self.height and 0 <= x < self.width

    def check_solid(self, y, x):
        index = y * self.width + x
        return self.blocks[index].is_solid
    
    def check_route(self, y, x):
        return self.check_inrange(y, x) and not self.check_solid(y, x)
    
    def check_bonus(self, y, x):
        index = y * self.width + x
        return self.blocks[index] == get_block("bonus")
    
    def update_bonus(self, y, x):
        index = y * self.width + x
        if self.check_bonus(y, x):
            self.blocks[index] = get_block("air")
    
    def check_box(self, y, x):
        index = y * self.width + x
        return self.blocks[index] == get_block("box")

    def check_box_pushable(self, y, x, dy, dx):
        ny, nx = y + dy, x + dx
        if not self.check_box(y, x):
            return 0
        elif self.check_box(ny, nx):
            n = self.check_box_pushable(ny, nx, dy, dx)
            return 0 if n == 0 else n + 1
        elif self.check_route(ny, nx):
            return 1
        else:
            return 0

    def update_box(self, y, x, dy, dx, n):
        ny, nx = y + dy * n, x + dx * n
        index = y * self.width + x
        nindex = ny * self.width + nx
        self.blocks[index] = get_block("air")
        self.blocks[nindex] = get_block("box")

    @staticmethod
    def get_distance(y1, x1, y2, x2):
        return abs(y1- y2) + abs(x1 - x2)

    def get_neighbours(self, y, x):
        neighbours = []
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if self.check_inrange(ny, nx) and not self.check_solid(ny, nx):
                neighbours.append((ny, nx))
        return neighbours

    def draw(self):
        for index, block in enumerate(self.blocks):
            y, x = divmod(index, self.width)
            block.draw(self.win, y, x)


class Player(MovableSprite):
    def __init__(self, win, height, width, blocks, maze):
        super().__init__(win, height, width, blocks)
        self.y, self.x = maze.start
        self.maze = maze
        self.score = 1000 # BASIC SCORE
        self.step = 0

    def check_win(self):
        return (self.y, self.x) == self.maze.end
    
    def check_lose(self, chasers):
        for chaser in chasers:
            if (chaser.y, chaser.x) == (self.y, self.x):
                return True
        return False
    
    def check_bonus(self):
        if self.maze.check_bonus(self.y, self.x):
            self.score += 1000 # BONUS SCORE

    def move(self, dy, dx):
        ny, nx = self.y + dy, self.x + dx
        if dy == dx == 0:
            return False
        if not self.maze.check_route(ny, nx):
            return False
        if self.maze.check_box(ny, nx):
            n = self.maze.check_box_pushable(ny, nx, dy, dx)
            if n == 0:
                return False
            else:
                self.maze.update_box(ny, nx, dy, dx, n)
        
        super().move(dy, dx)

        if self.maze.check_bonus(self.y, self.x):
            self.maze.update_bonus(self.y, self.x)
            self.score += 10000 # BONUS SCORE
        self.step += 1
        self.score -= 10 # STEP SCORE

        return True
        
    def draw(self):
        block = self.blocks[0]
        block.draw(self.win, self.y, self.x)


class Chaser(MovableSprite):
    def __init__(self, win, height, width, blocks, maze, route):
        super().__init__(win, height, width, blocks)
        self.maze = maze
        self.route = route
        self.y, self.x = route[0]
    
    def draw(self):
        block = self.blocks[0]
        block.draw(self.win, self.y, self.x)


class AutoChaser(Chaser):
    def __init__(self, win, height, width, blocks, maze, route, player):
        super().__init__(win, height, width, blocks, maze, route)
        self.player = player

    def search(self):
        start = self.y, self.x
        end = self.player.y, self.player.x
        open_nodes = [start]
        closed_nodes = []
        prev_nodes = {start: None}
        costs = {start: 0}

        while open_nodes:
            open_nodes.sort(key=lambda node: costs[node] + self.maze.get_distance(*node, *end))
            open_node = open_nodes.pop(0)
            closed_nodes.append(open_node)

            # Path Found and Return
            if open_node == end:
                path = []
                curr = end
                while curr != None:
                    path.append(curr)
                    curr = prev_nodes[curr]
                path.reverse()
                return path
            
            for neighbour_node in self.maze.get_neighbours(*open_node):
                if neighbour_node not in closed_nodes and neighbour_node not in open_nodes:
                    open_nodes.append(neighbour_node)
                    prev_nodes[neighbour_node] = open_node
                    cost = costs[open_node] + 1
                    if neighbour_node not in costs or cost < costs[neighbour_node]:
                        costs[neighbour_node] = cost
            
        # No Path Found
        return []

    def move(self):
        path = self.search()
        if len(path) < 2:
            dy = dx = 0
        else:
            target = path[1]
            dy = target[0] - self.y
            dx = target[1] - self.x
        super().move(dy, dx)
        

class FixedChaser(Chaser):
    def __init__(self, win, height, width, blocks, maze, route):
        super().__init__(win, height, width, blocks, maze, route)
        self.step = 0

    def move(self):
        self.step += 1
        target = self.route[self.step % len(self.route)]
        dy, dx = target[0] - self.y, target[1] - self.x
        super().move(dy, dx)

