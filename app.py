from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Default difficulty settings
DIFFICULTIES = {
    "easy": {"size": 8, "mines": 10},
    "medium": {"size": 12, "mines": 20},
    "hard": {"size": 16, "mines": 40}
}

def create_board(size, num_mines):
    board = [[' ' for _ in range(size)] for _ in range(size)]
    visible = [[False for _ in range(size)] for _ in range(size)]
    flagged = [[False for _ in range(size)] for _ in range(size)]
    mines = set()
    while len(mines) < num_mines:
        r, c = random.randint(0, size - 1), random.randint(0, size - 1)
        mines.add((r, c))
    for row in range(size):
        for col in range(size):
            if (row, col) in mines:
                board[row][col] = '*'
            else:
                count = sum((r, c) in mines
                            for r in range(row-1, row+2)
                            for c in range(col-1, col+2)
                            if 0 <= r < size and 0 <= c < size)
                board[row][col] = str(count) if count > 0 else ' '
    return board, visible, flagged, mines

# Global game state
game_board, visible_board, flagged_board, mines = create_board(8, 10)

def is_won(size):
    # The game is won if all cells without mines are revealed, and all mines are flagged
    for row in range(size):
        for col in range(size):
            if game_board[row][col] != '*' and not visible_board[row][col]:
                return False
            if game_board[row][col] == '*' and not flagged_board[row][col]:
                return False
    return True

@app.route('/')
def index():
    difficulty = request.args.get('difficulty', 'easy')
    size = DIFFICULTIES[difficulty]["size"]
    num_mines = DIFFICULTIES[difficulty]["mines"]
    
    global game_board, visible_board, flagged_board, mines
    game_board, visible_board, flagged_board, mines = create_board(size, num_mines)
    
    return render_template('index.html', board=visible_board, size=size, difficulty=difficulty)

@app.route('/reveal', methods=['POST'])
def reveal():
    row = int(request.json['row'])
    col = int(request.json['col'])
    
    if (row, col) in mines:
        return jsonify({'mine': True, 'row': row, 'col': col})

    reveal_cell(row, col)
    
    if is_won(len(game_board)):
        return jsonify({'won': True, 'board': visible_board, 'values': game_board})
    
    return jsonify({'won': False, 'board': visible_board, 'values': game_board})

@app.route('/flag', methods=['POST'])
def flag():
    row = int(request.json['row'])
    col = int(request.json['col'])
    
    flagged_board[row][col] = not flagged_board[row][col]
    
    if is_won(len(game_board)):
        return jsonify({'won': True, 'board': visible_board, 'values': game_board})
    
    return jsonify({'won': False, 'board': visible_board, 'values': game_board})

def reveal_cell(row, col):
    if not (0 <= row < len(game_board) and 0 <= col < len(game_board)) or visible_board[row][col]:
        return
    visible_board[row][col] = True
    if game_board[row][col] == ' ':
        for r in range(row-1, row+2):
            for c in range(col-1, col+2):
                reveal_cell(r, c)

if __name__ == '__main__':
    app.run(debug=True)
