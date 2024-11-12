import random
import pygame as py
from sys import exit
import time
import threading


# Game settings

# each cell will occupy a size of 40 pixels
columns = 10
rows = 20
cell_size = 40
# we multiply of cell size by a width of 10 and height of 20 to get
# a game width of 400 pixels and a game height of 800 pixels
game_width, game_height = columns * cell_size, rows * cell_size

# Colors
# we will use the colors to color in our game grid
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREEN = (144, 238, 144)
# Lighter green for border
LIGHTER_GREEN = (173, 255, 173)  
DARK_GREEN = (0, 100, 0) 




# Create the grid (2D array)
# we use a list compression to create a nested list for our game grid
# our game grid will include 20 rows and 10 columns
# we will use a function called draw_grid to draw physical map of our game grid 
# using pygame
# additionally, the design of this game will rely on functions such as move left,
# move down, etc. So our create_grid() will store the grid that all of the functions
# will operate on
#
# create grid is also used to create a temp_grid which is an empty grid used to map
# some of the movements such as move right or left
# this was done to avoid a collision between the pieces, represented by a a nested list
# of '*'
# if we wanted to move the piece * * * * to the right. Each * is moved 1 by 1 to the right
# by n+1 and would thus override the piece infront of it
# thus temp_grid is used to map the piece onto a blank grid and easily map it back to the
# grid being used for the game
def create_grid():
    return [[' ' for _ in range(columns)] for _ in range(rows)]

# Draw the grid and pieces
# draw_grid takes to parameters: display_surface and grid
# display_surface will be used by pygame to draw our game window
# we use grid to dictate which blocks to fill in on our game window
def draw_grid(display_surface, grid, score):
    # we iterate through all of our rows and columns to get the 
    # correct number of boxes for our grid
    for row in range(rows):
        for col in range(columns):

            # https://www.pygame.org/docs/ref/rect.html
            # we use py.Rect() to store our rectangle coordinates
            # Rect(left, top, width, height)
            # for column we start + 20 pixels from the left and store the 
            # coordinates for our column grids
            # we do the same for our rows
            # we thus have the coordinates of each square grid wtih a width
            # of 400 pixels + 20 and a length of 800 pixels + 10
            rect = py.Rect(
                # position of our X axis
                col * cell_size + 20, 
                # position of our Y axis
                row * cell_size + 10,  
                # cell_size contains our pixel size of our box
                # this will be passed as our width and height
                cell_size, cell_size   
            )
            # we get a value that looks like, (row = 0, col = 0)
            # <rect(20,20,40,40)>
            # the first two values will give us the location on our grid starting from the top left
            # the last two values give use the size of every square
            #
            # we get a value that looks like, (row = 0, col = 1)
            # <rect(60,20,40,40)>
            # as we can see the coordinates will constantly change while the square size stays constant
            # 
            # https://www.pygame.org/docs/ref/draw.html#pygame.draw.rect
            # we then call py.draw.rect(surface, color, rect) and pass
            # our display surface, which is where the grid is drawn.
            #  the color, DARK_GREEN, is our pre-defined color stored as a global variable for our grid lines,
            #  which we stored as a global variable.
            # The last agrgument we pass is rect, which contains the coordinates for our grid. 
            # rect takes our grid coordinates that were initialized above.
            # The 1 ensures that our grid is only 1 pixel thick
            py.draw.rect(display_surface, DARK_GREEN, rect, 1)  # Grid lines
            
            # A lot of the function of this game will come from predefined functions
            # pieces will be nested lists defined by '*'. Pieces that have been locked
            # into place from our lock_piece() function will convert those previous pieces
            # to nested lists of '0'
            #
            # This conditional statement is important because it will visiually represent to 
            # the user where the pieces are on the tetris grid
            #
            # if our  grid has '*' or '0' we will call py.draw.rect() again and 
            # pass it our Lighter Green color to display our piece on the display surface
            # '*' represent our pieces in play. '0' represent our pieces that have been 
            # locked and can no longer move.
            #
            # Since this call does not have a pixel boundary, such as the 1 pixel boundary in the above grid,
            #  py.draw.rect will fill the whole box with a green color.
            #  Thus this will be used to show the user the pieces on our grid. 
            #
            if grid[row][col] == '*' or grid[row][col] == '0':
                py.draw.rect(display_surface, LIGHTER_GREEN, rect)
    
    # This section is for our Game Over display
    #https://www.pygame.org/docs/ref/font.html#pygame.font.Font
    # we call py.font.Font(object, size) pass the size of our font
    #
    # https://pygame.readthedocs.io/en/latest/4_text/text.html
    # we then use render to create the text box and color of our text
    font = py.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    # https://www.geeksforgeeks.org/pygame-surface-blit-function/
    # we finally call blit(source, area) on our grid to display our 
    # game over screen which contains our font, text, and color from our
    # variable score_text and the area that was passed to .blit()
    display_surface.blit(score_text, (10, 10))

