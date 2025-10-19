"""
Environment entry point for ReinforceNow.
"""
import inspect
from typing import Dict, Any, Optional, List
from string import Template

# Conditional imports for type hints only
try:
    from tinker_cookbook.rl.types import Env, Observation, Action, StepResult
    from tinker_cookbook.completers import StopCondition
    TINKER_AVAILABLE = True
except ImportError:
    # Fallback for environments without tinker_cookbook
    TINKER_AVAILABLE = False
    Env = object
    Observation = Any
    Action = Any
    StepResult = Any
    StopCondition = List[str]

# Global registry for environment classes
ENV_REGISTRY: Dict[str, type] = {}


class ReinforceNowEnv(Env if TINKER_AVAILABLE else object):
    """Environment for both single-turn and multi-turn RL training."""

    def __init__(self, data, renderer, reward_registry, max_turns=1, max_tokens=2048):
        self.messages_templates = data["messages"]
        self.reward_names = data["rewards"]
        self.variables = data.get("variables", {})
        self.metadata = data["metadata"]

        self.reward_fns = []
        for name in self.reward_names:
            if name not in reward_registry:
                raise ValueError(f"Reward function '{name}' not found in registry")
            self.reward_fns.append(reward_registry[name])

        self.renderer = renderer
        self.max_turns = max_turns
        self.max_tokens = max_tokens

        ctx = {**self.metadata, **self.variables}
        self.messages = []
        for msg in self.messages_templates:
            content = Template(msg["content"]).safe_substitute(ctx)
            self.messages.append({"role": msg["role"], "content": content})

    async def initial_observation(self) -> tuple:
        self.turn_count = 0

        # Calculate prompt tokens at the start
        self.prompt_tokens = sum(
            len(self.renderer.tokenizer.encode(m["content"]))
            for m in self.messages
        )

        # Use copy to avoid mutation
        self.conversation = self.messages.copy()

        observation = self.renderer.build_generation_prompt(self.conversation)
        stop = self.renderer.get_stop_sequences()  # StopCondition is just a list
        return observation, stop

    async def step(self, action: Any) -> Any:
        self.turn_count += 1

        response = self.renderer.tokenizer.decode(action)
        self.conversation.append({"role": "assistant", "content": response})
        total_reward = 0.0
        metrics = {"turn": self.turn_count}

        done = self.turn_count >= self.max_turns

        if done:
            sample = {
                "messages": self.conversation,
                "rewards": {},
                "variables": self.variables,
                "metadata": self.metadata
            }

            # validation is done previously so no value guard
            for fn, name in zip(self.reward_fns, self.reward_names):
                value = await fn(None, sample)
                sample["rewards"][name] = value

            total_reward = sum(sample["rewards"].values()) / len(sample["rewards"])

            # The FULL training sample structure (same for messages AND rolloutData)
            full_training_sample = {
                "messages": self.conversation,
                "rewards": self.reward_names,  # List of reward function names
                "variables": self.variables,   # Template variables
                "metadata": self.metadata      # Sample metadata
            }

            # Prepare trace data matching the schema
            trace_data = {
                "messages": full_training_sample,      # Full structure
                "rolloutData": full_training_sample,   # SAME structure
                "reward": total_reward,
                "rewardBreakdown": sample["rewards"],  # Dict of individual rewards
                "promptId": self.metadata.get("prompt_index", 0),
                "step": self.turn_count,
                "rolloutId": self.metadata.get("prompt_index", 0),  # Using prompt_id as rollout
                "runId": "cmgx5o3f00001l804fvgd01sr"  # Hardcoded run ID
            }

            # Metrics must be flat numeric values for averaging
            metrics = {
                "prompt_id": self.metadata.get("prompt_index", 0),
                "step": self.turn_count,
                "total_tokens": len(action),
                "completion_tokens": len(action),
                "prompt_tokens": self.prompt_tokens,
                "_trace_data": trace_data  # Special key for trace extraction
            }
            # Add individual rewards as separate metrics
            for reward_name, reward_value in sample["rewards"].items():
                metrics[f"reward_{reward_name}"] = reward_value

        observation = self.renderer.build_generation_prompt(self.conversation)
        stop = self.renderer.get_stop_sequences()  # StopCondition is just a list

        if TINKER_AVAILABLE:
            from tinker_cookbook.rl.types import StepResult
            return StepResult(
                reward=total_reward,
                episode_done=done,
                next_observation=observation,
                next_stop_condition=stop,
                metrics=metrics
            )
        else:
            # Fallback for testing without tinker
            return {
                "reward": total_reward,
                "episode_done": done,
                "next_observation": observation,
                "next_stop_condition": stop,
                "metrics": metrics
            }


