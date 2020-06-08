"""The games module contains core classes and types for defining bandit games.

This module contains the abstract interface expected for bandit game implementations along
with the class defining a Round within a bandit game. Additionally, this module also contains 
the type hints for State, Action and Reward. These type hints don't contain any functionality. 
Rather, they simply make it possible to use static type checking for any project that desires 
to do so.

Todo:
    * Add RegressionGame(Game)
"""

import csv

from abc import ABC, abstractmethod
from itertools import repeat
from typing import Optional, Iterable, Sequence, List, Union, Callable, TextIO, Collection, Generator

#state, action, reward types
State  = Union[str,float,Sequence[Union[str,float]]]
Action = Union[str,float,Sequence[Union[str,float]]]
Reward = float

class Round:
    """A class to contain all data needed to play and evaluate a round in a bandit game."""

    def __init__(self, 
                 state  : Optional[State], 
                 actions: Sequence[Action],
                 rewards: Sequence[Reward]) -> None:
        """Instantiate Round.

        Args:
            state: Features describing the round's state. Will be None for no context games.
            actions: Features describing available actions for the given state.
            rewards: The reward that would be received for taking each of the given actions.        
        """

        assert len(actions) > 0, "At least one action must be provided for the round"
        assert len(actions) == len(rewards), "Mismatched lengths of actions and rewards"

        self._state   = state
        self._actions = actions
        self._rewards = rewards

    @property
    def state(self) -> Optional[State]:
        """Read-only property providing the round's state."""
        return self._state

    @property
    def actions(self) -> Sequence[Action]:
        """Read-only property providing the round's possible actions."""
        return self._actions

    @property
    def rewards(self) -> Sequence[Reward]:
        """Read-only property providing the round's reward for each action."""
        return self._rewards

class Game(ABC):
    """The interface for Game implementations."""

    @property
    @abstractmethod
    def rounds(self) -> Union[Generator[Round,None,None],Collection[Round]]:
        """A read-only property providing the rounds in a game.

        Remarks:
            All benchmark implementations bbench.Benchmarks assume that rounds
            implementation is re-iterable. That is, they assume code such as two
            example for loops would iterate over all rounds in the given game:
                
                for round in game.rounds:
                    ...
                
                for round in game.rounds:
                    ...
            
            That rounds would be re-iterable is not a given. Most iterables in Python
            are in fact iterators and therefore can only be looped over one time.

        Returns:
            The return value of Generator and Collection are defined to make it more
            likely that an implementation will posess the property of being re-iterable
        """
        ...

class ClassifierGame(Game):
    """A Game implementation created from supervised learning data with features and labels.
    
    Remark:
        Game creation is done by turning each feature observation, with its label, into 
        a round. Each feature set becomes a state in a round and all possible labels
        become the action set for each round. Rewards for each round are created by 
        assigning a reward of 1 to the correct label (action) for a feature set (state)
        and a value of 0 for all other labels on that feature set.
    """

    @staticmethod
    def from_csv_path(csv_path: str, label_col:str, dialect='excel', **fmtparams) -> Game:
        """Create a ClassifierGame from a csv file with a header row.

        Args:
            csv_path: The path to the csv file.
            label_col: The name of the column in the csv file that represents the label.
            dialect: See `csv.reader` for an explanation of this parameter.
            fmtparams: A pass through key value parameter for `csv.reader`.

        Remarks:
            This method will open the file and read it all into memory. Be careful when doing
            this if you are working with a large file. One way to improve on this is to make
            sure column are correctly typed and all string columns are represented as integer
            backed categoricals (aka, `factors` in R).
        """

        with open(csv_path, newline='') as csv_file:
            return ClassifierGame.from_csv_file(csv_file, label_col, dialect=dialect, **fmtparams)

    @staticmethod
    def from_csv_file(csv_file:TextIO, label_col:str, dialect='excel', **fmtparams) -> Game:
        """Create a ClassifierGame from TextIO of a csv file.

        Args:
            csv_file: Any TextIO implementation including `open(csv_path)` and `io.StringIO()`.
            label_col: The name of the column in the csv file that represents the label.
            dialect: See `csv.reader` for an explanation of this parameter.
            fmtparams: A pass through key value parameter for `csv.reader`.

        Remarks:
            This method will open the file and read it all into memory. Be careful when doing
            this if you are working with a large file. One way to improve on this is to make
            sure column are correctly typed and all string columns are represented as integer
            backed categoricals (aka, `factors` in R).
        """

        features: List[Sequence[str]] = []
        labels  : List[str]           = []

        # In theory we don't have to load the whole file up front. However, in practice,
        # not loading the file upfront is hard due to the fact that Python can't really 
        # guarantee a generator will close the file.
        # For more info see https://stackoverflow.com/q/29040534/1066291
        # For more info see https://www.python.org/dev/peps/pep-0533/
        for num,row in enumerate(csv.reader(csv_file, dialect=dialect, **fmtparams)):
                if num == 0:
                    label_index = row.index(label_col)
                else:
                    features.append(row[:label_index] + row[(label_index+1):])
                    labels  .append(row[label_index])

        return ClassifierGame(features, labels)

    def __init__(self, features: Collection[State], labels: Collection[Union[str,float]]) -> None:
        """Instantiate a ClassifierGame.

        Args:
            features: The collection of features used for the original classifier problem.
            labels: The collection of labels assigned to each observation of features.
        """

        assert len(features) == len(labels), "Mismatched lengths of features and labels"

        self._label_set = list(set(labels))

        self._features = features
        self._labels   = labels

        states      = features
        action_set  = list(set(labels))
        reward_sets = [ [int(label==action) for action in action_set] for label in labels ]

        self._rounds = list(map(Round, states, repeat(action_set), reward_sets))

    @property
    def rounds(self) -> Collection[Round]:
        """The rounds in this game.
        
        Remarks:
            See this class's base class and class level docstring for more information.
        """
        return self._rounds

class LambdaGame(Game):
    """A Game implementation that uses lambda functions to generate states, actions and rewards.
    
    Remarks:
        This implementation is useful for creating simulations from defined distributions.
    """

    def __init__(self,
                 S: Callable[[],State], 
                 A: Callable[[State],Sequence[Action]], 
                 R: Callable[[State,Action],float])->None:
        """Instantiate a LambdaGame.

        Args:
            S: A lambda function that should return a new state every time it is called.
            A: A lambda function that should return all valid actions for a given state.
            R: A lambda function that should return reward given a state and action.
        """

        self._S = S
        self._A = A
        self._R = R

    @property
    def rounds(self) -> Generator[Round, None, None]:
        """The rounds in this game.

        Remarks:
            See the base class for more information.
        """

        S = self._S
        A = self._A
        R = self._R

        for s in (S() for _ in repeat(1)):
            yield Round(s, A(s), [R(s,a) for a in A(s)])

class MemoryGame(Game):
    """A Game implementation created using an in memory collection of Rounds.
    
    Remarks:
        This implementation is very useful for unit-testing known edge cases.
    """

    def __init__(self, rounds: Collection[Round]) -> None:
        """Instantiate a MemoryGame.

        Args:
            rounds: a collection of rounds to turn into a game.
        """
        self._rounds = rounds

    @property
    def rounds(self) -> Collection[Round]:
        """The rounds in this game.
        
        Remarks:
            See the base class for more information.
        """
        return self._rounds