# Tetris pieces
# Tetris is composed of seven pieces represented by the letters I, O, S, Z, L, J, T
# we define each one of these pieces as a nested list
# we represent the piece as a ' ' or '*' within its nest to define the 'shape' of the piece
# since the nested list alone has no shape, it is up to us to correctly map the 'piece' onto
# our grid. Thus these 'pieces' were created to help us do this
def new_pieces():
    I = [['*'], ['*'], ['*'], ['*']]
    O = [['*','*'], ['*','*']]
    S = [[' ','*','*'], ['*','*',' ']]
    Z = [['*','*'], [' ','*','*']]
    L = [['*',' '], ['*',' '], ['*','*']]
    J = [[' ','*'], [' ','*'], ['*','*']]
    T = [['*','*','*'], [' ','*',' ']]
    return [I, O, S, Z, L, J, T]

# Randomly select a piece
# we wanted a random piece to be generated after every old piece is locked
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html
# we use random.choice() from the random library to achieve this
# choice() takes an array and generates a random sample
# we store all seven of our 'pieces' created in function new_pieces() and store
# them in variable pieces
# we then call random.choice() on our pieces, which are just seven nested lists
# and random will randomly generate one of these seven pieces after each new piece is
# locked and stored as a '0'
import random
def random_piece():
    pieces = new_pieces()
    return random.choice(pieces)

# Map the piece onto the grid
# our map_to_grid function takes four paramaters, two of which are default arguements
# our two default arugments are start_row and start_col and gaurentee that our piece starts
# at position (0,4) on our grid
def map_to_grid(piece, grid, start_row=0, start_col=4):
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            # we iterate through our piece and if we find a '*' and the '*' is within the bounds
            # of our row and column after adjusting for the starting position, then we map that
            # '*' to the starting position plus the i or j location in the row and column of the
            # piece
            if piece[i][j] == '*':
                if start_row + i < len(grid) and start_col + j < len(grid[0]):
                    grid[start_row + i][start_col + j] = '*'
# The key note is that each '*' is iterated through and individually mapped on to our grid one by one
# at our starting grid posiiton of (0,4)
# Thus we have our 'piece', which is simply a collection of '*' mapped on to our grid.
# Recall that by our condition in the draw_grid() function; if the function detects a '*', 
# py.draw.rect() will fill in all of the green box denoting our piece 


# we have many move functions such as move_right, move_left and move_down
# these functions deal with the managmeent of our piece on the grid.
# Everytime we 'move' a piece we have to clear its previous place on the grid 
# defined by '*'
# to do this, clear_piece takes the parameter grid
def clear_piece(grid):
    # we iterate through our entire grid
     for r in range(len(grid)):
        for c in range(len(grid[0])): 
            # if we find a '*' on our grid we replace it with ' '
            if grid[r][c] == '*':
                grid[r][c] = ' '
# thus our piece is cleared from its previous positon

