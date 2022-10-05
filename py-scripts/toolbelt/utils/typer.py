import typer


def version_validation(ctx: typer.Context, p: typer.CallbackParam, v: str):
    if ctx.resilient_parsing:
        return
    if len(v) != 7 or not v.startswith("v"):
        raise typer.BadParameter("APV version (e.g. v100086)")
    return v


version_arg = typer.Argument(
    ..., help="RC version ie. v100260", callback=version_validation
)
apv_arg = typer.Argument(..., help="APV version ie. 1085/123...")
