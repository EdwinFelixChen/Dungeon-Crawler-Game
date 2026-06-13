import random
from world.room import Room

class DungeonGenerator:

    def __init__(self):
        self.positions = [(0,0)]

    def generate(self, number_of_rooms):
        self.positions = [(0, 0)]
        self.num = number_of_rooms

        for _ in range(self.num - 1):
            position_index = random.randint(0, len(self.positions) - 1)
            
            base_x, base_y = self.positions[position_index]

            while True:

                axis = random.choice([1, 2])

                x, y = base_x, base_y

                if axis == 1:
                    x += random.choice([1, -1])

                else:
                    y += random.choice([1, -1])

                if (x, y) not in self.positions:
                    self.positions.append((x, y))
                    break

    def convert(self, room_size):
        rooms = []

        screen_width = 1280
        screen_height = 720

        offset_x = screen_width/2 - room_size/2
        offset_y = screen_height/2 - room_size/2

        for x, y in self.positions:
            position_x = x * room_size + offset_x
            position_y = y * room_size + offset_y

            room = Room(position_x, position_y, room_size, room_size)
            
            rooms.append(room)

        return rooms

    def add_doors(self, rooms: Room):
        #positions and doors list must match in order

        room_index = 0

        for x, y in self.positions:

            if (x + 1, y) in self.positions:

                rooms[room_index].doors["right"] = True
            
            if (x - 1, y) in self.positions:

                rooms[room_index].doors["left"] = True

            if (x, y + 1) in self.positions:

                rooms[room_index].doors["bottom"] = True

            if (x, y - 1) in self.positions:

                rooms[room_index].doors["top"] = True

            room_index += 1