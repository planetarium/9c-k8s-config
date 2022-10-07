def build_download_url(
    base_url: str,
    env: str,
    apv_version: int,
    project: str,
    commit: str,
    file_name: str,
):
    return "/".join(
        [base_url, env, f"v{apv_version}", project, commit, file_name]
    )