# our move_right function takes two arguments: grid and temp_grid
# we use temp_grid to prevent '*' in our piece from colliding and leading to a disfigured piece on grid.
# Thus when we move right we will map each '*' individually onto the empty temp_grid so we have no collisions.
# We then clear our game grid of any '*' and we then map the piece from our temp_grid back on to our 
# game grid.
def move_right(grid, temp_grid):
    # we set moved to False
    # if no piece is moved right we return False
    # if a piece does move right then we will return True
    moved = False
    # grid_width stores the full length of the column length
    grid_width = len(grid[0])
    
    # Blocking condtions
    # in our loop we iterate over our grid by in the reverse direction starting from right to left
    for r in range(len(grid)):
        for c in range(len(grid[0])-1, -1, -1): 
            # When we detect an '*' in our piece we must check for two conditions before we move it right
            # the first condition is if our piece is outside of the right most parameter of our grid, denoted
            # by grid_width - 1 
            # The second condition is to check if there is a locked piece in our way
            # Since the pieces are moved by individual '*'; we check if there is an individual '0' in our way
            # 
            # recall that our locked pieces are deonated by '0'
            # to check if there is a locked piece in our way we denoted this by grid[r][c+1] == '0'
            # if either of these conditions are met then we CANNOT move our piece right and we
            # return False
            if grid[r][c] == '*' and (c == grid_width - 1 or grid[r][c + 1] == '0'):
                return False  
    
    # In the case when we can move our piece we have to 'clear out temp_grid by iterating through
    # ensuring that each box on the grid is held by an empty space ' ' 
    for r in range(len(temp_grid)):
        for c in range(len(temp_grid[0])):
            temp_grid[r][c] = ' '

    # we then iterate through our game grid starting from the right side
    for r in range(len(grid)):
        for c in range(len(grid[0])-1, -1, -1):
            # we check for the position of '*' in our gam grid to get our piece
            if grid[r][c] == '*':
                # we check to see if there is space to the right of our piece denoted by c+1 
                # we ensure we're still in bounds when its less than our grid_width
                # then check if the space to the right is empty denoted by ' '
                # if it is we move our '*' to the right by 1 in our temp_grid
                # we then change moved to True
                if c + 1 < grid_width:
                    if grid[r][c + 1] == ' ':
                        temp_grid[r][c + 1] = '*'
                        moved = True
                
                    else:
                        # if we cannot right we will keep the '*' in our current temp_grid position
                        temp_grid[r][c] = '*'
                        # this conditional will help in the when we have collisions with other '*'
                        # so our piece doesn't run into itself
                    # [ ' ', ' ', '*', ' ', ' ' ]     [ ' ', ' ', ' ', '*', ' ' ]
                    # [ ' ', '*', '*', ' ', ' ' ] ->  [ ' ', ' ', '*', '*', ' ' ]
                    # [ ' ', ' ', '*', ' ', ' ' ]     [ ' ', ' ', ' ', '*', ' ' ]
                    # recall that we iterate from the right for this loop to reduce the chance for colliding
                    # with its own piece
                else:
                    # this last condition handles for when our piece is at its right most bound
                    temp_grid[r][c] = '*'
                    # [ ' ', ' ', '*' ]     [ ' ', ' ', '*' ]
                    # [ ' ', ' ', '*' ] ->  [ ' ', ' ', '*' ]
                    # [ ' ', ' ', '*' ]     [ ' ', ' ', '*' ]

                # regardless of the conditional  outcome we will clear our grid
                grid[r][c] = ' '

    # once we've ensure that the right space is open and it is not an edge we will map our temp_grid '*'
    # to our game grid with this loop
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if temp_grid[r][c] == '*':
                grid[r][c] = '*'

    # if the piece '*' was able to be move then in our conditional statement above
    # temp_grid would have been updated and moved would have been changed to True
    # so we return moved
    #
    # if we ran into any collisions in our initial loop, such as colliding with the wall or locked piece
    # our function would immediately return False thus not executing the movement
    return moved

# The logic for move left is similar to move right. 
# We define our grid_width as the length of our columns and we set our variable moved to False
def move_left(grid, temp_grid):
    moved = False
    grid_width = len(grid[0])
    
    # We start with checking for the conditions of out of bounds or collision with a locked piece
    # if any of our '*' collide with a locked '0' or go out of bounds we return False and prevent 
    # the left movement from occuring
    for r in range(len(grid)):
        for c in range(len(grid[0])): 
            # our left most bound is when c == 0 and a left psoition collision is
            # defined by grid[r][c-1] == '0'
            # we check see if we're at our left bound or if there is a locked piece
            # in the left position that we intend to move to
            # we return False anytime this case occurs to stop the left mvoement
            if grid[r][c] == '*' and (c == 0 or grid[r][c - 1] == '0'):
                return False  
    
    # We clear our temp_grid so that we don't have any collisions
    for r in range(len(temp_grid)):
        for c in range(len(temp_grid[0])):
            temp_grid[r][c] = ' '

    # we iterate through our grid and look for individual piece components denoted by '*'
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '*':
                # Store in temp if left space is available
                # if c-1 is 0 or greater we are within the bounds of our grid
                # if grid[r][c-1] == ' ' then there is space on our grid to move left
                # so we map to this left position on our temp_grid and change moved to True 
                # so that our function can execute
                if c - 1 >= 0 and grid[r][c - 1] == ' ':
                    temp_grid[r][c - 1] = '*'
                    moved = True            

                # We then clear our original grid of the previous '*' so that they can be place in the 
                # new left position
                grid[r][c] = ' '

    # We finally map the new position from our tem_grid to our game grid
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if temp_grid[r][c] == '*':
                grid[r][c] = '*'

    # we return moved that is now True so that our function executes
    return moved


