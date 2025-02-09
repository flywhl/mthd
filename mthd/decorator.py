from functools import wraps
from typing import Callable, Optional, cast

from pydantic import BaseModel
from rich.console import Console
from rich.padding import Padding

from mthd.domain.commit import CommitMessage, StageStrategy
from mthd.error import MthdError


def commit(
    fn: Optional[Callable] = None,
    hypers: str = "hypers",
    strategy: StageStrategy = StageStrategy.ALL,
) -> Callable:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # di = DI()
            hyperparameters = cast(BaseModel, kwargs.get(hypers, None))
            if not hyperparameters:
                raise MthdError(
                    "Hyperparameters must be provided in the function call."
                )
            # git_service = di[GitService]
            # codebase_service = di[CodebaseService]

            # Generate commit message
            commit_msg = CommitMessage(
                summary="exp: foo bar baz",
                hyperparameters=hyperparameters.model_dump(),
                # annotations=codebase_service.get_all_annotations(),
            )
            # print(hyperparameters.model_dump_json(indent=2))
            # print(commit_msg.format())

            # Run experiment
            result = func(*args, **kwargs)

            # Commit changes
            console = Console()
            console.print("Generating commit with message:\n")
            console.print(
                Padding(commit_msg.format(), pad=(0, 0, 0, 4))
            )  # Indent by 4 spaces.
            # if git_service.should_commit(strategy):
            #     git_service.stage_and_commit(commit_msg)

            return result

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


if __name__ == "__main__":

    class Hyperparameters(BaseModel):
        a: int
        b: float
        c: str

    @commit(hypers="hypers")
    def test(hypers: Hyperparameters):
        print("<Experiment goes here>\n")

    test(hypers=Hyperparameters(a=1, b=2.0, c="3"))
