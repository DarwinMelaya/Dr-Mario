from dr_mario_logic import DrMario

def main():
    try:
        game = DrMario()
        
        # Get dimensions with error checking
        try:
            rows = int(input("Enter number of rows: "))
            cols = int(input("Enter number of columns: "))
            if rows <= 0 or cols <= 0:
                raise ValueError("Dimensions must be positive numbers")
        except ValueError as e:
            print(f"Error: {e}")
            return

        game.initialize(rows, cols)
        print("Game initialized. Enter commands (press Ctrl+D or type 'Q' to quit):")

        while True:
            try:
                command = input().strip()
            except EOFError:
                break

            try:
                if command == '':
                    game.pass_time()
                    game.print_field()
                elif command == 'Q':
                    break
                elif command == 'EMPTY':
                    game.set_empty_field()
                    game.print_field()
                elif command == 'CONTENTS':
                    lines = []
                    print(f"Enter {rows} lines of content:")
                    for _ in range(rows):
                        line = input().strip()
                        if len(line) != cols:
                            raise ValueError(f"Each line must be {cols} characters long")
                        lines.append(line)
                    game.set_field_contents(lines)
                    game.print_field()
                elif command.startswith('F '):
                    parts = command.split()
                    if len(parts) != 3:
                        raise ValueError("F command requires two colors (e.g., 'F R Y')")
                    game.spawn_faller(parts[1], parts[2])
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
                    game.print_field()
                else:
                    print(f"Unknown command: {command}")
            except Exception:
                # Don't show internal error details
                pass  # Just continue without showing error

    except Exception:
        # Don't show internal error details
        pass

if __name__ == '__main__':
    main()