# we define a move_down function to move our piece down 1 row
def move_down(grid, temp_grid):
    # we set moved to False and should_lock to False to prevent our function from running if
    # its conditions aren't met
    # we define our row and column length by grid_height and grid_width
    moved = False
    grid_height = len(grid)
    grid_width = len(grid[0])
    should_lock = False

    # We iterate through our grid and check to see if we in the last row or if there is a locked 
    # piece below
    for c in range(grid_width):
        for r in range(grid_height):
            if grid[r][c] == '*':
            # the last row is defined by grid_height - 1 
            # a locked peice below is defined by grid[r+1][c]
            # if any of the '*' in our piece meets this condition we change should_lock to True and
            # break out of this loop
                if r == grid_height - 1 or grid[r + 1][c] == '0':
                    should_lock = True
                    break
        if should_lock:
            break

    # we clear our temp grid like we did in move_left and move_right
    for r in range(len(temp_grid)):
        for c in range(len(temp_grid[0])):
            temp_grid[r][c] = ' '

    # We iterate through our grid starting from the bottom
    for c in range(grid_width):
        for r in range(grid_height - 1, -1, -1): 
            if grid[r][c] == '*':
                # if our piece denoted by '*' does not meet our locking condition and
                # is not in our last row denoted by r+1 < grid_height and there is 
                # an empty space below denoted by grid[r+1][c] == ' '
                # then we move the piece down on our temp_grid and change moved to True
                if not should_lock and r + 1 < grid_height and grid[r + 1][c] == ' ':
                    temp_grid[r + 1][c] = '*'
                    moved = True
                else:
                # otherwise we keep the piece in the same position and map it to our temp_grid
                    temp_grid[r][c] = '*'
                # we then clear our grid of the old piece position
                grid[r][c] = ' '

    # Finally, we map the moved down piece from our temp_grid back onto our game grid
    for r in range(grid_height):
        for c in range(grid_width):
            if temp_grid[r][c] == '*':
                grid[r][c] = '*'

    # if the piece should lock we call our lock_pieces function and return False so that
    # our move_down function doesn't execute
    if should_lock:
        lock_pieces(grid)
        return False

    # presuming there is space for our piece to move down, then moved is changed to True and our 
    # move_down function is executed
    return moved








# since our section that we want to rotate is small compared to the big grid
# we need to create a subgrid around our 'piece' to allow for a rotation
# where the pieces do not end in the wrong parts of the grid
def subgrid_bound(grid):
    rows, cols = len(grid), len(grid[0])
    min_row, max_row = rows, 0
    min_col, max_col = cols, 0

    # we iterate through our grid to the boundaries of our subgrid
    # we use the min row, col and max row, col variables to do this
    # the min and max function min(n1,n2..) take any number n and return
    # the highest or lowest number n
    # we thus get our boundary for our subgrid
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '*':
                # min_row is set to the total number of rows
                # r is when this iteration finds a '*' 
                # if r is less than min_row, min_row then becomes r
                # we repeat this until we have the smallest value for row
                # our max_row starts at 0. As we iterate through our row and
                # replace max_row with our greatest r
                #
                # we do this with our columns as well
                min_row = min(min_row, r)
                max_row = max(max_row, r)
                min_col = min(min_col, c)
                max_col = max(max_col, c)

    # we then return all for values
    return min_row, max_row, min_col, max_col

# we want to isolate our subgrid from our game grid
# we pass the arguements grid, min_row, max_row, min_col, max_col
def isolate_subgrid(grid, min_row, max_row, min_col, max_col):

    # we iterator through our min and max boundaries to get our subgrid matrix
    # that we will use to rotate
    subgrid = [row[min_col:max_col+1] for row in grid[min_row:max_row+1]]
    return subgrid




