"""


This is a simple snake game .
Author : userAnonymous
GitHub : https://github.com/ramimk0bir
## Author

* **userAnonymous**
* GitHub: [ramimK0bir](https://github.com/ramimk0bir)

---


## Usage



You can import and run the game from Python code:

```python
import python_snake_game as snake_game

snake_game.play()

```

---

## Parameters of `play` function

| Parameter              | Type            | Default | Description                                                   |
| -----------------------| --------------- | ------- | --------------------------------------------------------------|
| `speed`                | int             | 10      | Controls the game speed (higher = faster)(1-20).              |
| `snake_food_emoji`     | str             | "🍎"    | Emoji to represent the food on the grid.                      |
| `grid_size`            | tuple (int,int) | (15,12) | Size of the game grid as (width, height).                     |
| `background_emoji`     | str             | "🟫"    | Emoji or character to represent the grid blocks.              |
| `invisible_wall`       | bool            | False   | Allow snake to pass through walls and appear on the other side. |
|And many more you can explore after using this |

---"""
__version__ = "1.0.6"
__author__ = "ramimK0bir"
__email__ = "kobirbiddut81@gmail.com"
__license__ = "MIT"
__description__ = "A simple Snake game written in Python for the command-line interface (CLI). Control the snake with arrow keys, eat food to grow, and avoid running into yourself. Built entirely with Python's standard libraries-no third-party packages required."
__url__ = "https://github.com/ramimK0bir/python-snake-game.git@v1.0.6"


import random 
import time 
from .utilities import   handle_keyboard  , custom_print
import sys
import asyncio
import os

def clear_terminal():

    os.system('cls' if os.name == 'nt' else 'clear')
def get_scorebar(score, length):
    GREEN = "\033[92m"
    RESET = "\033[0m"
    if length < 5:
        length = 5

    return f"""{GREEN}{"".join("-" for x in range(2*length))}
|{f"score:{score}".center(2*length-2)}|
{"".join("-" for x in range(2*length))}{RESET}"""

def get_gameovere_bar(score, length):
    RED = "\033[91m"
    RESET = "\033[0m"
    clear_terminal()

    if length < 5:
        length = 5
    
    print(f"""{RED}{"".join("-" for x in range(2*length))}
|{"Game Over".center(2*length-1)}|
|{f"score:{score}".center(2*length-1)}|
{"".join("-" for x in range(2*length))}{RESET}""")


def get_text_from_charmap_only(char_map):

    xs = [x for (x, y) in char_map]
    ys = [y for (x, y) in char_map]

    max_x = max(xs)
    max_y = max(ys)

    result = ""
    for y in range(max_y + 1):
        row_str = ""
        for x in range(max_x + 1):
            row_str += char_map[(x, y)]  # assumes all cells filled
        result += row_str + "\n"
    return result

