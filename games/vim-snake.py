import curses
import json
import os
import random
import time


# An implementation of snake with vim movement keys.
# This this could potentially help a beginner with vim
# to learn movement keys.

# Controls:
#	h - Left
#	j - Down
#	k - Up
#	l - Right


source_path = os.path.abspath(os.path.dirname(__file__))

DIRECTIONS = [
	[-1, 0],
	[1, 0],
	[0, -1],
	[0, 1]
]

snake = []

def scoreboard(screen, score):
	"""Show the scoreboard menu.
	Scores are loaded in from 'scores.json'
	if the file does not exist, a default scoreboard will be used.
	If the user scored greater than or equal to another user,
	then new score is inserted first.
	Only the first 5 entries will be written back to the json file."""
	
	fn = os.path.join(source_path, "snake_scores.json")

	# If the scores file exists, load it into memory.
	if os.path.exists(fn):
		with open(fn, "rb") as f:
			data = json.load(f)

	# Otherwise use the default score table.
	else:
		data = [
				{"name": "Jebby", "score": 20},
				{"name": "Billy", "score": 15},
				{"name": "Timmy", "score": 8},
				{"name": "Todd", "score": 5},
				{"name": "Joey", "score": 4}
		]
	
	# Make sure the scoreboard is sorted by score.
	data = list(sorted(data, key=lambda x: x["score"], reverse=True))

	user = None

	for idx, d in enumerate(data):

		# If the user's score is greater or equal
		# to the current entry's score, set the user's entry
		# to that index.
		if score >= d["score"]:
			data.insert(idx, {"name": "", "score": score})
			user = data[idx]
			curses.curs_set(1)
			break
	
	data = data[:5]

	finished = False

	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

	lower = "abcdefghijklmnopqrstuvwxyz"
	symbols = "1234567890!@#$%^&*()_+;:'\\|{}[],.<>/?-="
	valid_chars = lower + lower.upper() + symbols + " "

	# While the user hasn't finished input.
	while not finished:
		h, w = screen.getmaxyx()
		mh = h // 2
		mw = w // 2
		screen.erase()

		# Draw each entry and their score.
		for idx, entry in enumerate(data):
			if entry is user:
				screen.attron(curses.color_pair(3))
			screen.addstr(mh-(5-idx), mw//2, entry["name"])
			screen.addstr(mh-(5-idx), mw + 30, str(entry["score"]))
			screen.attroff(curses.color_pair(3))

		if user is not None:
			status = "You got a high score."
		else:
			status = "You didn't get a high score. Press Enter to continue."

		if user:
			screen.attron(curses.color_pair(3))
		screen.addstr(mh-9, mw//2, status)
		screen.attroff(curses.color_pair(3))

		ch = screen.getch()


		# If the user pressed enter.
		if ch in [10, 13]:
			if user is None:
				finished = True
			else:
				if user["name"]:
					finished = True

		# If the user pressed backspace, remove a character
		elif chr(ch) == u"\u007f":
			if len(user["name"]):
				user["name"] = user["name"][:-1]

		# Otherwise append the character to the name
		# and trim the name to 10 characters.
		elif user is not None:
			if chr(ch) in valid_chars:
				user["name"] = user["name"] + chr(ch)
				user["name"] = user["name"][:10]

		screen.refresh()

	# Write the new scores to the file.
	with open(fn, "w") as f:
		json.dump(data, f)
	
def add_new_fruit(screen):
	x = 0
	y = 0
	h, w = screen.getmaxyx()

	while True:
		x = random.randint(5, (w-1)-5)
		y = random.randint(5, (h-1)-5)
		fruit = [y, x]
		if fruit in snake:
			continue
		break
	return fruit

def main(screen):
	"""The main loop for the game."""
	
	running = True

	# Hide the cursor.
	curses.curs_set(0)

	# Set up colors.
	# 1 is red for apples.
	# 2 is green for sections of the snake.
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)

	screen.nodelay(True)
	h, w = screen.getmaxyx()

	snake = []

	# Add the initial sections to the snake.
	for i in range(4):
		snake.append([h//2, (w//2)-i])

	# Set the snake's direction to right.
	direction = 3

	fruit = add_new_fruit(screen)

	while running:
		h, w = screen.getmaxyx()

		ch = screen.getch()
		try:
			if chr(ch) in "kjhl":
				direction = "kjhl".index(chr(ch))
		except:
			pass

		time.sleep(.1)
		
		screen.erase()
		d = DIRECTIONS[direction]

		head = snake[0]

		# If the snake's head is colliding with the fruit
		# insert the fruit's position at the beginning of
		# the snake, making the fruit the new head.
		# Then generate a new fruit
		if head == fruit:
			snake.insert(0, fruit)
			fruit = add_new_fruit(screen)

		head = snake[0]

		# Add the direction to the snake's head
		# to the the new position.
		ny = head[0] + d[0]
		nx = head[1] + d[1]
		new_head = [ny, nx]

		# Move the snake's head to the new position
		# and remove the tail. This gives the snake it's movement.
		snake.insert(0, new_head)
		snake.pop(-1)


		# Set the color to green
		screen.attron(curses.color_pair(2))

		# For each section of the snake
		for section in snake[1:]:

			# If the head is in the current section
			# or the section's position is out of bounds
			# the game is over.
			if new_head == section:
				running = False

			y, x = section
			if y < 0 or y > (h-1):
				running = False
			if x < 0 or x > (w-1):
				running = False

			# Draw the section of the snake.
			screen.addstr(y, x, " ")

		# Turn green color off.
		screen.attroff(curses.color_pair(2))

		# Set color to red and draw the fruit.
		screen.attron(curses.color_pair(1))
		screen.addstr(*fruit, " ")
		screen.attroff(curses.color_pair(1))

		# Draw the score in the top right corner.
		screen.addstr(2, w-4, str(len(snake)))

		# If the game is over, break fro the loop.
		if not running:
			break
		
		screen.refresh()

	
	# Show the game over message in the center of the screen.
	screen.addstr(h//2, w//2, "Game Over.")

	# Turn off nonblocking input and wait for user to press a key.
	screen.nodelay(False)
	screen.getch()

	# Show the scoreboard screen.
	scoreboard(screen, len(snake))

if __name__ == "__main__":
	curses.wrapper(main)
