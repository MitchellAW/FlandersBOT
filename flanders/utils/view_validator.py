import discord


def get_view_as[TView: discord.ui.View | discord.ui.LayoutView](
    view: discord.ui.View | discord.ui.LayoutView | None,
    view_type: type[TView],
) -> TView:
    if view is None or not isinstance(view, view_type):
        msg = f"Expected view to be a {view_type.__name__} but got {type(view).__name__}"
        raise ValueError(msg)

    return view
