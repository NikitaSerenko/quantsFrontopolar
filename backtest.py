# coding: utf-8
import numpy as np

listOrders = []
start_up = 0.0


def initialize(context):
    context.security = '13'
    context.name = 'SBER'
    context.cash = 1000000
    context.amount = 1000
    context.bet = 0


def handle_data(context, data):
    if data.time_index == 36:
        global start_up
        total_cost = context.cash + \
            context.amount * data.array[data.time_index]
        print("Total cost with stocks: %d \n\n" % total_cost)
        start_up = total_cost

    if context.bet == 1:
        operation = listOrders[-1][0]
        amount = listOrders[-1][1]
        time_index = listOrders[-1][2]
        take_profit = listOrders[-1][3]
        stop_loss = listOrders[-1][4]
        holding_period = listOrders[-1][5]

        if operation == 'buy':
            if data.array[data.time_index] > data.array[data.time_index - 1]:
                # correction(increase level of stop_loss)
                listOrders[-1][2] = data.time_index
                time_index = listOrders[-1][2]

            take_profit_bool = \
                bool(take_profit / 100.0 * data.array[time_index] <
                     data.array[data.time_index] - data.array[time_index])

            stop_loss_bool = \
                bool(stop_loss / 100.0 * data.array[time_index] <
                     data.array[time_index] - data.array[data.time_index])

            holding_period_bool = \
                bool(data.time_index - time_index > holding_period)

            if (take_profit_bool == 1 or stop_loss_bool == 1 or
                    holding_period_bool == 1):

                current_price = data.array[data.time_index + 1]
                context.cash += amount * current_price
                context.amount -= amount
                context.bet = 0
                print("Close long bet.\t Total stocks: %d \t Cash: %d\n"
                      % (context.amount, context.cash))

        elif operation == 'sell':
            if data.array[data.time_index] < data.array[data.time_index - 1]:
                # correction(decrease level of stop_loss)
                listOrders[-1][2] = data.time_index
                time_index = listOrders[-1][2]

            take_profit_bool = \
                bool(take_profit / 100.0 * data.array[time_index] <
                     data.array[time_index] - data.array[data.time_index])

            stop_loss_bool = \
                bool(stop_loss / 100.0 * data.array[time_index] <
                     data.array[data.time_index] - data.array[time_index])

            holding_period_bool = \
                bool(data.time_index - time_index > holding_period)

            if (take_profit_bool == 1 or stop_loss_bool == 1 or
                    holding_period_bool == 1) and \
                    context.cash >= amount * data.array[data.time_index]:

                current_price = data.array[data.time_index + 1]
                context.cash -= amount * current_price
                context.amount += amount
                context.bet = 0

                print("Close short bet.\t Total stocks: %d \t Cash: %d\n"
                      % (context.amount, context.cash))
    else:
        average_price = \
            data.array[data.time_index - 36: data.time_index].mean()
        current_price = data.array[data.time_index + 1]
        cash = context.cash
        amount = context.amount

        # Need to calculate how many shares we can buy and sell
        number_of_shares_buy = int(cash / current_price)
        number_of_shares_sell = amount

        if 1.01 * average_price < current_price < cash:
            # Place the buy order (positive means buy, negative means sell)
            operation = 'buy'
            order(operation, number_of_shares_buy, data.time_index + 1)
            context.cash -= number_of_shares_buy * current_price
            context.amount += number_of_shares_buy
            print("Buying %s \t Amount: %d \t Cash: %d \t TimeIndex: %d"
                  % (context.security, number_of_shares_buy,
                     context.cash, data.time_index + 1))
            context.bet = 1

        elif current_price < 0.99 * average_price and amount > 0:
            # Sell all of our shares by setting the target position to zero
            operation = 'sell'
            order(operation, amount, data.time_index + 1)
            context.cash += amount * current_price
            context.amount -= amount
            print("Selling %s \t Amount %d \t Cash: %d \t TimeIndex: %d"
                  % (context.security, number_of_shares_sell,
                     context.cash, data.time_index + 1))
            context.bet = 1

    if data.time_index == len(data.array) - 2:
        global start_up
        print(start_up)
        total_cost = \
            context.cash + context.amount * data.array[data.time_index]
        print("\n\nTotal cost with stocks: %d" % total_cost)
        percent = (total_cost - start_up) / start_up * 100.0
        print("Percent: %f" % percent)


def algorithms_to_orders(_initialize, _handle_data):
    class Empty:
        pass
    context = Empty()
    _initialize(context)

    class Data:
        def __init__(self, array):
            self.array = array.copy()
            self.time_index = 0

        def info(self):
            print('data: ', self.array)
            print('time_index: ', self.time_index)

    close = np.load('close.npy')
    data = Data(close)

    for data.time_index in range(36, len(close) - 1):
        _handle_data(context, data)


def order(operation, amount, time_index,
          take_profit=2.0, stop_loss=1.0, holding_period=10):
    listOrders.append([operation, amount, time_index,
                       take_profit, stop_loss, holding_period])


algorithms_to_orders(initialize, handle_data)
