# How to run this code? 
# Open two terminals
# In the first terminal run "python server.py" (Do not close this terminal)
# In the second terminal run "python client.py" (You will play the game in this terminal by using commands)

# This is a Text-Based Adventure Game
# You (the player) will navigate through a story, interact with monsters, move between rooms, and explore this world.
# The story has both a good and a bad ending.
# The outcome of the story depends on the number of friends you make; the player can either lose or win based on the decisions they make during the adventure.
# The player can quit the game at any time or keep playing to achieve the desired ending.

import socket
import threading
import random
# Added for extra credit
import logging 

# Citation for the following function:
# Date: 12/7/2023
# Adapted from
# Source URL: https://www.youtube.com/playlist?list=PLJPiff845eg8hBMJNo6Y2Yo7LKAB8oedh
class Monster:
    def __init__(self, name, description, is_hostile):
        self.name = name
        self.description = description
        self.is_hostile = is_hostile

    def __str__(self):
        return f"{self.name}, {self.description}"

class Room:
    def __init__(self, description):
        self.description = description
        self.connections = {}
        self.monsters = []

    def connect(self, direction, room):
        self.connections[direction] = room

    def add_monster(self, monster):
        self.monsters.append(monster)

    def remove_monster(self, monster):
        self.monsters.remove(monster)

    def get_monster_by_name(self, monster_name):
        for monster in self.monsters:
            if monster.name.lower() == monster_name.lower():
                return monster
        return None           

