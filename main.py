import pygame
import math
pygame.init()

class Point:
  def __init__(self, x, y, z, x_angle=None, horizontal_distance=None, y_angle=None, distance=None, screen_x=None, screen_y=None):
    self.x = x
    self.y = y
    self.z = z
  def calculate_angles(self, viewpoint):
    # calculates the difference in coordinates between the viewpoint and the point
    x_diff = self.x - viewpoint.x
    y_diff = self.y - viewpoint.y
    z_diff = self.z - viewpoint.z
    # calculates the horizontal angle (in degrees) from the viewpoint to the point
    try:
      self.x_angle = math.degrees(math.atan(
        y_diff / x_diff
      ))
      if self.x_angle >= 360:
        self.x_angle = self.x_angle % 360
    except:
      self.x_angle = math.pi
    print(self.x_angle)
    # calculates the horizontal distance to the point
    self.horizontal_distance = math.sqrt(x_diff**2 + y_diff**2)
    # calculates the vertical angle (in degrees) from the viewpoint to the point
    try:
      self.y_angle = math.degrees(math.atan(
        z_diff / self.horizontal_distance
      ))
      if self.y_angle > 360:
        self.y_angle = self.y_angle % 360
    except:
      self.y_angle = math.pi / 2
    # calculates the true distance to the point
    self.distance = math.sqrt(z_diff**2 + self.horizontal_distance**2)
  
  def calculate_position(self, viewpoint):
    relative_x_angle = (self.x_angle + viewpoint.x_angle) % 360
    relative_y_angle = (self.y_angle + viewpoint.y_angle) % 360

    if viewpoint.fov == 180:
      if 0 <= relative_x_angle <= 90:
        self.screen_x = relative_x_angle * 2 + 180
      elif 360 >= relative_x_angle >= 270:
        self.screen_x = (relative_x_angle - 270) * 2
      else:
        self.screen_x = None
      
      if 0 <= relative_y_angle <= 90:
        self.screen_y = (90 - relative_y_angle) * 2
      elif 360 >= relative_y_angle >= 270:
        self.screen_y = (360 - relative_y_angle) * 2 + 180
      else:
        self.screen_y = None
    else:
      self.screen_x = viewpoint.screen_distance * math.tan(math.radians(relative_x_angle)) + 180
      self.screen_y = viewpoint.screen_distance * math.tan(math.radians(relative_y_angle)) + 180
  
  def render(self, pygame, screen):
    if self.screen_x != None and self.screen_y != None:
      pygame.draw.circle(screen, (255, 255, 255), (point.screen_x, point.screen_y), 2)
    return(screen)

class Face:
  def __init__(self, point_indexes, colour, distance=None):
    self.point_indexes = point_indexes
    self.colour = colour
  
  def calculate_avg_distance(self, points):
    total_distance = 0
    for index in self.point_indexes:
      total_distance += points[index].distance
    self.distance = total_distance / len(self.point_indexes)
    
  def render(self, pygame, screen, points):
    poly_points = []
    for index in self.point_indexes:
      poly_points.append((points[index].screen_x, points[index].screen_y))
    pygame.draw.polygon(screen, self.colour, poly_points)

class Shape:
  def __init__(self, points, faces):
    self.points = points
    self.faces = faces
  
  def reorder_faces(self):
    for face in self.faces:
      face.calculate_avg_distance(self.points)
    self.faces.sort(key = lambda sort_key: sort_key.distance, reverse=True) 
  def recalculate_positions(self, viewpoint):
    for point in self.points:
      point.calculate_position(viewpoint)
    self.reorder_faces()
  def recalculate_angles(self, viewpoint):
    for point in self.points:
      point.calculate_angles(viewpoint)
    self.recalculate_positions(viewpoint)
  
  def render(self, pygame, screen):
    for face in self.faces:
      face.render(pygame, screen, self.points)

class Viewpoint:
  def __init__(self, x, y, z, x_angle, y_angle, fov, screen_distance=None):
    self.x = x
    self.y = y
    self.z = z
    self.x_angle = x_angle
    self.y_angle = y_angle
    self.fov = fov
  def fix_screen_distance(self):
    self.screen_distance = 180 / round(math.tan(math.radians(self.fov / 2)), 2) 

#point = Point(2, 1, 1)
viewpoint = Viewpoint(0, 0, 0, 0, 0, 180)
#viewpoint.fov = int(input('Field of View: '))
viewpoint.fov = 90
viewpoint.fix_screen_distance()
shape = Shape(
  [
    Point(200, 25, -125),
    Point(300, 25, -125),
    Point(200, 125, -125),
    Point(300, 125, -125),
    Point(200, 25, -25),
    Point(300, 25, -25),
    Point(200, 125, -25),
    Point(300, 125, -25),
  ],
  [
    Face((0, 2, 6, 4), (255, 0, 0)),
    Face((1, 3, 7, 5), (255, 0, 0)),
    Face((0, 1, 3, 2), (0, 255, 0)),
    Face((4, 5, 7, 6), (0, 255, 0)),
    Face((0, 1, 5, 4), (0, 0, 255)),
    Face((2, 3, 7, 6), (0, 0, 255)),
  ]
)
shape.recalculate_angles(viewpoint)

screen = pygame.display.set_mode((360,360))
pygame.display.set_caption('test')
clock = pygame.time.Clock()
running = True

while running == True:
  clock.tick(30)
  #exit
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      running = False
  pressed = pygame.key.get_pressed()
  if pressed[pygame.K_w]:
    viewpoint.x += 10
    shape.recalculate_angles(viewpoint)
  if pressed[pygame.K_s]:
    viewpoint.x -= 10
    shape.recalculate_angles(viewpoint)
  if pressed[pygame.K_a]:
    viewpoint.y -= 10
    shape.recalculate_angles(viewpoint)
  if pressed[pygame.K_d]:
    viewpoint.y += 10
    shape.recalculate_angles(viewpoint)
  if pressed[pygame.K_SPACE]:
    viewpoint.z += 10
    shape.recalculate_angles(viewpoint)
  if pressed[pygame.K_LSHIFT]:
    viewpoint.z -= 10
    shape.recalculate_angles(viewpoint)

  screen.fill((0, 0, 0))
  shape.render(pygame, screen)
  for point in shape.points:
    screen = point.render(pygame, screen)
  pygame.display.flip()
pygame.display.quit()