# we then use this subgrid to perform our matrix operations for the rotation
def rotate(subgrid):

    # we create a variable that can hold empty places for our transpose matrix
    transpose = [[0] * len(subgrid) for _ in range(len(subgrid[0]))]

    # we then iterate through our subgrid and switch the cols and rows or switch the x-y axis
    for r in range(len(subgrid)):
        for c in range(len(subgrid[0])):
            transpose[c][r] = subgrid[r][c]
    # We have
    # [' ','*']
    # ['*','*']
    # ['*',' ']
    # We get
    # ['*','*',' ']
    # [' ','*','*']


    # We then reverse our rows in the transposed matrix
    rotated = [row[::-1] for row in transpose]
    # We then get
    # [' ','*','*']
    # ['*','*',' ']
    # thus our piece is rotate 

    return rotated







# we clear our grid then map our rotated subgrid to our main grid
def map_rotate_to_grid(grid, rotated, min_row, min_col):

    # check if rotated is empty or has empty rows then return the unchanged grid
    if not rotated or not rotated[0]: 
        return grid 

    # we get the length of the rows and columns for both the grid and rotated matrix
    grid_rows, grid_cols = len(grid), len(grid[0])
    rotated_rows, rotated_cols = len(rotated), len(rotated[0])
    
    # we need to prevent our rotated piece from going out of bounds
    # we will add the starting point, the min_row and col and add the roated row and col
    # which includes the length of the rotated row or column
    # if either of these are greater we will subtract rotated_rows from our grid
    # and start at the new min_row and min_col so that 
    # our rotated piece does not go out of bounds
    if min_row + rotated_rows > grid_rows:
        min_row = grid_rows - rotated_rows
    
    if min_col + rotated_cols > grid_cols:
        min_col = grid_cols - rotated_cols

    # we clear our previous non rotated piece to allow for the rotation to be mapped to our grid
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '*':
                grid[r][c] = ' '

    for r in range(len(rotated)):
        for c in range(len(rotated[0])):
            # our mapping begins at our min row and colum
            # # we map the length of rotated piece's row and column to our grid
            grid[min_row + r][min_col + c] = rotated[r][c]




def clear_lines(grid):
    # we create a temporary place holder for cleared rows
    new_grid = []
    # we set our cleared rows counter to zero
    lines_cleared = 0
    # we define the length of our row on our grid
    row_length = len(grid[0])

    for row in grid:
        # check to see if the row is filled denoted by '0'
        if all(cell == '0' for cell in row):
            # if the row is filled then increase the lines cleared counter
            lines_cleared += 1
        else:
            # if the row is NOT cleared then we append that row to our new_grid
            new_grid.append(row.copy())

    # Add new empty rows to the top of new_grid to replace the cleared rows
    for _ in range(lines_cleared):
        new_grid.insert(0, [' ' for _ in range(row_length)])

    return new_grid, lines_cleared
    



# we iterate through our grid
# if we encounter a '*' on our grid we change it to a '0', which 
# locks our piece
def lock_pieces(grid):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '*':
                grid[r][c] = '0'


# score increase based on the amount of lines_cleared in one move
def calculate_score(lines_cleared):
    if lines_cleared == 1:
        return 100
    elif lines_cleared == 2:
        return 300
    elif lines_cleared == 3:
        return 500
    elif lines_cleared == 4:
        return 800
    else:
        return 0

# we define our game over condition in this function
def game_over_condition(grid):
    # Check if any cell in the top row contains a locked piece
    return any(cell == '0' for cell in grid[0])

def game_over(display_surface):
    font = py.font.SysFont('Arial', 26)

    game_over_text = font.render('Game Over', True, WHITE)  # White text

    # screen.get_size() gets use the x and y width and length of our screen
    screen_width, screen_height = display_surface.get_size()
    text_width, text_height = game_over_text.get_size()

    # we get the dimensions for our Game Over box
    box_width, box_height = text_width + 20, text_height + 20
    box_x = (screen_width - text_width) // 2
    box_y = (screen_height - text_height) // 2


    py.draw.rect(display_surface, BLACK, (box_x, box_y, box_width, box_height))
    # .blit(source, destination) is used to draw our box over the Tetris game surface
    # it takes a source which is what we want to draw over our Surface
    # and it takes a destination where box_x and box_y contain our coordinates for the 
    # gameover display
    display_surface.blit(game_over_text, (box_x, box_y))

    py.display.flip()



