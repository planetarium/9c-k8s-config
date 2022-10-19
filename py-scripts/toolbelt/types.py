from typing import Literal, List, Tuple, Optional

Env = Literal["test", "production"]
Network = Literal["main", "internal", "preview", "test"]

# repo title, tag, commit sha
RepoInfos = List[Tuple[str, Optional[str], str]]
