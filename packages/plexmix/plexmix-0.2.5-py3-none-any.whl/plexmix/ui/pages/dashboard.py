import reflex as rx
from plexmix.ui.components.navbar import layout
from plexmix.ui.states.dashboard_state import DashboardState


def status_card(title: str, configured, link: str) -> rx.Component:
    """Create a status card showing configuration state.

    Args:
        title: The title of the card
        configured: A Reflex state variable (not a bool)
        link: The link to the configuration page
    """
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(title, size="5"),
                rx.cond(
                    configured,
                    rx.badge("Configured", color_scheme="green"),
                    rx.badge("Not Configured", color_scheme="red"),
                ),
                justify="between",
                width="100%",
            ),
            rx.cond(
                ~configured,
                rx.link(
                    rx.button("Configure", variant="soft", size="2"),
                    href=link,
                ),
                rx.box(),
            ),
            spacing="3",
            align="start",
        ),
        width="100%",
    )


def stats_card(label: str, value) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(label, size="3", color_scheme="gray"),
            rx.heading(value, size="7"),
            spacing="2",
            align="start",
        ),
        width="100%",
    )


def dashboard() -> rx.Component:
    content = rx.container(
        rx.vstack(
            rx.heading("Dashboard", size="8", margin_bottom="6"),
            rx.heading("Configuration Status", size="6", margin_bottom="3"),
            rx.grid(
                status_card(
                    "Plex Server",
                    DashboardState.plex_configured,
                    "/settings"
                ),
                status_card(
                    "AI Provider",
                    DashboardState.ai_provider_configured,
                    "/settings"
                ),
                status_card(
                    "Embeddings",
                    DashboardState.embedding_provider_configured,
                    "/settings"
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
            rx.divider(margin_y="6"),
            rx.heading("Library Statistics", size="6", margin_bottom="3"),
            rx.grid(
                stats_card("Total Tracks", DashboardState.total_tracks),
                stats_card("Embedded Tracks", DashboardState.embedded_tracks),
                stats_card("Last Sync", rx.cond(DashboardState.last_sync, DashboardState.last_sync, "Never")),
                columns="3",
                spacing="4",
                width="100%",
            ),
            rx.divider(margin_y="6"),
            rx.heading("Quick Actions", size="6", margin_bottom="3"),
            rx.hstack(
                rx.link(
                    rx.button(
                        "Generate Playlist",
                        size="3",
                        disabled=~(DashboardState.plex_configured & DashboardState.ai_provider_configured),
                    ),
                    href="/generator",
                ),
                rx.button(
                    "Sync Library",
                    size="3",
                    variant="soft",
                    on_click=DashboardState.refresh_stats,
                    disabled=~DashboardState.plex_configured,
                ),
                spacing="4",
            ),
            spacing="4",
            width="100%",
        ),
        size="4",
        on_mount=DashboardState.on_load,  # Add on_mount to trigger state initialization
    )
    return layout(content)
