from collections import Counter
from minesweeper_field import MinesweeperField, FieldType
import numpy as np


class MinesweeperBoard:

    def __init__(self, fields):
        field_matrix = self._sort_to_2d(fields)
        self._height, self._width = field_matrix.shape
        self._board = field_matrix

    def update(self, fields, delta = 5):
        updated_fields = []
        for i, row in enumerate(self._board):
            for j, col in enumerate(row):
                matching_field = next(
                    (field for field in fields 
                     if abs(field.x - col.x) <= delta and abs(field.y - col.y) <= delta),
                    None
                )
                if matching_field:
                    if self._board[i][j].type != FieldType.BOMB:
                      self._board[i][j].type = matching_field.type
                    updated_fields.append((i, j))
        
        all_indices = {(i, j) for i in range(self._height) for j in range(self._width)}
        not_updated_fields = all_indices - set(updated_fields)
        
        for i, j in not_updated_fields:
            self._board[i][j].type = FieldType.EMPTY

    def show(self):
        bombs_found = 0
        opened_fields = 0

        bombs_found = sum(field.type == FieldType.BOMB for row in self._board for field in row)
        opened_fields = sum(field.type != FieldType.BOMB and field.type != FieldType.UNKNOWN for row in self._board for field in row)

        print()
        for row in self._board:
            row_print = ''
            for col in row:
                 row_print += col.type.value
            print(row_print)
            
        print()
        print(f"OPENED FIELDS: {opened_fields}")
        print(f"BOMBS FOUND: {bombs_found}")

    def getWidth(self):
        return self._width
    
    def getHeight(self):
        return self._height
    
    def getFieldByKeys(self, row_index, col_index):
        return self._board[row_index][col_index]
    
    def getKeysByField(self, searched_field):
        for row_index, row in enumerate(self._board):
            for col_index, field in enumerate(row):
                if searched_field == field:
                    return (row_index, col_index)

        return False
    
    def changeFieldType(self, row_index, col_index, type):
        if  self._board[row_index][col_index].type != type:
            self._board[row_index][col_index].type = type
    
    def _sort_to_2d(self, fields):
        sorted_by_x = sorted(fields, key=lambda pos: (pos.y, pos.x))
        grouped = {}
        for position in sorted_by_x:
            if position.y not in grouped:
                grouped[position.y] = []
            grouped[position.y].append(position)

        sorted_2d = list(grouped.values())
        return np.array(sorted_2d, dtype=object)