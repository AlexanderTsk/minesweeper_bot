import pygetwindow as gw
import cv2
import mss
import numpy as np
from minesweeper_board import MinesweeperBoard
from image_vision import ImageVision
import config
from minesweeper_field import MinesweeperField, FieldType
import pyautogui
import random

class Game:

    def __init__(self, argv = []):
        self._last_fields_snapshot = None
        self._debug_mode = False
        if len(argv) >= 2:
            if argv[1] == '--debug':
                self._debug_mode = True


        self._running = False

        self.image_vision = ImageVision()
        self._objects = {
            FieldType.UNKNOWN: config.UNKNOWN_OBJECT, 
            FieldType.ONE: config.ONE_OBJECT, 
            FieldType.TWO: config.TWO_OBJECT, 
            FieldType.THREE: config.THREE_OBJECT, 
            FieldType.FOUR: config.FOUR_OBJECT, 
            FieldType.FIVE: config.FIVE_OBJECT,
            FieldType.SIX: config.SIX_OBJECT
            }
        
        self._round = 0

    def run(self):
        self._create_window()

        self._running = True
        while self._running:
            self._round += 1

            with mss.mss() as sct:
                monitor = {"top": self._window.top, "left": self._window.left, "width": self._window.width, "height": self._window.height}
                
                frame = np.array(sct.grab(monitor))

                #DETECT EVERY SINGLE OBJECT ON SCREEN
                detected_objects = {}
                masks = {}
                fields = []
                for key in self._objects:
                    detected_objects[key], masks[key] = self.image_vision.detect_object(frame, self._objects[key])
                    frame = self._draw_boxes(frame, self._objects[key]["box_hex_color"], detected_objects[key])
                    #CONVERT FOUNDED BOXES TO FIELDS ARRAY
                    for detected_object in detected_objects[key]:
                        x, y, w, h = detected_object
                        center_x = int(x + w // 2)
                        center_y = int(y + h // 2)
                        fields.append(MinesweeperField(type=key, x=center_x, y=center_y))
              
                if self._last_fields_snapshot == fields:
                    print("Looks like I'm lost:( Please restart the game and try again.")
                    break

                self._last_fields_snapshot = fields

                #SORT FIELDS ARRAY TO MATRIX BY COORDINATES AND CREATE BOARD
                if self._round == 1:
                    try:
                        self._board = MinesweeperBoard(fields)
                    except Exception:
                        print("Game board creation failed. Restart the program and try again.")
                        break
              
                #UPDATE BOARDS
                self._board.update(fields)
                self._board.show()
                print(f"ROUND: {self._round}")
                
                if self._debug_mode:
                    for key in self._objects:
                        cv2.imshow(f"Debug mask [{key.name}]", masks[key])  

                cv2.imshow("Minesweeper automation", frame)  

                print("I'm thinking! Please wait...")
                key = cv2.waitKey(1000)
                if key == 27:
                    self._running = False
                else:
                    if self._is_game_over():
                        print("Congratulations!!! You are winner!!!")
                        break    
                    self._predict_and_click()
                     
    
        cv2.destroyAllWindows()
        self._running = False

    def _create_window(self):
        print("Select number with game window title: ")
        titles = gw.getAllTitles()
        titles = list(set(titles))

        number = 1
        for title in titles[:]:
            if len(str(title).strip()) > 0:
                print(f"{number}. {title}")
                number += 1
            else:
                titles.remove(title)

        while True:
            try:
                title_index = int(input())
                window_title = titles[title_index-1]
            except ValueError:
                print("Invalid window title numer. Try again.")
                continue
            break

        self._window = gw.getWindowsWithTitle(window_title)[0]
        self._window.activate()

    def _draw_boxes(self, image, box_hex_color, objects):
        for object in objects:
            x, y, w, h = object

            box_bgr_color = self.image_vision.hex_to_bgr(box_hex_color)
            image = cv2.rectangle(image, (x, y), (x + w, y + h), box_bgr_color, 2)

        return image
    
    def _find_bomb_field_keys(self):
        detected_bombs = []
        for row_index in range(self._board.getHeight()): 
            for col_index in range(self._board.getWidth()): 

                field = self._board.getFieldByKeys(row_index, col_index)
                neighbors = self._get_neighbor_fields(row_index, col_index)
                bomb_neighbors = [neighbor for neighbor in neighbors if neighbor.type == FieldType.BOMB]
                unknown_neighbors = [neighbor for neighbor in neighbors if neighbor.type == FieldType.UNKNOWN]

                if field.type == FieldType.ONE and (1 - len(bomb_neighbors)) == len(unknown_neighbors):
                    detected_bombs.append(self._extractFieldsKeys(unknown_neighbors)) 
                elif field.type == FieldType.TWO and (2 - len(bomb_neighbors)) == len(unknown_neighbors):
                    detected_bombs.append(self._extractFieldsKeys(unknown_neighbors)) 
                elif field.type == FieldType.THREE and (3 - len(bomb_neighbors)) == len(unknown_neighbors):
                   detected_bombs.append(self._extractFieldsKeys(unknown_neighbors))  
                elif field.type == FieldType.FOUR and (4 - len(bomb_neighbors)) == len(unknown_neighbors):
                    detected_bombs.append(self._extractFieldsKeys(unknown_neighbors)) 
                elif field.type == FieldType.FIVE and (5 - len(bomb_neighbors)) == len(unknown_neighbors):
                    detected_bombs.append(self._extractFieldsKeys(unknown_neighbors)) 
                elif field.type == FieldType.SIX and (6 - len(bomb_neighbors)) == len(unknown_neighbors):
                    detected_bombs.append(self._extractFieldsKeys(unknown_neighbors)) 
        
        flattened_bomb_list = [item for sublist in detected_bombs for item in sublist]
        return list(set(flattened_bomb_list))
    
    def _find_safety_field_keys(self):
        detected_safety = []
        for row_index in range(self._board.getHeight()): 
            for col_index in range(self._board.getWidth()): 

                field = self._board.getFieldByKeys(row_index, col_index)
                neighbors = self._get_neighbor_fields(row_index, col_index)
                bomb_neighbors = [neighbor for neighbor in neighbors if neighbor.type == FieldType.BOMB]
                unknown_neighbors = [neighbor for neighbor in neighbors if neighbor.type == FieldType.UNKNOWN]

                if field.type == FieldType.ONE and len(bomb_neighbors) == 1:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors)) 
                elif field.type == FieldType.TWO and len(bomb_neighbors) == 2:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors))
                elif field.type == FieldType.THREE and len(bomb_neighbors) == 3:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors))
                elif field.type == FieldType.FOUR and len(bomb_neighbors) == 4:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors))
                elif field.type == FieldType.FIVE and len(bomb_neighbors) == 5:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors))
                elif field.type == FieldType.SIX and len(bomb_neighbors) == 6:
                    detected_safety.append(self._extractFieldsKeys(unknown_neighbors))

        flattened_safe_list = [item for sublist in detected_safety for item in sublist]
        return list(set(flattened_safe_list))
    
    def _find_first_unknown_field(self):
        for row_index in range(self._board.getHeight()): 
            for col_index in range(self._board.getWidth()): 
                field = self._board.getFieldByKeys(row_index, col_index)
                if field.type == FieldType.UNKNOWN:
                    return field
        return None
    
    def _find_random_unknown_field(self):
        w, h = self._board.getWidth(), self._board.getHeight()

        while True:
            random_row = random.randint(0, h - 1)
            random_col = random.randint(0, w - 1)
            field = self._board.getFieldByKeys(random_row, random_col)
            if field.type == FieldType.UNKNOWN:
                return field
    
    def _get_neighbor_fields(self, row_index, col_index):
        neighbors = []
        rows, cols = self._board.getHeight(), self._board.getWidth()

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue 
                nx, ny = row_index + i, col_index + j 
                if 0 <= nx < rows and 0 <= ny < cols:  
                    neighbors.append(self._board.getFieldByKeys(nx, ny)) 
        return neighbors

    def _extractFieldsKeys(self, fields):
        extracted_keys = []
        for field in fields:  
            keys = self._board.getKeysByField(field)
            if keys:
                extracted_keys.append(keys) 

        return extracted_keys
    
    def _predict_and_click(self):
        bomb_field_keys = self._find_bomb_field_keys()
        for key in bomb_field_keys:
            self._board.changeFieldType(key[0], key[1], FieldType.BOMB)

        safety_field_keys = self._find_safety_field_keys()
        if len(safety_field_keys) > 0:
            field = self._board.getFieldByKeys(safety_field_keys[0][0], safety_field_keys[0][1])
        else:
            field = self._find_random_unknown_field()
        
        global_x = self._window.left + field.x
        global_y = self._window.top + field.y

        pyautogui.moveTo(global_x, global_y, duration=0.1)
        pyautogui.click()  

    def _is_game_over(self):
        unknowns_count = 0
        for row_index in range(self._board.getHeight()): 
            for col_index in range(self._board.getWidth()): 
                if self._board.getFieldByKeys(row_index, col_index).type == FieldType.UNKNOWN:
                    unknowns_count += 1
            
        if unknowns_count == 1: 
            return True    
        
        return False