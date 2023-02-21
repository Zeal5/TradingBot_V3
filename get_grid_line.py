import time

def max_loss(grid: dict, qty:int,shorts_sl,longs_sl) -> int:
    """takes in first and last price of grid and returns the maxx loss"""
    short_losses = []
    long_losses = []
    usd_loss_l = []
    usd_loss_s = []
    usd_req = 0
    for k,current_price in grid.items():
        usd_req += current_price * qty
        short_loss_percentage = ((shorts_sl - current_price) / current_price) * 100 
        short_losses.append(short_loss_percentage)
        usd_loss_s.append((short_loss_percentage * (current_price * qty)/100))

        long_loss_percentage = ((current_price - longs_sl) / current_price) * 100
        long_losses.append(long_loss_percentage)
        usd_loss_l.append((long_loss_percentage * (current_price * qty))/100 )
        usd_req += current_price * qty

    print(f"max long drawdown {sum(usd_loss_l):.2f} X lev\nmax shorts drawdown {sum(usd_loss_s):.2f}")

    



# grid always strats from bottom to top start < stop
def grid_line_map(start: int, stop, profit_percentage: float, qty:int) -> dict:
    """gets start, stop price of grid line and profit% and converts it into
    enumurated dict with grid lines for given profit%"""
    profit_percentage = profit_percentage / 100
    grid_list = []
    if start > stop:
        start, stop = stop, start
    n = 0
    a = 0

    while a < stop:
        grid_list.append(start + (start * (profit_percentage * n)))
        a = start + (start * (profit_percentage * n))
        n += 1
    grid = dict(enumerate(grid_list,start=1))
    shorts_stop = list(grid.values())[-1]
    longs_stop  = list(grid.values())[0]
    # shorts_stop = 26.68
    # longs_stop = 23.11
    max_loss(grid, qty,shorts_sl = shorts_stop,longs_sl = longs_stop)
    return( grid)


# grid_lines = grid_line_map(0.1800, 0.1835, profit_percentage=1, qty=111)