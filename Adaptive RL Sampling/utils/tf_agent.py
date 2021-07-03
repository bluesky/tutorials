# Add class structure from https://github.com/bnl/pub-Maffettone_2021_02
# Full environment needed to initialize agent. A skeleton could be used, but nah tho.
# Modified setup to remove some functionality like saving and GPU etc
# Add load function
from pathlib import Path

import numpy as np
from tensorforce import Agent
from tensorforce.environments import Environment


class CartSeed(Environment):
    def __init__(
        self,
        seed_count,
        *,
        bad_seed_count=None,
        max_count=10,
        frozen_order=False,
        sequential=False,
        revisiting=True,
        bad_seed_reward_f=None,
        good_seed_reward_f=None,
        measurement_time=None,
    ):
        """
        Bad seeds, but make it cartpole...

        Assuming the envrionment experiences two kinds of seeds:
            - Good Seeds that no longer need to be sampled
            - Bad Seeds that need to be sampled a fixed amount

        This allows for a deterministic high score that a well behaved agent will approach.
        The key assumptions of this framing are that from an initial sampling of all seeds (brief scans of all samples)
        it will be clear which are Bad and which are Good. This should be extensible to varying degrees of goodness.

        Scores are default scaled to 100.
        If a bad_seed_reward_f is given, no scaling is done unelss a point max is given.
        Parameters
        ----------
        seed_count: int
            Number of total seeds
        bad_seed_count: int, None
            Number of bad seeds. If None, a variable amount will be used for each reset.
        max_count: int
            Maximum number of samples/scans needed to saturate a bad_seed
        frozen_order: bool
            For debugging or an easier game. This locks the order of the seeds and order of the sampling.
            Bad seeds are the first set of seeds.
        sequential: bool
            Visit the samples in sequential order, not randomly.
        revisiting: bool
            Whether to allow revisiting of past samples. Once all samples are visited, the memory resets.
            The memory is a hashable set that gets emptied when its length reaches the seed count.
            A possible update is to make this a terminal condition.
        bad_seed_reward: function
            Function of the form f(state, terminal, action). Where the state is the resultant state from the action.
        good_seed_reward: function
            Function of the form f(state, terminal, action). Where the state is the resultant state from the action.
        measurement_time: int, None
            Override for max_episode_timesteps in Environment.create().
            Passing a value of max_episode_timesteps to Environment.create() will override measurement_time and the
            default max_episode_timesteps(), raising an UnexpectedError if the override value is greater than the others.
        """
        super().__init__()

        if bad_seed_count is None:
            self.variable_bad_seed = True
            self.bad_seed_count = 0
        elif bad_seed_count > seed_count:
            raise ValueError("bad_seed_count must be less than or equal to seed_count")
        else:
            self.bad_seed_count = bad_seed_count
            self.variable_bad_seed = False
        self.seed_count = seed_count
        # Hidden functions that get rescaled
        if bad_seed_reward_f is None:
            self._bad_seed_reward_f = lambda s, t, a: 1
        else:
            self._bad_seed_reward_f = bad_seed_reward_f
        self.bad_seed_reward_f = None  # Get's set and rescaled on reset()
        if good_seed_reward_f is None:
            self.good_seed_reward_f = lambda s, t, a: 0
        else:
            self.good_seed_reward_f = good_seed_reward_f

        self.max_count = max_count
        self.frozen_order = bool(frozen_order)
        self.sequential_order = bool(sequential)
        self.revisiting = bool(revisiting)
        self.measurement_time = measurement_time
        self.visited = set()
        self.timestep = 0

        self.seeds = np.empty((seed_count, 2))
        self.current_idx = None
        self.exp_sequence = []

        self.bad_seed_indicies = None
        self.good_seed_indicies = None

        self.rng = np.random.default_rng()

    def bad_seed_reward(self, state, terminal, action):
        """
        Functional approach to the bad seed reward
        Parameters
        ----------
        state: array
            Current state
        terminal: bool
            Current terminal status
        action: array
            Action preceeding the current state
        Returns
        -------
        reward
        """
        return self.bad_seed_reward_f(state, terminal, action)

    def good_seed_reward(self, state, terminal, action):
        """
        Functional approach to the good seed reward
        Parameters
        ----------
        state: array
            Current state
        terminal: bool
            Current terminal status
        action: array
            Action preceeding the current state
        Returns
        -------
        reward
        """
        return self.good_seed_reward_f(state, terminal, action)

    def states(self):
        """
        State is current seed [bool(bad), countdown]

        Returns
        -------
        state specification
        """
        return dict(type="float", shape=(2,))

    def actions(self):
        """
        Actions specification: Stay or go
        Returns
        -------
        Action spec
        """
        return dict(type="int", num_values=2)

    def max_episode_timesteps(self):
        """
        Returns
        -------
        Maximum count equivalent to maximum possible score plus required moves to get there.
        Is overridden by the use inclusion of max_episode_timesteps in Environment.create() kwargs.
        (This uses a hidden variable from tensorforce.Environment)
        """
        if self.measurement_time is None:
            return self.max_count * self.bad_seed_count + self.seed_count
        else:
            return self.measurement_time

    def reset(self):
        """
        Sets up seeds array and indicies. Plenty of redundant tracking.
        If frozen order is set, then the first 3 indicies are always bad seeds.
        If variable bad seed, the bad seed count is randomly varied, and the max score is kept at 100.
        Returns
        -------
        State
        """
        self.timestep = 0
        l = list(range(self.seed_count))
        if not self.frozen_order:
            self.rng.shuffle(l)

        if self.variable_bad_seed:
            self.bad_seed_count = self.rng.integers(self.seed_count)

        # Always scales the reward such that the optimal performance is 100
        # Does this for defaults as well as calculating optimal points for input functions
        if self.bad_seed_count > 0:
            point_max = (
                np.sum(
                    [
                        self._bad_seed_reward_f([1, p], None, None)
                        for p in range(self.max_count, 0, -1)
                    ]
                )
                * self.bad_seed_count
            )
            self.bad_seed_reward_f = (
                lambda s, t, a: self._bad_seed_reward_f(s, t, a) * 100 / point_max
            )
        else:
            self.bad_seed_reward_f = self._bad_seed_reward_f

        self.bad_seed_indicies = l[: self.bad_seed_count]
        self.good_seed_indicies = l[self.bad_seed_count :]
        self.seeds[self.bad_seed_indicies, :] = [1, self.max_count]
        self.seeds[self.good_seed_indicies, :] = [0, 0]

        self.current_idx = self.rng.integers(self.seed_count)
        self.exp_sequence.append(self.current_idx)
        state = self.seeds[self.current_idx, :]
        return state

    def execute(self, actions):
        """
        Updates timestep
        Updates state if moved
        Updates overall seed tracking (countdown)
        Calculates reward based on current seed and positive countdown

        Parameters
        ----------
        action: bool

        Returns
        -------
        next_state: array
        terminal: bool
        reward: float
        """
        self.timestep += 1
        move = bool(actions)
        prev_index = self.current_idx
        if move:
            # Clear previously visited or complete episode if all samples visited
            if len(self.visited) == self.seed_count:
                if not self.revisiting:
                    state = self.seeds[prev_index, :]
                    terminal = True
                    reward = self.good_seed_reward(state, terminal, actions)
                    return state, terminal, reward
                else:
                    self.visited = set()
            # Frozen order  and sequential order iterates
            if self.frozen_order or self.sequential_order:
                self.current_idx = (self.current_idx + 1) % self.seed_count
            # Otherwise random change that hasn't been visited
            else:
                self.current_idx = self.rng.integers(self.seed_count)
                while (
                    self.current_idx in self.visited or self.current_idx == prev_index
                ):
                    self.current_idx = self.rng.integers(self.seed_count)
        # Add to memory
        if not self.revisiting:
            self.visited.add(self.current_idx)

        self.exp_sequence.append(self.current_idx)
        state = self.seeds[self.current_idx, :]

        if self.timestep >= self.max_episode_timesteps():
            terminal = True
        else:
            terminal = False

        if (
            bool(self.seeds[self.current_idx, 0])
            and self.seeds[self.current_idx, 1] > 0
        ):
            reward = self.bad_seed_reward(state, terminal, actions)
        else:
            reward = self.good_seed_reward(state, terminal, actions)

        self.seeds[self.current_idx, 1] -= 1

        return state, terminal, reward


