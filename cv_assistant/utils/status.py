from rich.progress import (
        Progress,
        TimeElapsedColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
    )


def get_progress_bar():

    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        "[yellow]({task.completed}/{task.total})",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )


