from dr_mario import DrMario
import sys

def parse_line_content(line: str, cols: int) -> str:
    # Remove leading/trailing spaces and ensure the line is the right length
    content = line.strip()
    # Pad with spaces if needed
    while len(content) < cols:
        content += ' '
    return content

def main():
    try:
        game = DrMario()
        
        # Get dimensions with error checking
        try:
            # Check if stdin is interactive or being piped
            is_interactive = sys.stdin.isatty()
            
            if is_interactive:
                rows = int(input("Enter number of rows: ").strip())
                cols = int(input("Enter number of columns: ").strip())
            else:
                rows = int(input().strip())
                cols = int(input().strip())
                
            if rows <= 0 or cols <= 0:
                raise ValueError("Dimensions must be positive numbers")
        except ValueError as e:
            print(f"Error: {e}")
            return

        game.initialize(rows, cols)
        
        if is_interactive:
            print("Game initialized. Enter commands (press Ctrl+D or type 'Q' to quit):")
            print("Commands:")
            print("  Direct input - Enter content directly (e.g., 'R  r' or 'YyYy')")
            print("  EMPTY - Clear the field")
            print("  CONTENTS - Set field contents")
            print("  F color1 color2 - Spawn a new faller")
            print("  A - Rotate clockwise")
            print("  B - Rotate counterclockwise")
            print("  < - Move left")
            print("  > - Move right")
            print("  V row col color - Insert virus")
            print("  Q - Quit")
            print("  ENTER - Pass time")
        
        empty_count = 0
        last_content_row = None

        while True:
            try:
                command = input().strip()
            except EOFError:
                break

            try:
                if command == '':
                    empty_count += 1
                    game.pass_time()
                    last_content_row = None
                    
                    if empty_count == 2 and game.faller and game.faller['state'] == 'falling':
                        game.faller['state'] = 'landed'
                        
                    game.print_field()
                elif command == 'Q':
                    break
                elif command == 'EMPTY':
                    game.set_empty_field()
                    last_content_row = None
                    game.print_field()
                elif command == 'CONTENTS':
                    lines = []
                    if is_interactive:
                        print(f"Enter {rows} lines of content:")
                    for _ in range(rows):
                        line = input().strip()
                        if len(line) != cols:
                            raise ValueError(f"Each line must be {cols} characters long")
                        lines.append(line)
                    game.set_field_contents(lines)
                    last_content_row = None
                    game.print_field()
                # Handle direct content input like "R  r" or "YyYy"
                elif all(c in 'RYBryb ' for c in command):
                    content = parse_line_content(command, cols)
                    current_field = [[''] * cols for _ in range(rows)]
                    
                    # Copy existing non-empty cells
                    for r in range(rows):
                        for c in range(cols):
                            if game.field[r][c] != ' ':
                                current_field[r][c] = game.field[r][c]
                    
                    # For initial placement (when field is empty), use row 1
                    target_row = 1
                    
                    # If there's existing content, place new content in row 3
                    for r in range(rows):
                        if any(game.field[r][c] != ' ' for c in range(cols)):
                            target_row = 3
                            break
                    
                    # Place the new content in the target row
                    for c in range(cols):
                        if content[c] != ' ':
                            current_field[target_row][c] = content[c]
                    
                    # Convert back to string lines
                    lines = []
                    for r in range(rows):
                        line = ''
                        for c in range(cols):
                            line += current_field[r][c] if current_field[r][c] != '' else ' '
                        lines.append(line)
                    
                    game.set_field_contents(lines)
                    game.print_field()
                elif command.startswith('F '):
                    parts = command.split()
                    if len(parts) != 3:
                        raise ValueError("F command requires two colors (e.g., 'F R Y')")
                    game.spawn_faller(parts[1], parts[2])
                    empty_count = 0
                    last_content_row = None
                    game.print_field()
                    if game.is_game_over:
                        break
                elif command == 'A':
                    game.rotate_faller(clockwise=True)
                    game.print_field()
                elif command == 'B':
                    game.rotate_faller(clockwise=False)
                    game.print_field()
                elif command in ['<', '>']:
                    direction = -1 if command == '<' else 1
                    game.move_faller(direction)
                    game.print_field()
                elif command.startswith('V '):
                    parts = command.split()
                    if len(parts) != 4:
                        raise ValueError("V command requires row, col, and color (e.g., 'V 3 4 R')")
                    game.insert_virus(int(parts[1]), int(parts[2]), parts[3])
                    last_content_row = None
                    game.print_field()
                else:
                    if is_interactive:
                        print(f"Unknown command: {command}")
            except Exception as e:
                if is_interactive:
                    print(f"Error: {e}")
                pass

    except Exception as e:
        if is_interactive:
            print(f"Error: {e}")
        pass

if __name__ == '__main__':
    main() 