class CartSeedCountdown(CartSeed):
    """
    CartSeed01, with variable countdown (proxy for badness of seed), and no boolean in state

    Assuming the envrionment experiences two kinds of seeds:
            - Good Seeds that no longer need to be sampled
            - Bad Seeds that need to be sampled a randomly initialized amount (less than or equal to max_count)

    See CartSeed for further details which are identical.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_max_count = self.max_count * self.bad_seed_count

    def reset(self):
        super().reset()
        for i in self.bad_seed_indicies:
            self.seeds[i, 1] = self.rng.integers(1, self.max_count)

        # Always scales the reward such that the optimal performance is 100
        # Does this for defaults as well as calculating optimal points for input functions
        if self.bad_seed_count > 0:
            point_max = np.sum(
                [
                    self._bad_seed_reward_f(self.seeds[i, 1], None, None)
                    * self.seeds[i, 1]
                    for i in self.bad_seed_indicies
                ]
            )
            self.bad_seed_reward_f = (
                lambda s, t, a: self._bad_seed_reward_f(s, t, a) * 100 / point_max
            )
        else:
            self.bad_seed_reward_f = self._bad_seed_reward_f

        self.total_max_count = np.sum(self.seeds[:, 1])
        state = np.array([self.seeds[self.current_idx, 1]])
        return state

    def max_episode_timesteps(self):
        """
        Returns
        -------
        Maximum count equivalent to maximum possible score plus required moves to get there.
        Is overridden by the use inclusion of max_episode_timesteps in Environment.create() kwargs.
        (This uses a hidden variable from tensorforce.Environment)
        """
        if self.measurement_time is None:
            return self.total_max_count + self.seed_count
        else:
            return self.measurement_time

    def states(self):
        """
        State is current seed [countdown]

        Returns
        -------
        state specification
        """
        return dict(type="float", shape=(1,))

    def execute(self, actions):
        """
        Updates timestep
        Updates state if moved
        Updates overall seed tracking (countdown)
        Calculates reward based on current seed and positive countdown

        Parameters
        ----------
        action: bool

        Returns
        -------
        next_state: array
        terminal: bool
        reward: float
        """
        self.timestep += 1
        move = bool(actions)
        prev_index = self.current_idx
        if move:
            # Clear previously visited or complete episode if all samples visited
            if len(self.visited) == self.seed_count:
                if not self.revisiting:
                    state = np.array([self.seeds[prev_index, 1]])
                    terminal = True
                    reward = self.good_seed_reward(state, terminal, actions)
                    return state, terminal, reward
                else:
                    self.visited = set()
            # Frozen order  and sequential order iterates
            if self.frozen_order or self.sequential_order:
                self.current_idx = (self.current_idx + 1) % self.seed_count
            # Otherwise random change that hasn't been visited
            else:
                self.current_idx = self.rng.integers(self.seed_count)
                while (
                    self.current_idx in self.visited or self.current_idx == prev_index
                ):
                    self.current_idx = self.rng.integers(self.seed_count)
        # Add to memory
        if not self.revisiting:
            self.visited.add(self.current_idx)

        self.exp_sequence.append(self.current_idx)
        state = np.array([self.seeds[self.current_idx, 1]])

        if self.timestep >= self.max_episode_timesteps():
            terminal = True
        else:
            terminal = False

        if state > 0:
            reward = self.bad_seed_reward(state, terminal, actions)
        else:
            reward = self.good_seed_reward(state, terminal, actions)

        self.seeds[self.current_idx, 1] -= 1

        return state, terminal, reward


def set_up(
    time_limit=100,
    batch_size=16,
    env_version=1,
    seed_count=10,
    max_count=10,
):
    """
    Set up a rushed CartSeed agent with less time than it needs to complete an episode.
    Parameters
    ----------
    time_limit : int, None
        Turn time limit for episode
    batch_size : int
        Batch size for training
    env_version : int in {1, 2}
        Environment version. 1 being ideal time, 2 being time limited
    seed_count : int
        Number of bad seeds
    max_count: int
            Maximum number of samples/scans needed to saturate a bad_seed

    Returns
    -------
    Environment
    Agent
    """

    def default_score(state, *args):
        return 1

    if env_version == 1:
        environment = CartSeed(
            seed_count=seed_count,
            bad_seed_count=None,
            max_count=max_count,
            sequential=True,
            revisiting=True,
            bad_seed_reward_f=default_score,
            measurement_time=time_limit,
        )
    elif env_version == 2:
        environment = CartSeedCountdown(
            seed_count=seed_count,
            bad_seed_count=None,
            max_count=max_count,
            sequential=True,
            revisiting=True,
            bad_seed_reward_f=default_score,
            measurement_time=time_limit,
        )
    else:
        raise NotImplementedError
    env = Environment.create(environment=environment)
    agent = Agent.create(agent="a2c", batch_size=batch_size, environment=env)

    return env, agent


def load_agent(
    path, *, time_limit=None, batch_size=16, env_version=1, seed_count=9, max_count=10
):
    """
    Loads pretrained A2C reinforcement for prediction.
    Because this uses the internals of TensorForce (Not TensorFlow), the environment needs to
    be fully specified along with the agent. Some keyword arguments have been left
    behind to make sure nothing gets broken.

    Parameters
    ----------
    path : Path, str
        path to load directory
    time_limit : int, None
        Turn time limit for episode
    batch_size : int
        Batch size for training
    env_version : int in {1, 2}
        Environment version. 1 being ideal time, 2 being time limited
    seed_count : int
        Number of bad seeds
    max_count: int
            Maximum number of samples/scans needed to saturate a bad_seed

    Returns
    -------

    """
    env, agent = set_up(
        time_limit=time_limit,
        batch_size=batch_size,
        env_version=env_version,
        seed_count=seed_count,
        max_count=max_count,
    )
    agent.restore(directory=str(path))
    return agent
