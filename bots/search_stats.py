class SearchStats:

    def __init__(self):
        self.reset()

    def reset(self):

        self.nodes_searched = 0
        self.cutoffs = 0

        self.q_nodes = 0

        self.tt_hits = 0
        self.q_tt_hits = 0

        self.killer_hits = 0
        self.history_hits = 0

        self.lmr_reductions = 0


search_stats = SearchStats()