import arcade


class CameraController:
    def __init__(self):
        self.world_camera = arcade.Camera2D()

        self.base_pan_speed = 400.0

        self.min_zoom = 0.1
        self.max_zoom = 3.0
        self.target_zoom = 1.0
        self.zoom_speed = 8.0

    def use_world(self):
        self.world_camera.use()

    def update(self,
               delta_time: float,
               active_keys: set
               ):
        dx, dy = 0.0, 0.0
        if arcade.key.W in active_keys or arcade.key.UP in active_keys:
            dy += self.base_pan_speed * delta_time
        if arcade.key.S in active_keys or arcade.key.DOWN in active_keys:
            dy -= self.base_pan_speed * delta_time
        if arcade.key.A in active_keys or arcade.key.LEFT in active_keys:
            dx -= self.base_pan_speed * delta_time
        if arcade.key.D in active_keys or arcade.key.RIGHT in active_keys:
            dx += self.base_pan_speed * delta_time

        if dx != 0.0 or dy != 0.0:
            camera_x, camera_y = self.world_camera.position
            zoom_adjust = self.world_camera.zoom
            self.world_camera.position = (camera_x + (dx / zoom_adjust), camera_y + (dy / zoom_adjust))

        current_zoom = self.world_camera.zoom
        if abs(current_zoom - self.target_zoom) > 0.001:
            interpolated_zoom = current_zoom + (self.target_zoom - current_zoom) * (self.zoom_speed * delta_time)
            self.world_camera.zoom = interpolated_zoom

    def adjust_zoom_target(self, scroll_y: float):
        zoom_factor = 1.15 if scroll_y > 0 else (1.0 / 1.15)
        self.target_zoom = max(self.min_zoom, min(self.target_zoom * zoom_factor, self.max_zoom))
