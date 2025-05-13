from typing import List, Optional

class DrMario:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.field: List[List[str]] = []
        self.faller: Optional[dict] = None
        self.is_game_over = False

    def initialize(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.field = [[' ' for _ in range(cols)] for _ in range(rows)]

    def set_empty_field(self):
        self.initialize(self.rows, self.cols)

    def set_field_contents(self, lines: List[str]):
        for r in range(self.rows):
            for c in range(self.cols):
                self.field[r][c] = lines[r][c]

    def print_field(self):
        faller_cells = self.get_faller_cells()
        for r in range(self.rows):
            line = '|'
            skip_next = False
            for c in range(self.cols):
                if skip_next:
                    skip_next = False
                    continue
                if (r, c) in faller_cells:
                    char, state = faller_cells[(r, c)]
                    if self.faller['orientation'] == 'horizontal' and (r, c + 1) in faller_cells:
                        right_char, _ = faller_cells[(r, c + 1)]
                        if state == 'falling':
                            line += f'[{char}--{right_char}]'
                        elif state == 'landed':
                            line += f'|{char}--{right_char}|'
                        elif state == 'frozen':
                            line += f' {char}--{right_char} '
                        skip_next = True
                    elif self.faller['orientation'] == 'vertical':
                        if state == 'falling':
                            line += f'[{char}]'
                        elif state == 'landed':
                            line += f'|{char}|'
                        elif state == 'frozen':
                            line += f'{char}'
                    else:
                        line += f' {char} '
                else:
                    line += self.render_cell(self.field[r][c])
            line += '|'
            print(line)

        print(' ' + '-' * (self.cols * 3) + ' ')
        if self.is_game_over:
            print('GAME OVER')
        elif not self.contains_virus():
            print('LEVEL CLEARED')

    def render_cell(self, cell: str) -> str:
        if cell in 'ryb':
            # Rendering the virus in lowercase when displaying it
            return f' {cell.lower()} '
        elif cell != ' ':
            return f' {cell} '
        return '   '

    def contains_virus(self) -> bool:
        return any(cell in 'ryb' for row in self.field for cell in row)

    def spawn_faller(self, left: str, right: str):
        mid = self.cols // 2 - 1
        if self.field[1][mid] != ' ' or self.field[1][mid + 1] != ' ':
            self.is_game_over = True
            return
        self.faller = {
            'row': 1,
            'col': mid,
            'orientation': 'horizontal',
            'left': left,
            'right': right,
            'state': 'falling'
        }

    def rotate_faller(self, clockwise=True):
        if self.faller and self.faller['orientation'] == 'horizontal':
            self.faller['orientation'] = 'vertical'
        elif self.faller and self.faller['orientation'] == 'vertical':
            self.faller['orientation'] = 'horizontal'

    def move_faller(self, direction: int):
        if not self.faller:
            return

        new_col = self.faller['col'] + direction
        r = self.faller['row']

        if self.faller['orientation'] == 'horizontal':
            if 0 <= new_col and new_col + 1 < self.cols and \
               self.field[r][new_col] == ' ' and self.field[r][new_col + 1] == ' ':
                self.faller['col'] = new_col

        elif self.faller['orientation'] == 'vertical':
            if 0 <= new_col < self.cols and \
               self.field[r][new_col] == ' ' and self.field[r - 1][new_col] == ' ':
                self.faller['col'] = new_col

    def insert_virus(self, row: int, col: int, color: str):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            # Ensure the virus color is always lowercase
            self.field[row][col] = color.lower()

    def pass_time(self):
        if not self.faller:
            matched = self.find_matches()
            if matched:
                self.remove_matches(matched)
                self.apply_gravity()
            return

        r = self.faller['row']
        c = self.faller['col']

        can_fall = False

        # Check if the faller can fall based on its orientation
        if self.faller['orientation'] == 'horizontal':
            if r + 1 < self.rows and self.field[r + 1][c] == ' ' and self.field[r + 1][c + 1] == ' ':
                can_fall = True
        else:
            if r + 1 < self.rows and self.field[r + 1][c] == ' ':
                can_fall = True

        # Handle different faller states
        if self.faller['state'] == 'falling':
            if can_fall:
                self.faller['row'] += 1
            else:
                self.faller['state'] = 'landed'
        elif self.faller['state'] == 'landed':
            if can_fall:
                self.faller['row'] += 1
                self.faller['state'] = 'falling'
            else:
                # Freeze the faller in place
                if self.faller['orientation'] == 'horizontal':
                    self.field[r][c] = self.faller['left']
                    self.field[r][c + 1] = self.faller['right']
                else:
                    self.field[r - 1][c] = self.faller['left']
                    self.field[r][c] = self.faller['right']
                self.faller = None  # Remove the faller

                # After freezing, check for matches and apply gravity
                matched = self.find_matches()
                if matched:
                    self.remove_matches(matched)
                    self.apply_gravity()

    def get_faller_cells(self):
        """Returns the coordinates of the faller cells."""
        result = {}
        if not self.faller:
            return result

        r = self.faller['row']
        c = self.faller['col']
        state = self.faller['state']

        if self.faller['orientation'] == 'horizontal':
            result[(r, c)] = (self.faller['left'], state)
            result[(r, c + 1)] = (self.faller['right'], state)
        else:
            result[(r - 1, c)] = (self.faller['left'], state)
            result[(r, c)] = (self.faller['right'], state)

        return result

    def find_matches(self) -> set:
        matched = set()
        faller_cells = self.get_faller_cells()

        # Horizontal matches
        for r in range(self.rows):
            for c in range(self.cols - 2):
                ch = self.field[r][c]
                # Skip empty cells and cells that are part of a falling piece
                if ch == ' ' or (r, c) in faller_cells:
                    continue
                # Compare uppercase versions to match viruses with pills
                if ch.upper() == self.field[r][c + 1].upper() == self.field[r][c + 2].upper():
                    # Only add to matches if none of the cells are part of a falling piece
                    if not any((r, col) in faller_cells for col in [c, c + 1, c + 2]):
                        matched.update([(r, c), (r, c + 1), (r, c + 2)])

        # Vertical matches
        for c in range(self.cols):
            for r in range(self.rows - 2):
                ch = self.field[r][c]
                # Skip empty cells and cells that are part of a falling piece
                if ch == ' ' or (r, c) in faller_cells:
                    continue
                # Compare uppercase versions to match viruses with pills
                if ch.upper() == self.field[r + 1][c].upper() == self.field[r + 2][c].upper():
                    # Only add to matches if none of the cells are part of a falling piece
                    if not any((row, c) in faller_cells for row in [r, r + 1, r + 2]):
                        matched.update([(r, c), (r + 1, c), (r + 2, c)])

        return matched

    def remove_matches(self, matched: set):
        for r, c in matched:
            self.field[r][c] = ' '

    def apply_gravity(self):
        for c in range(self.cols):
            # Only non-virus cells should fall
            stack = [self.field[r][c] for r in range(self.rows) if self.field[r][c] not in 'ryb' and self.field[r][c] != ' ']
            # Keep viruses in their original positions
            viruses = [(r, self.field[r][c]) for r in range(self.rows) if self.field[r][c] in 'ryb']
            
            # Clear the column
            for r in range(self.rows):
                self.field[r][c] = ' '
            
            # Restore viruses to their original positions
            for virus_row, virus_color in viruses:
                self.field[virus_row][c] = virus_color
            
            # Place non-virus cells at the bottom, above any viruses
            current_row = self.rows - 1
            for val in stack:
                while current_row >= 0 and self.field[current_row][c] in 'ryb':
                    current_row -= 1
                if current_row >= 0:
                    self.field[current_row][c] = val
                    current_row -= 1