class SnakeGame :
    def __init__ (self,snake_food_emoji = "🍎",speed :int =10
        , snake_head_emoji :str ="" , background_emoji  :str =""  
        ,invisible_wall :bool =False ,grid_size :tuple[int, int] = (10,10) 
        ,snake_body_emoji ="🟩",poison_mode : bool= False
    ) :
        clear_terminal()
        self.poison_mode=poison_mode
        self.snake_body_emoji=snake_body_emoji
        self.snake_head_emoji=snake_head_emoji
        self.background_emoji=background_emoji
        self.snake_food_emoji=snake_food_emoji
        self.poison_point=0
        self.invisible_wall=invisible_wall
        self.grid_size=grid_size
        self.board=[  ( i,x)   for i in range(grid_size[0]) for x in range(grid_size[1])   ] 
        self.__score=0
        self.speed=speed
        self.game_over=False
        self.pressed_key=-5
        self.second_last_pressed_key=-5
        self.snake_body=[(0,0)]
        self.game_paused=False
        self.food=-1
        self.last_keys=[]
    async def mainloop (self):
        while (not self.game_over) :
            try :
                if not self.game_paused :
                    
                    if (
                        self.pressed_key==-1 or \
                        ( self.pressed_key==-5 and \
                            self.second_last_pressed_key==-5    ) 
                    ):

                        pass
                    else :
                        self.second_last_pressed_key = self.pressed_key
                        try :
                            if self.pressed_key != self.last_keys[0] and abs(self.pressed_key-self.last_keys[0])!=2 and \
                                self.pressed_key in [0,1,2,3] :
            
                                self.last_keys.insert(0, self.pressed_key)

                        except :
                            self.last_keys.insert(0,self.pressed_key) 
                    
                    if len(self.last_keys)>2 :
                        self.last_keys.pop()
                    if len(self.last_keys)==1 :
                        if self.last_keys[0]==3 :
                            for index, item in enumerate (self.snake_body ):
                                if index==0 :
                                    head=self.snake_body[0]
                                    self.snake_body[index]=(item[0]+1, item[1])
                                    self.snake_body.insert(1,head)
                                    self.snake_body.pop()

                        elif self.last_keys[0]==2 :
                            for index, item in enumerate (self.snake_body ):
                                if index==0 :
                                    head=self.snake_body[0]
                                    self.snake_body[index]=(item[0], item[1]+1)
                                    self.snake_body.insert(1, head)
                                    self.snake_body.pop()
                        elif self.last_keys[0] in [0,1] and self.invisible_wall==False  :
                            self.game_over=True

                        elif self.last_keys[0]==0 :
                            for index, item in enumerate (self.snake_body ):
                                if index==0 :
                                    head=self.snake_body[0]
                                    self.snake_body[index]=(item[0], item[1]-1)
                                    self.snake_body.insert(1, head)
                                    self.snake_body.pop()
                        elif self.last_keys[0]==1 :
                            for index, item in enumerate (self.snake_body ):
                                if index==0 :
                                    head=self.snake_body[0]
                                    self.snake_body[index]=(item[0]-1, item[1])
                                    self.snake_body.insert(1, head)
                                    self.snake_body.pop()

                    elif len(self.last_keys) > 1 :
                        head=self.snake_body[0]
                        if self.last_keys.count(self.last_keys[0]) >1 :
                            pass


                        elif self.last_keys[0] == 3  :
                            
                            self.snake_body[0]=(head[0]+1, head[1])
                            self.snake_body.insert(1, head)
                            self.snake_body.pop()
                        elif self.last_keys[0]==0 :
                            self.snake_body[0]=(head[0], head[1]-1)
                            self.snake_body.insert(1, head)
                            self.snake_body.pop()      
                        elif self.last_keys[0] == 1 :
                            self.snake_body[0]=(head[0]-1, head[1])
                            self.snake_body.insert(1, head)
                            self.snake_body.pop()
                        elif self.last_keys[0] == 2 :
                            self.snake_body[0]=(head[0], head[1]+1)
                            self.snake_body.insert(1, head)
                            self.snake_body.pop()  
                        

                    if len(set(self.snake_body)) < len(self.snake_body) :
                        self.game_over=True

                    if  self.food ==-1 :
                        self.food=random.choice(self.board)

                    elif self.food ==self.snake_body[0] :
                        self.__score+=1
                        
                        self.food=random.choice(self.board)
                        self.snake_body.append(self.snake_body[-1])
                        if self.poison_mode :
                            empty_space =[]
                            for item in self.board :
                                if item not in self.snake_body or item !=self.food :
                                    empty_space.append(item)
                            self.poison_point=0
                            if len(empty_space)  > 1 :
                                self.poison_point=random.choice(empty_space)

                    if  not self.invisible_wall  :
                        if  any( x not in self.board  for x in  self.snake_body     ) :
                            self.game_over=True

                    else :
                        for index ,item in enumerate( self.snake_body ):
                            if item in self.board :
                                pass
                            else :
                                x,y=item
                                if x==-1 :
                                    x=self.grid_size[0]-1
                                elif x==self.grid_size[0] :
                                    x=0
                                elif y==-1 :
                                    y=self.grid_size[1]-1
                                elif y==self.grid_size[1] :
                                    y=0
                                self.snake_body[index]=(x,y)

                                if self.snake_body[0]==self.food :
                                    self.__score+=1
                                    self.food=random.choice(self.board)
                                    self.snake_body.append(self.snake_body[-1])
                                    if self.poison_mode :
                                        empty_space =[]
                                        for item in self.board :
                                            if item not in self.snake_body or item !=self.food :
                                                empty_space.append(item)
                                        self.poison_point=0
                                        if len(empty_space)  > 1 :
                                            self.poison_point=random.choice(empty_space)
                    if self.poison_mode :
                        if self.poison_point !=0 :
                            if self.snake_body[0]==self.poison_point :
                                self.game_over=True


                    char_map = {
                        i : self.background_emoji for i in self.board 
                    }

                    for index,item in enumerate(self.snake_body) :
                        if index==0 :
                            char_map[item]=self.snake_head_emoji
                        else :
                            char_map[item]=self.snake_body_emoji

                    if self.food not in self.snake_body :
                        char_map[self.food]=self.snake_food_emoji
                    else :
                        char_map[self.food] = "❌"
                    if self.poison_mode and self.poison_point :
                        char_map[self.poison_point]= "🟥"
                    if self.game_over :
                        get_gameovere_bar(self.__score,self.grid_size[0])
                        break
                    text = get_text_from_charmap_only( char_map) 
                    lines = text.count("\n") + 4
                    print(get_scorebar(self.__score,self.grid_size[0]))
                    print(text)

                    time.sleep((1 / self.speed if self.speed > 0 else 0.5)-0.02)

                    print("\033[F" * lines, end="")
                await asyncio.sleep(.02)
            except KeyboardInterrupt :
                break



    async def keyboard_handling (self): 
        if  sys.platform.startswith('win'):
            while (not self.game_over) :
                try :
                    self.pressed_key= handle_keyboard()
                    if self.pressed_key ==4 :
                        self.game_paused=not self.game_paused
                    elif self.pressed_key==5 :
                        self.game_over=True
                        print("Game closed by user.")
                        break
                except KeyboardInterrupt :
                    self.game_over=True
                    get_gameovere_bar(self.__score,self.grid_size[0])
                    break

                await asyncio.sleep(0.1)
        elif sys.platform.startswith('linux'):
            import select
            import tty
            import termios

            def isData():
                return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

            old_settings = termios.tcgetattr(sys.stdin)

            try:
                tty.setcbreak(sys.stdin.fileno())

                while (not self.game_over):
                    if isData():
                        c = sys.stdin.read(1)
                        if c == '\x1b':  # start of escape sequence
                            c += sys.stdin.read(2)
                        if self.game_paused :
                            pass
                        elif c in [ "[B" ,"s" ]:
                            self.pressed_key=2
                        elif c in ["[A", "w"] :
                            self.pressed_key=0
                        elif c in ["[D", "a"] :
                            self.pressed_key=1
                        elif c in ["[C", "d"] :
                            self.pressed_key=3
                        if c == '\x1b':  # ESC alone to break
                            break
                        if c==" " :
                            self.game_paused=not self.game_paused
                    await asyncio.sleep(0.1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


    async def async_run (self) :
            await asyncio.gather(self.keyboard_handling(), self.mainloop())

    def run(self):
        try :
            asyncio.run(self.async_run())
        except KeyboardInterrupt :
            print("Game closed by user.")

def play (speed = 10 ,snake_food_emoji = "🍎", snake_head_emoji = "🐸",snake_body_emoji="🟩",  background_emoji = "🟫" ,invisible_wall =False, grid_size=(15,12),poison_mode=False) :
    guide = "Use help(python_snake_game) for more info."

    if str(grid_size).isnumeric() :
        print(f"Grid_size must be tuple of 2 integer (width,heigh).\n{guide}")
        return
    if len(grid_size) != 2 :
        print(f"Grid_size must be tuple of 2 integer (width,heigh).\n{guide}")
        return
    if 0 in grid_size :
        print(f"Grid's height or width can't be 0 .\n{guide}")
        return 
    if len(snake_body_emoji) !=1 :
        print(f"Length of snake_body_emoji must be exactly one character long.\n{guide}")
        return
    
    if len(snake_food_emoji) !=1 :
        print(f"Length of snake_food_emoji must be exactly one character long.\n{guide}")
        return
    
    if len(background_emoji) !=1 :
        print(f"Length of background_emoji must be exactly one character long.\n{guide}")
        return
    
    if len(snake_head_emoji) !=1 :
        print(f"Length of snake_head_emoji must be exactly one character long.\n{guide}")
        return
    if speed < 1 or speed >20 : 
        print(f"Range of speed is 1 to 20\n{guide}")
        return
    
    grid_size=(abs(grid_size[0]),abs(grid_size[1]))

    snake_game=SnakeGame(speed=speed ,snake_food_emoji=snake_food_emoji
        ,background_emoji=background_emoji ,grid_size= grid_size,invisible_wall=invisible_wall
        ,snake_head_emoji=snake_head_emoji,snake_body_emoji=snake_body_emoji
        ,poison_mode=poison_mode    
    )
    snake_game.run()

if __name__== "__main__" :
    play(grid_size=(15,12),speed=5)