class Dungeon:
    def __init__(self):
        self.rooms = {}
        self.room_descriptions = [
            "You find yourself in a room filled with computer servers, all blinking and whirring.",
            "This room is eerily quiet, with a single dim light flickering overhead.",
            "You've entered what appears to be a robotics workshop, tools and parts scattered about.",
            "The room is a small, cramped corridor with pipes running along the ceiling, leaking steam.",
            "It looks like a storage room, stacks of metal crates reach the ceiling.",
            "You've stumbled upon what looks like a break area, but there's no one around.",
            "The walls here are lined with large windows showing the vast expanse of space outside.",
            "You enter a control room, with numerous switches and screens, most of which are inactive.",
            "This seems to be a greenhouse, with an array of exotic plants under artificial lights.",
            "The room contains a large, inactive teleportation device, humming with latent energy."
        ]
        self.create_dungeon()

    def process_command(self, player, command):
        parts = command.split()
        if parts[0] in ["go", "north", "south", "east", "west", "n", "s", "e", "w"]:      # Go [direction] command
            return self.handle_movement(player, parts)
        elif parts[0] in ["look", "l"]:
            return player.location.description      # Look command
        elif parts[0] == "fight":
            monster_name = ' '.join(parts[1:]) if len(parts) > 1 else None  # Fight command
            return self.handle_fight(player, monster_name)
        elif parts[0] == "talk":
            monster_name = ' '.join(parts[1:]) if len(parts) > 1 else None # Talk command
            return self.handle_talk(player, monster_name)
        elif parts[0] == "status":
            return player.get_status()  # Status command
        else:
            return "Unknown command."

    def handle_fight(self, player, monster_name):
        # If no specific monster name is given, choose a random monster in the room
        monster = random.choice(player.location.monsters) if not monster_name else player.location.get_monster_by_name(monster_name)

        if monster:
            if monster.is_hostile:
                if monster.name.lower() == "goblin":
                    player.friends += 1
                    message = "You bravely engage the Goblin in combat, gaining respect from others."
                else:
                    message = f"You engage the {monster.name} in combat!"
            else:
                if monster.name.lower() == "robot":
                    player.friends -= 1
                    message = "Fighting the Robot loses you a friend."
                else:
                    message = f"The {monster.name} does not seem to want to fight you."

            # Check for losing condition
            if player.friends <= -3:
                return "Bad ending achieved. You have made too many enemies. You can either quit or continue playing."
            # Check for winning condition
            elif player.friends >= 3:
                return "Good ending achieved. You have made so many friends along the way that now they have joined you in building a society. You can either quit or continue playing."
            else:
                return message            
        else:
            return "No such monster here."

    def handle_talk(self, player, monster_name):
        # If no specific monster name is given, choose a random monster in the room
        monster = random.choice(player.location.monsters) if not monster_name else player.location.get_monster_by_name(monster_name)

        if monster:
            if monster.name.lower() == "robot":
                player.friends += 1
                message = "The robot beeps happily, and you feel a bond forming."
            elif monster.name.lower() == "goblin":
                player.friends -= 1
                message = "The goblin grunts and turns away, clearly uninterested in friendship."
            else:
                message = f"You try to talk to the {monster.name}. {monster.description}"

            # Check for losing condition
            if player.friends <= -3:
                return "Bad ending achieved. You have made too many enemies. You can either quit or continue playing."
            # Check for winning condition
            elif player.friends >= 3:
                return "Good ending achieved. You have made so many friends along the way that now they have joined you in building a society. You can either quit or continue playing."
            else:
                return message
        else:
            return "No such monster here."


    def handle_movement(self, player, parts):
        # This method handles movement
        if len(parts) == 1:
            direction = parts[0]
        else:
            direction = parts[1]

        return self.move_player(player, direction)

    def move_player(self, player, direction):
        current_room = player.location
        if direction not in current_room.connections:
            # If there's no room in the direction, create a new one
            new_room_description = random.choice(self.room_descriptions)
            new_room = Room(new_room_description)
            self.populate_monsters(new_room)  # Add monsters to the new room
            current_room.connect(direction, new_room)  # Connect new room to current one
            new_room.connect("back", current_room)  # Allow the player to go back
            self.rooms[f"room{len(self.rooms) + 1}"] = new_room

        new_room = current_room.connections[direction]
        player.location = new_room
        encounter_message = self.encounter_monster(new_room)
        return f"You move {direction}.\n{new_room.description}\n{encounter_message}"


    def populate_monsters(self, room):
        goblin = Monster("Goblin", "A small, green-skinned creature", True)
        robot = Monster("Robot", "A friendly looking robot", False)
        if random.random() < 0.9:  # 90% chance to find a monster
            room.add_monster(random.choice([goblin, robot]))

    def create_dungeon(self):
        # Create rooms and define connections
        room1 = Room("You find yourself in a sleek, metallic chamber with glowing panels on the walls. "
                    "Wires and pipes run across the ceiling.")
        room2 = Room("This room looks like a high-tech laboratory, filled with strange gadgets and "
                    "flickering holographic displays.")
        room3 = Room("You enter a vast, dimly lit hangar. You can see rows of dormant robots and "
                    "vehicles, covered in dust.")

        # Connect rooms
        room1.connect("north", room2)
        room2.connect("south", room1)
        room2.connect("east", room3)
        room3.connect("west", room2)

        # Add rooms to the dungeon
        self.rooms['room1'] = room1
        self.rooms['room2'] = room2
        self.rooms['room3'] = room3

        # Create monsters
        goblin = Monster("Goblin", "A small, green-skinned creature", True)
        robot = Monster("Robot", "A friendly looking robot", False)

        # Add monsters to rooms
        room1.add_monster(goblin)
        room2.add_monster(robot)

    def get_room(self, room_name):
        return self.rooms.get(room_name)
    
    def encounter_monster(self, room):
        if room.monsters:
            monster = random.choice(room.monsters)
            return f"You encounter a {monster.name}! {monster.description}"
        return "The room is quiet... too quiet."

class Player:
    def __init__(self, start_location):
        self.location = start_location
        self.friends = 0  # Track the number of friends the player has

    def get_status(self):
        return f"Current friends count: {self.friends}" 

