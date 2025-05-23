from typing import List, Optional

class DrMario:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.field: List[List[str]] = []
        self.faller: Optional[dict] = None
        self.is_game_over = False
        self.direct_input_mode = False  # Flag to track which mode we're in

    def initialize(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.field = [[' ' for _ in range(cols)] for _ in range(rows)]

    def set_empty_field(self):
        self.initialize(self.rows, self.cols)

    def set_field_contents(self, lines: List[str]):
        for r in range(self.rows):
            c = 0
            while c < self.cols:
                if c + 2 < self.cols and lines[r][c:c+3] == 'R--' and lines[r][c+3] == 'Y':
                    self.field[r][c] = 'R'
                    self.field[r][c+3] = 'Y'
                    c += 4
                else:
                    self.field[r][c] = lines[r][c]
                    c += 1

    def print_field(self):
        faller_cells = self.get_faller_cells()
        matched_cells = self.find_matches()
        
        # Always show at least 4 rows
        for r in range(4):
            line = '|'
            skip_next = False
            for c in range(self.cols):
                if skip_next:
                    skip_next = False
                    continue
                
                cell = self.field[r][c]
                next_cell = self.field[r][c+1] if c+1 < self.cols else ' '
                
                if (r, c) in faller_cells:
                    char, state = faller_cells[(r, c)]
                    if self.faller['orientation'] == 'horizontal' and (r, c + 1) in faller_cells:
                        right_char, _ = faller_cells[(r, c + 1)]
                        if state == 'falling':
                            line += f'[{char}--{right_char}]'
                        elif state == 'landed':
                            line += f'|{char}--{right_char}|'
                        else:  # frozen
                            line += f' {char}--{right_char} '
                        skip_next = True
                    elif self.faller['orientation'] == 'vertical':
                        if state == 'falling':
                            line += f'[{char}]'
                        elif state == 'landed':
                            line += f'|{char}|'
                        else:  # frozen
                            line += f' {char} '
                    else:
                        line += f' {char} '
                else:
                    if (r, c) in matched_cells:
                        if cell == 'R' and next_cell == 'Y':
                            line += f'*{cell}*-{next_cell} '
                            skip_next = True
                        else:
                            line += f'*{cell}*'
                    else:
                        if cell == 'R' and next_cell == 'Y':
                            line += f' {cell}--{next_cell} '
                            skip_next = True
                        else:
                            line += f' {cell} '
            line += '|'
            print(line)

        print(' ' + '-' * (self.cols * 3) + ' ')
        has_viruses = self.contains_virus()
        if self.is_game_over:
            print('GAME OVER')
        elif not has_viruses:
            print('LEVEL CLEARED')

    def render_cell(self, cell: str) -> str:
        if cell in 'ryb':
            return f' {cell.lower()} '
        elif cell != ' ':
            return f' {cell} '
        return '   '

    def contains_virus(self) -> bool:
        return any(cell in 'ryb' for row in self.field for cell in row)

    def spawn_faller(self, left: str, right: str):
        mid = 1
        
        if self.field[1][mid] != ' ' or self.field[1][mid + 1] != ' ':
            self.faller = {
                'row': 1,
                'col': mid,
                'orientation': 'horizontal',
                'left': left,
                'right': right,
                'state': 'landed'
            }
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
        self.direct_input_mode = False  # Switch to faller mode

    def rotate_faller(self, clockwise=True):
        if not self.faller:
            return

        r = self.faller['row']
        c = self.faller['col']

        if self.faller['orientation'] == 'horizontal':
            if r-1 >= 0 and self.field[r-1][c] == ' ':
                self.faller['orientation'] = 'vertical'
                if clockwise:
                    pass
        else:
            if c + 1 < self.cols and self.field[r][c+1] == ' ':
                self.faller['orientation'] = 'horizontal'
                if not clockwise:
                    temp = self.faller['left']
                    self.faller['left'] = self.faller['right']
                    self.faller['right'] = temp

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
            self.field[row][col] = color.lower()
            self.direct_input_mode = True  # Switch to direct input mode

    def pass_time(self):
        if not self.faller:
            # First check for matches
            matched = self.find_matches()
            if matched:
                self.remove_matches(matched)
            # Always apply gravity, even if there were no matches
            self.apply_gravity()
            return

        r = self.faller['row']
        c = self.faller['col']

        can_fall = False

        if self.faller['orientation'] == 'horizontal':
            if r + 1 < self.rows and self.field[r + 1][c] == ' ' and self.field[r + 1][c + 1] == ' ':
                can_fall = True
        else:
            if r + 1 < self.rows and self.field[r + 1][c] == ' ':
                can_fall = True

        if self.faller['state'] == 'falling':
            if can_fall:
                self.faller['row'] += 1
            else:
                self.faller['state'] = 'landed'
        elif self.faller['state'] == 'landed':
            # First freeze the faller in place
            if self.faller['orientation'] == 'horizontal':
                self.field[r][c] = self.faller['left']
                self.field[r][c + 1] = self.faller['right']
            else:
                self.field[r - 1][c] = self.faller['left']
                self.field[r][c] = self.faller['right']
            self.faller = None

            # Check for matches
            matched = self.find_matches()
            if matched:
                # First print the field to show the matches with asterisks
                self.print_field()
                # Then remove matches and apply gravity
                self.remove_matches(matched)
            # Always apply gravity after freezing, even if there were no matches
            self.apply_gravity()

    def get_faller_cells(self):
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

    def find_matches(self):
        matched = set()
        faller_cells = self.get_faller_cells()

        # Check for horizontal matches first
        for r in range(self.rows):
            for c in range(self.cols - 3):
                ch = self.field[r][c]
                if ch == ' ' or (r, c) in faller_cells:
                    continue
                if ch.upper() == self.field[r][c + 1].upper() == self.field[r][c + 2].upper() == self.field[r][c + 3].upper():
                    if not any((r, col) in faller_cells for col in [c, c + 1, c + 2, c + 3]):
                        if ch.islower():
                            if all(self.field[r][col].islower() for col in [c, c + 1, c + 2, c + 3]):
                                matched.update([(r, c), (r, c + 1), (r, c + 2), (r, c + 3)])
                        else:
                            matched.update([(r, c), (r, c + 1), (r, c + 2), (r, c + 3)])

        # Check for vertical matches
        for c in range(self.cols):
            for r in range(self.rows - 3):
                ch = self.field[r][c]
                if ch == ' ' or (r, c) in faller_cells:
                    continue
                if ch.upper() == self.field[r + 1][c].upper() == self.field[r + 2][c].upper() == self.field[r + 3][c].upper():
                    if not any((row, c) in faller_cells for row in [r, r + 1, r + 2, r + 3]):
                        matched.update([(r, c), (r + 1, c), (r + 2, c), (r + 3, c)])

        return matched

    def remove_matches(self, matched):
        for r, c in matched:
            if self.field[r][c] == 'R' and c + 1 < self.cols and self.field[r][c + 1] == 'Y':
                self.field[r][c] = ' '
            else:
                self.field[r][c] = ' '

    def apply_gravity(self):
        moved = False
        for c in range(self.cols):
            # Move each piece down only one row per pass_time
            # Start from second-to-last row and move up
            for r in range(self.rows - 2, -1, -1):
                # Skip if current cell is empty or a virus (lowercase)
                if self.field[r][c] == ' ' or self.field[r][c].islower():
                    continue
                
                # Check if this is part of a horizontal vitamin pair
                is_horizontal_pair = False
                if c + 1 < self.cols and self.field[r][c].isupper() and self.field[r][c + 1].isupper():
                    is_horizontal_pair = True
                elif c > 0 and self.field[r][c].isupper() and self.field[r][c - 1].isupper():
                    # Skip if this is the right part of a pair (left part will handle it)
                    continue
                
                # If it's a horizontal pair and we can move both pieces down
                if is_horizontal_pair and self.field[r + 1][c] == ' ' and self.field[r + 1][c + 1] == ' ':
                    # Move both pieces down together
                    self.field[r + 1][c] = self.field[r][c]
                    self.field[r + 1][c + 1] = self.field[r][c + 1]
                    self.field[r][c] = ' '
                    self.field[r][c + 1] = ' '
                    moved = True
                    break
                # If it's a single piece and we can move it down
                elif not is_horizontal_pair and self.field[r + 1][c] == ' ':
                    self.field[r + 1][c] = self.field[r][c]
                    self.field[r][c] = ' '
                    moved = True
                    break
        return moved

def parse_line_content(line: str, cols: int) -> str:
    content = line.strip()
    # Pad with spaces to match the required length
    while len(content) < cols:
        content += ' '
    # Truncate if too long
    return content[:cols]
