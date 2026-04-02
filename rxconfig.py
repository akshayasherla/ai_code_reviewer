import reflex as rx

config = rx.Config(
    app_name="AI_CODE_REVIEWER",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)