# Previous Code without improvement for extra credit
# def handle_client(conn, addr, dungeon):
#     introduction = ("You are a normal student walking on campus. In front of you, a little robot is delivering food. "
#                     "The robot gets stuck on the sidewalk, and you decide to help it. "
#                     "Suddenly, you get hit by a car and die! "
#                     "When you open your eyes, you find yourself transformed into a small food delivery robot. Your adventure begins!\n\n"
#                     "Available commands:\n"
#                     "go [direction] - Move in a direction (north, south, east, west)\n"
#                     "look - Get a description of your current location\n"
#                     "fight [monster] - Engage in combat with a monster\n"
#                     "talk [monster] - Attempt to talk to a monster\n"
#                     "status - See your current friends count\n"
#                     "quit or exit - Exit game\n")

#     print(f"New connection from {addr}") # This is part of handling a new connection
#     # 3. When connected, the server calls recv to receive data
#     # 4. The server prints the data, then prompts for a reply
#     # 5. The server sends the reply
#     # 6. Back to step 3
#     conn.sendall(introduction.encode()) # Sending initial message to the client
#     player = Player(dungeon.get_room('room1'))  # Start player in room1

#     while True:
#         data = conn.recv(1024)
#         if not data:
#             break

#         command = data.decode().lower()
#         response = dungeon.process_command(player, command)
#         conn.sendall(response.encode())

#     # 7. Sockets are closed (can use with in python3)
#     conn.close()

# def start_server():
#     host = 'localhost'
#     port = 12345  # Must match the client's port

#     # 1. The server creates a socket and binds to ‘localhost’ and port xxxx
#     # 2. The server then listens for a connection    
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((host, port))
#     server.listen()

#     dungeon = Dungeon()  # Initialize the dungeon

#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr, dungeon))
#         thread.start()

# if __name__ == "__main__":
#     start_server()

# Improved code for extra credit
def handle_client(conn, addr, dungeon):
    try:
        introduction = ("You are a normal student walking on campus. In front of you, a little robot is delivering food. "
                        "The robot gets stuck on the sidewalk, and you decide to help it. "
                        "Suddenly, you get hit by a car and die! "
                        "When you open your eyes, you find yourself transformed into a small food delivery robot. Your adventure begins!\n\n"
                        "Available commands:\n"
                        "go [direction] - Move in a direction (north, south, east, west)\n"
                        "look - Get a description of your current location\n"
                        "fight [monster] - Engage in combat with a monster\n"
                        "talk [monster] - Attempt to talk to a monster\n"
                        "status - See your current friends count\n"
                        "quit or exit - Exit game\n")

        print(f"New connection from {addr}")  # Log new connection
        conn.sendall(introduction.encode())  # Send introduction message to client
        player = Player(dungeon.get_room('room1'))  # Initialize player in the dungeon

        while True:
            try:
                data = conn.recv(1024)  # Receive data from client
                if not data:
                    break  # Break loop if no data is received (client disconnected)

                command = data.decode().lower()
                if not command.strip():  # Check if command is empty or whitespace
                    response = "No command received. Please enter a valid command."
                else:
                    response = dungeon.process_command(player, command)  # Process valid command
                conn.sendall(response.encode())  # Send response back to client
            except ValueError as ve:
                logging.error(f"Value error: {ve}")  # Log value errors
                conn.sendall("Invalid input. Please try again.".encode())  # Inform client about invalid input
            except Exception as e:
                logging.error(f"Unexpected error: {e}")  # Log unexpected errors
                conn.sendall("An error occurred. Please try again.".encode())  # Inform client about unexpected error

    except socket.error as e:
        logging.error(f"Socket error: {e}")  # Log socket errors
    finally:
        conn.close()  # Ensure connection is closed
        print(f"Connection with {addr} closed.")  # Log connection closure

def start_server():
    logging.basicConfig(level=logging.INFO)  # Set up logging
    host = 'localhost'
    port = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))  # Bind server to localhost and port
    server.listen()  # Start listening for connections

    dungeon = Dungeon()  # Initialize the dungeon

    while True:
        try:
            conn, addr = server.accept()  # Accept new connections
            thread = threading.Thread(target=handle_client, args=(conn, addr, dungeon))
            thread.start()  # Start a new thread for each client
        except Exception as e:
            logging.error(f"Error accepting a connection: {e}")  # Log errors in accepting connections

if __name__ == "__main__":
    start_server()  # Start the server
