import pygame

class InventoryUI:
    def __init__(self):
        #sprite sheets
        self.button_sheet = pygame.image.load("assets/UI_pack/PNG/Buttons.png")
        self.inventory_sheet = pygame.image.load("assets/UI_pack/PNG/Inventory.png")

        #inventory button
        self.button_rect = pygame.Rect(94, 338, 56, 12)
        self.button_image = self.button_sheet.subsurface(self.button_rect)
        self.button_image = pygame.transform.scale(self.button_image, (112, 24))
        self.button_pos = (1148, 20)
        self.update_button_hitbox()

        #slotted inventory screen
        sf = 4
        self.inventory_rect = pygame.Rect(118, 0, 98, 102)
        self.inventory_image = self.inventory_sheet.subsurface(self.inventory_rect)
        inv_width = 98 * sf
        inv_height = 102 * sf
        self.inventory_image = pygame.transform.scale(self.inventory_image, (inv_width, inv_height))
        self.inventory_is_open = False
        self.inventory_pos = (640 - inv_width / 2, 360 - inv_height / 2)
        self.inv_x, self.inv_y = self.inventory_pos

        self.close_x = 2 * sf
        self.close_y = 2 * sf
        self.close_dim = 10 * sf
        self.close_pos = (self.inv_x + inv_width - self.close_dim - self.close_x, self.inv_y + self.close_y)
        self.update_close_hitbox()


    def update_button_hitbox(self):
        self.button_hitbox = pygame.Rect(
            self.button_pos[0],
            self.button_pos[1],
            self.button_image.get_width(),
            self.button_image.get_height()
        )

    def update_close_hitbox(self):
        self.close_hitbox = pygame.Rect(
            self.close_pos[0],
            self.close_pos[1],
            self.close_dim,
            self.close_dim
        )


    def draw_button(self, renderer):
        renderer.draw_sprite(self.button_image, self.button_pos)

    def draw_inventory(self, renderer):
        renderer.draw_sprite(self.inventory_image, self.inventory_pos)