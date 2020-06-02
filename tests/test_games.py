import unittest as ut
import bbench.games as bg

class Test_Round_Instance(ut.TestCase):

    def setUp(self):
        self.round = bg.Round([[1],[2],[3]], [1, 0, 1])

    def test_setUp(self):
        pass

    def test_action_features_correct(self):
        self.assertEqual([[1],[2],[3]], self.round.action_features)

    def test_action_features_readonly(self):

        def assign_action_features():
            self.round.action_features = [[4],[5],[6]]

        self.assertRaises(AttributeError, assign_action_features)

    def test_action_rewards_correct(self):
        self.assertEqual([1, 0, 1], self.round.action_rewards)

    def test_action_rewards_readonly(self):

        def assign_action_rewards():
            self.round.action_rewards = [2, 0, 1]

        self.assertRaises(AttributeError, assign_action_rewards)

class Test_ContextRound_Instance(Test_Round_Instance):
    def setUp(self):
        self.round = bg.ContextRound([1, 1, 1], [[1],[2],[3]], [1, 0, 1])

    def test_context_features_correct(self):
        self.assertEqual([1, 1, 1], self.round.context_features)

    def test_context_features_readonly(self):
        def assign_context_features():
            self.round.context_features = [2, 0, 1]

        self.assertRaises(AttributeError, assign_context_features)

class Test_Game_Instance(ut.TestCase):
    def setUp(self):
        self.rounds = [bg.Round([[1],[2],[3]], [1, 0, 1]), bg.Round([[1],[2],[3]], [1, 0, 1])]
        self.game = bg.Game(self.rounds)

    def test_setUp(self):
        pass

    def test_rounds_correct(self):
        self.assertIs(self.rounds, self.game.rounds)    

class Test_ContextGame_Instance(Test_Game_Instance):
    def setUp(self):
        self.rounds = [bg.ContextRound([1], [[1],[2],[3]], [1, 0, 1])]
        self.game = bg.ContextGame(self.rounds)

if __name__ == '__main__':
    ut.main()
