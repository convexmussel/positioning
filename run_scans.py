from Scanmethods.Precision.simplex_2d import Simplex_2D
from data_visualisation.plot import Plot
from Scanmethods.snake_scan import SnakeScan

snake = SnakeScan()
for i in range(0, 16):
    print(i*2)
    snake.interfaces.move(0, 0, (30-i*2))
    snake.snake_scan()
    snake.save_data("um from wave guide" + str(30 - i*2) + "readings turnnob-8-3-1,2-minimaal3.xls")
