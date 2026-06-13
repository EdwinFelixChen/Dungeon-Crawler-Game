def get_direction(object, target):
        dx = target.x - object.x
        dy = target.y - object.y

        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            return 0, 0, 0, 0

        object_dx = dx / distance
        object_dy = dy / distance

        target_dx = -dx / distance 
        target_dy = -dy / distance 

        return object_dx, object_dy, target_dx, target_dy