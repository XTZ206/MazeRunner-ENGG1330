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
        ny = self.y + dy
        nx = self.x + dx
        
        if self.maze.check_route(ny, nx):
            self.y, self.x = ny, nx
            return True
        
        else:
            return False


class Maze(Sprite):
    def __init__(self, win, height, width, blocks, start, end):
        super().__init__(win, height, width, blocks)
        self.start = start
        self.end = end

    def get_start(self, name):
        return self.start[name]
    
    def get_end(self):
        return self.end

    def check_inrange(self, y, x):
        return 0 <= y < self.height and 0 <= x < self.width

    def check_solid(self, y, x):
        index = y * self.width + x
        return self.blocks[index].is_solid
    
    def check_route(self, y, x):
        return self.check_inrange(y, x) and not self.check_solid(y, x)
    
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
        self.y, self.x = maze.get_start("player")
        self.maze = maze   

    def check_win(self):
        return (self.y, self.x) == self.maze.get_end()
    
    def check_lose(self, chasers):
        for chaser in chasers:
            if (chaser.y, chaser.x) == (self.y, self.x):
                return True
        return False
            
    
    def draw(self):
        block = self.blocks[0]
        block.draw(self.win, self.y, self.x)


class Chaser(MovableSprite):
    def __init__(self, win, height, width, blocks, maze):
        super().__init__(win, height, width, blocks)
        self.maze = maze
    
    def draw(self):
        block = self.blocks[0]
        block.draw(self.win, self.y, self.x)


class AutoChaser(Chaser):
    def __init__(self, win, height, width, blocks, maze, player):
        super().__init__(win, height, width, blocks, maze)
        self.y, self.x = maze.get_start("auto_chaser")
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
    def __init__(self, win, height, width, blocks, maze, index):
        super().__init__(win, height, width, blocks, maze)
        self.y, self.x = maze.get_start(f"fixed_chaser_{index}")
        self.route = maze.get_fixed_route(index)
        self.step = 0

    def move(self):
        # TODO: Complete the Move Method of FixedChaser
        pass



class FixedChaserStraight(MovableSprite):
    def __init__(self,win,height,width,blocks,maze,player):
        super().__init__(win, height, width, blocks)
        self.y, self.x = self.starty,self.startx = maze.get_start("fixed_chaser_start")
        self.endy, self.endx = maze.get_start("fixed_chaser_end")
        self.maze=maze
        self.player=player
        self.pastpath=[]        

    #using pastpath to check where the chaser come from (start or end)
    def check_direction(self):
        if self.pastpath[0]==(self.starty, self.startx):
            return True
        elif self.pastpath[0]==(self.endy, self.endx):
            return False
        return True
    #determine the move direction
    def check_step(self,dirction):
        available_steps=((1,0),(0,1),(-1,0),(0,-1))
        if direction:
            if self.endy-self.y>0 and self.endx-self.x==0:
                return available_steps[0]
            elif self.endy-self.y<0 and self.endx-self.x==0:
                return available_steps[2]
            elif self.endy-self.y==0 and self.endx-self.x>0:
                return available_steps[1]
            elif self.endy-self.y==0 and self.endx-self.x<0:
                return available_steps[3]
            
        else:
            if self.starty -self.y>0 and self.startx-self.x==0:
                return available_steps[0]
            elif self.starty-self.y<0 and self.startx-self.x==0:
                return available_steps[2]
            elif self.starty-self.y==0 and self.startx-self.x>0:
                return available_steps[1]
            elif self.starty-self.y==0 and self.startx-self.x<0:
                return available_steps[3]
        
        return(0,0)
    
    def move(self):
        self.pastpath.append((self.y,self.x))
        direction=check_direction()
        dy, dx = check_step(direction)
        super().move(dy,dx)
        if (self.y, self.x) in ((self.starty,self.startx),(self.endy,self.endx)):
            self.pastpath =[]#refresh the pastpath to record the latest initial point(start or end)
    
    def draw(self):
        block = self.blocks[0]
        block.draw(self.win,self.y,self.x)
    def check_lose(self):
        return (self.y,self.x) == (self.player.y,self.player.x)