class TelemetryWrapper:
    """
    Enforces ReinforceNow telemetry and validates user environments.
    Wraps custom user environments to ensure they conform to the
    ReinforceNow environment contract and provide proper telemetry.
    """

    def __init__(self, user_env: Any, renderer: Any):
        """
        Initialize the telemetry wrapper.

        Args:
            user_env: User's custom environment (must have Env-like interface)
            renderer: The renderer for the environment
        """
        self.user_env = user_env
        self.renderer = renderer
        self.turn_count = 0

        # Validate required attributes
        if not hasattr(user_env, "metadata"):
            raise AttributeError("Environment must define `self.metadata`.")
        if not getattr(user_env, "messages", None):
            raise AttributeError("Environment must define a non-empty `self.messages` list.")

    async def initial_observation(self) -> tuple:
        """
        Get initial observation from the wrapped environment.
        Adds telemetry for token counting before delegating to user env.
        """
        # Count prompt tokens if tokenizer available
        tokenizer = getattr(self.renderer, "tokenizer", None)
        self.user_env.prompt_tokens = (
            sum(len(tokenizer.encode(m["content"])) for m in self.user_env.messages if "content" in m)
            if tokenizer else 0
        )

        return await self.user_env.initial_observation()

    async def step(self, action: Any) -> Any:
        """
        Execute a step in the wrapped environment.

        Args:
            action: The action to take

        Returns:
            StepResult with added telemetry
        """
        self.turn_count += 1
        result = await self.user_env.step(action)

        # Validate messages still exist
        if not getattr(self.user_env, "messages", None):
            raise AttributeError("`self.messages` must remain defined and non-empty.")

        # Extract metadata
        metadata = getattr(self.user_env, "metadata", {})

        # Build telemetry data
        telemetry = {
            "reward_breakdown": result.metrics.get("reward_breakdown", {}) if hasattr(result, 'metrics') else {},
            "prompt_id": metadata.get("prompt_index"),
            "step": self.turn_count,
            "rollout_id": self.turn_count,
            "rollout_data": {
                "totalTokens": len(action) if hasattr(action, '__len__') else 0,
                "completion": len(action) if hasattr(action, '__len__') else 0,
                "prompt": getattr(self.user_env, "prompt_tokens", 0),
                "truncated": False,
                "sample_index": self.turn_count,
                "metadata": metadata,
            },
        }

        # Update result metrics with telemetry
        if hasattr(result, 'metrics'):
            result.metrics = telemetry

        return result


def env(cls: type = None, *, name: str = None, max_turns: int = 1, use_telemetry: bool = True) -> type:
    """
    Decorator to register environment classes with automatic telemetry wrapping.

    Usage:
        @env
        class CustomEnv(Env):
            def __init__(self, data, renderer):
                self.metadata = data["metadata"]
                self.messages = data["messages"]

            async def initial_observation(self):
                # Your logic here
                pass

            async def step(self, action):
                # Your logic here
                pass

        # The environment will be automatically wrapped with TelemetryWrapper
        # when instantiated, ensuring proper telemetry collection.
    """
    def decorator(env_class):
        if not inspect.isclass(env_class):
            raise TypeError(f"@env can only decorate classes, not {type(env_class)}")

        # Create a wrapper class that applies TelemetryWrapper automatically
        if use_telemetry:
            original_init = env_class.__init__

            def wrapped_init(self, *args, **kwargs):
                # Call original init
                original_init(self, *args, **kwargs)

            env_class.__init__ = wrapped_init

            # Mark for telemetry wrapping during instantiation
            env_class._use_telemetry = True

        # Register with class name as key (or custom name)
        registry_name = name or env_class.__name__
        ENV_REGISTRY[registry_name] = env_class

        # Add metadata
        env_class._is_env = True
        env_class._max_turns = max_turns
        env_class._registry_name = registry_name

        return env_class

    # Support both @env and @env(name="...", max_turns=5)
    if cls is None:
        return decorator
    return decorator(cls)


# Factory function to create environments with automatic telemetry wrapping
def create_env(env_class_or_name, *args, **kwargs):
    """
    Create an environment instance with automatic telemetry wrapping if needed.

    Args:
        env_class_or_name: Either an environment class or a registered name
        *args, **kwargs: Arguments to pass to the environment constructor

    Returns:
        Environment instance, wrapped with TelemetryWrapper if use_telemetry=True
    """
    # Resolve class from registry if string provided
    if isinstance(env_class_or_name, str):
        if env_class_or_name not in ENV_REGISTRY:
            raise ValueError(f"Environment '{env_class_or_name}' not found in registry")
        env_class = ENV_REGISTRY[env_class_or_name]
    else:
        env_class = env_class_or_name

    # Create the environment instance
    env_instance = env_class(*args, **kwargs)

    # Wrap with telemetry if needed
    if getattr(env_class, '_use_telemetry', False):
        # Extract renderer from args/kwargs
        renderer = kwargs.get('renderer') or (args[1] if len(args) > 1 else None)
        if renderer:
            env_instance = TelemetryWrapper(env_instance, renderer)

    return env_instance


__all__ = ['ReinforceNowEnv', 'TelemetryWrapper', 'env', 'ENV_REGISTRY', 'create_env']