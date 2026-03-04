from gui.gui import parse_puzzle_line

with open('data/test.csv', 'r', encoding='utf-8') as f:
    for i in range(3):
        line = f.readline().strip()
        print('line:', line)
        board = parse_puzzle_line(line)
        print('parsed?', board is not None, 'first row', board[0] if board else None)