def game_loop():
    py.init()
    #https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
    # display.set_mode() intializes our game window and generate our display surface
    # we pass display.set_mode() our size denated by a pair of numbers our height and width
    # recall that we have a game width of 400 pixels and height of 800 pixels
    # we add 40 pixels of additional space to our height and width
    display_surface = py.display.set_mode((game_width + 40, game_height + 40))
    # https://www.pygame.org/docs/ref/display.html#pygame.display.set_caption
    # display.set_caption() takes our title arguement and returns it in our display
    # window. So we pass it the title of our game, 'Tetris'
    py.display.set_caption('Tetris')

    clock = py.time.Clock()

    # initialize score
    global score
    score = 0


    # we initialize our grid for our playing game
    grid = create_grid()
    # we initialize our temp_grid to manage the pieces of our game
    temp_grid = create_grid()
    # we generate a random piece and store it in variable piece
    piece = random_piece()
    # we then map our piece to game
    map_to_grid(piece, grid)

    kill_game = False

    # we define our auto_move_down function in our game loop that will
    # access our variables and thread functions
    def auto_move_down(delay = 0.4):
        # we access our global variable score so that we can modify it inside of
        # this function
        global score
        # we call the nonlocal kill_game because we want to modify it in this function, 
        # but not affect outside of this function
        nonlocal kill_game
        # when kill_game is True our game will cease and call game over
        # so when we pass while not kill_game; our function will continue to
        # run. 
        while not kill_game:
            # https://www.geeksforgeeks.org/sleep-in-python/
            # the function sleep() in our time library suspends the execution of our
            # function for a set amount of seconds. We need this function to properly
            # pass our function to Thread which is needed to continuously call auto_move_down
            # while all of our other functions are called
            time.sleep(delay)
            # if our conditions for move_down are met we set moved = move_down since
            # move_down will return True
            moved = move_down(grid, temp_grid)
            # However if we can not move down we need to pass a couple of other functions.
            # these functions must account for locking a piece, clearing_lines, scoring,
            # generating random pieces, mapping them to grid and ending the game if the
            # game over conditions are met.
            if not moved:
                # if we cannot move we first lock our piece which involves changing all
                # '*' to '0'
                lock_pieces(grid)
                # we set our function clear_lines equal to our nested list new_grid and
                # lines_cleared, which counts how many lines need to be cleared
                new_grid, lines_cleared = clear_lines(grid)
                # we then update our grid with the grid that has the lines cleared denoted
                # by new_grid
                grid[:] = new_grid
                # we pass lines cleared to our calculate_score function on store the value in
                # score_increase
                score_increase = calculate_score(lines_cleared)
                # we then add value to our score
                score += score_increase
                # we then check our game_over_condition, where there any '0' in row 0
                # and if this condtion is met we set kill_game to True which will terminate
                # our while loop and stop the pieces from moving
                if game_over_condition(grid):
                    kill_game = True
                # however, if the game over condition is not met we will generate a new piece
                # and map it to our grid
                else:
                    piece = random_piece()
                    map_to_grid(piece, grid)
    # https://www.geeksforgeeks.org/multithreading-python-set-1/
    # we use threading to achieve multitasking
    # we use the function Thread(target, args) which takes the target - function
    # to be executed and arguments being passed to the target function
    # as we can see our time delay of 0.4 is passed
    auto_move_thread = threading.Thread(target=lambda: auto_move_down(delay=0.4))    
    auto_move_thread.daemon = True
    
    # we then call start() on our thread to being multithreading so that auto_move_down
    # is always running in our background while the game is still running
    auto_move_thread.start()

    # we create a while loop to handle the functions of our game
    # we want our game to continue to run until we reach our game over condition
    while True:
        # https://www.youtube.com/watch?v=KR2zP6yuWAs
        # https://www.pygame.org/docs/ref/event.html
        # pygame.event.get() will get all of the events and store them as a list
        # our event handler users a for loop to iterate through our event list
        # if the event is one that we need then we catch it with an if statement
        #
        for event in py.event.get():
            # close game
            # if the user presses quit on our game window this will exit our window
            # and close our game
            # we uses even.type to look for the event py.QUIT to close our game
            if event.type == py.QUIT:
                py.quit()
                exit()
            # Move piece and run if game over condition NOT met denoted
            # by  kill_game
            # this is our outter elif statement since while our game is running
            # it needs to accept events Left key, Right key, Down key, and Space key
            # to allow our pieces to move and rotate
            # we achieve this with py.KEYDOWN denoted the keys that will be pressed down 
            # to trigger our function
            elif event.type == py.KEYDOWN and not kill_game:
                # we start will our Right Key event to move our piece right
                # if this event is called we simply call our move_right() function
                # recall that our move_right function() handles the out of
                # bounds and collision cases
                if event.key == py.K_RIGHT:  
                    move_right(grid, temp_grid)
                # we set the condition for our left key event and pass
                # our move left function
                elif event.key == py.K_LEFT: 
                    move_left(grid, temp_grid)
                # our condition for move down takes many functions
                # consider that when we reach the bottom of our tetris grid
                # we cannot move down anymore so we will need to lock our piece
                # and map the new piece to the grid so we can continue to uses
                # move down also hands our clear lines, scoring and come over conditions
                elif event.key == py.K_DOWN:
                    # if our piece cannot move down we must:
                    # 1. lock our piece
                    # 2. clear our row if possible (the if conditon is built
                    # into clear_lines() to check if the conditions are met)
                    #   - update our grid with new rows if we cleared a row
                    #   - calculate our score increase if we cleared a row
                    #   - and finally increase our score
                    #
                    # we then check to see if our game over condition is met
                    # if it is not we genderate a new piece and map it to our
                    # grid
                    if not move_down(grid, temp_grid):
                        # lock piece
                        lock_pieces(grid)
                        # clear line if row filled
                        new_grid, lines_cleared = clear_lines(grid)
                        # generate our new grid with the cleared row gone
                        grid[:] = new_grid
                        # calculate our score
                        score_increase = calculate_score(lines_cleared)
                        # increase our score
                        score += score_increase

                        # check game over condition
                        if game_over_condition(grid):
                            # we change kill_game to kill to stop all of the events under our 
                            # left key, right key, down key, and space key event
                            # recall that the elif condition containing all of these events is
                            # elif event.type == py.KEYDOWN and not kill_game:
                            # so once kill_game is True then all of these events stop and we
                            # call our game over display further down in this code
                            kill_game = True
                        else:
                            # if our game over condition isn't met; since we have locked
                            # our piece in the above event call and check the other conditions
                            # it is time to generate a new piece and map it to the grid
                            piece = random_piece() 
                            map_to_grid(piece, grid)
                # our space key handles the rotate peiece event
                elif event.key == py.K_SPACE: 
                    # when we call rotate we must call our subgrid_bound()function to
                    # get the min and max row and column matrix values
                    min_row, max_row, min_col, max_col = subgrid_bound(grid)
                    # we then isolate our subgrid and store it in a variable subgrid
                    # so we have
                    # [' ',' ',' ',' ',' ',' ']
                    # [' ',' ',' ',['*','*'],' ']
                    # [' ',' ',['*','*'],' ',' ']
                    # [' ',' ',' ',' ',' ',' ']
                    # [' ',' ',' ',' ',' ',' ']
                    # the subgrid within our game grid
                    subgrid = isolate_subgrid(grid, min_row, max_row, min_col, max_col)
                    # we then pass our subgrid to the rotate() fundtion in store in 
                    # in variable rotate
                    rotated = rotate(subgrid)
                    # then clear the non rotated piece from our grid
                    clear_piece(grid) 
                    # last we map our rotated piece to our grid using
                    # our map_rotate_to_grid() function 
                    map_rotate_to_grid(grid, rotated, min_row, min_col)
        
        # Fill background
        display_surface.fill(BLACK)

        # Draw grid with pieces
        draw_grid(display_surface, grid, score)
        
        # if our game over condition is met all key board and auto move down
        # events will end and we will display our game over surface
        if kill_game:
            game_over(display_surface)


        # Update display
        py.display.update()

        # Cap the frame rate
        clock.tick(60)

if __name__ == '__main__':
    game_loop()