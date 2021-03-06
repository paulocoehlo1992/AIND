import types


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).
    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)
    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """
    return custom_score_weight(game, player, 1, 1.5)


def custom_score_weight(game, player, my_weight=1, opp_weight=1.5):
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    my_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(my_weight * my_moves - opp_weight * opp_moves)


def use_alpha_beta_pruning(alpha, beta):
    return alpha is not None and beta is not None


class GamePlayer:

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def should_timeout(self):
        return self.time_left() < (self.TIMER_THRESHOLD - 3)  # Give time to return

    def get_move(self, game, legal_moves, time_left):

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        move = (-1, -1)
        search_method = self.minimax if self.method == 'minimax' else self.alphabeta
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                current_depth = 1
                # while current_depth <= self.search_depth:
                while True:
                    move = search_method(game, current_depth)[1]
                    current_depth += 1
            else:
                move = search_method(game, self.search_depth)[1]
        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # best move available
        return move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.
                Parameters
                ----------
                game : isolation.Board
                    An instance of the Isolation game `Board` class representing the
                    current game state
                depth : int
                    Depth is an integer representing the maximum number of plies to
                    search in the game tree before aborting
                maximizing_player : bool
                    Flag indicating whether the current search depth corresponds to a
                    maximizing layer (True) or a minimizing layer (False)
                Returns
                ----------
                float
                    The score for the current search branch
                tuple(int, int)
                    The best move for the current branch; (-1, -1) for no legal moves
                """
        if maximizing_player:
            return self.max_value(game, depth)
        else:
            return self.min_value(game, depth)

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.
        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state
        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting
        alpha : float
            Alpha limits the lower bound of search on minimizing layers
        beta : float
            Beta limits the upper bound of search on maximizing layers
        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)
        Returns
        ----------
        float
            The score for the current search branch
        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """
        if maximizing_player:
            return self.max_value(game, depth, alpha, beta)
        else:
            return self.min_value(game, depth, alpha, beta)

    def max_value(self, game, depth, alpha=None, beta=None):
        if self.should_timeout():
            raise Timeout()

        if depth == 0:
            return self.score(game, self), (-1, -1)

        utility_score = float("-inf")
        next_move = (-1, -1)
        available_my_moves = game.get_legal_moves(self)
        for move in available_my_moves:
            next_score, _ = self.min_value(game.forecast_move(move), depth - 1, alpha, beta)
            if isinstance(next_score, types.FunctionType):
                print('bummer')
            if utility_score < next_score:
                utility_score = next_score
                next_move = move
            if use_alpha_beta_pruning(alpha, beta):
                if utility_score >= beta:
                    return utility_score, next_move
                alpha = max(alpha, utility_score)
        return utility_score, next_move

    def min_value(self, game, depth, alpha=None, beta=None):
        if self.should_timeout():
            raise Timeout()

        if depth == 0:
            return self.score(game, self), (-1, -1)

        utility_score = float("inf")
        next_move = (-1, -1)
        available_opponent_moves = game.get_legal_moves(game.get_opponent(self))
        for move in available_opponent_moves:
            next_score, _ = self.max_value(game.forecast_move(move), depth - 1, alpha, beta)
            if utility_score > next_score:
                utility_score = next_score
                next_move = move
            if use_alpha_beta_pruning(alpha, beta):
                if utility_score <= alpha:
                    return utility_score, next_move
                beta = min(beta, utility_score)
        return utility_score, next_move