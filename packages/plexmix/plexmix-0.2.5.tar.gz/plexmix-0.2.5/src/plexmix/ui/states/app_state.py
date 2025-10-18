import reflex as rx
from pathlib import Path
from typing import Optional


class AppState(rx.State):
    plex_configured: bool = False
    ai_provider_configured: bool = False
    embedding_provider_configured: bool = False

    total_tracks: str = "0"
    embedded_tracks: str = "0"
    last_sync: Optional[str] = None

    current_task: Optional[str] = None
    task_progress: int = 0

    @rx.event
    def on_load(self):
        """Load app data when the page loads."""
        print("AppState.on_load called")
        self.check_configuration_status()
        self.load_library_stats()
        return rx.console_log("App state loaded")

    def check_configuration_status(self):
        try:
            from plexmix.config.settings import Settings
            from plexmix.config.credentials import get_plex_token, get_google_api_key, get_openai_api_key, get_anthropic_api_key, get_cohere_api_key
            import os

            settings = Settings.load_from_file()

            # Check Plex configuration
            plex_token = get_plex_token()
            print(f"Plex URL: {settings.plex.url}, Token: {bool(plex_token)}, Library: {settings.plex.library_name}")
            self.plex_configured = bool(
                settings.plex.url and
                plex_token and
                settings.plex.library_name
            )

            # Check AI provider configuration
            # Check both the credentials module and environment variables
            ai_configured = False

            # Check Google API key
            google_key = get_google_api_key()
            if not google_key:
                google_key = os.environ.get("GOOGLE_API_KEY")

            # Check OpenAI API key
            openai_key = get_openai_api_key()
            if not openai_key:
                openai_key = os.environ.get("OPENAI_API_KEY")

            # Check Anthropic API key
            anthropic_key = get_anthropic_api_key()
            if not anthropic_key:
                anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

            # Check Cohere API key
            cohere_key = get_cohere_api_key()
            if not cohere_key:
                cohere_key = os.environ.get("COHERE_API_KEY")

            ai_keys = [google_key, openai_key, anthropic_key, cohere_key]
            self.ai_provider_configured = any(ai_keys)

            # Check embedding provider configuration
            embedding_keys = [google_key, openai_key, cohere_key]
            self.embedding_provider_configured = any(embedding_keys) or settings.embedding.default_provider == "local"

        except Exception as e:
            print(f"Error checking configuration: {e}")
            self.plex_configured = False
            self.ai_provider_configured = False
            self.embedding_provider_configured = False

    def load_library_stats(self):
        try:
            from plexmix.config.settings import Settings
            settings = Settings.load_from_file()
            db_path = settings.database.get_db_path()

            if not db_path.exists():
                self.total_tracks = "0"
                self.embedded_tracks = "0"
                self.last_sync = None
                return

            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM tracks")
            self.total_tracks = str(cursor.fetchone()[0])

            # Count embedded tracks from the embeddings metadata
            import pickle
            from pathlib import Path
            # Use the FAISS index path with .metadata extension
            faiss_path = Path(settings.database.faiss_index_path).expanduser()
            metadata_path = faiss_path.with_suffix('.metadata')
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.embedded_tracks = str(len(metadata.get('track_ids', [])))
            else:
                self.embedded_tracks = "0"

            # Use last_played as a proxy for last sync since updated_at doesn't exist
            cursor.execute("SELECT MAX(last_played) FROM tracks")
            last_update = cursor.fetchone()[0]
            self.last_sync = last_update if last_update else None

            conn.close()

        except Exception as e:
            print(f"Error loading library stats: {e}")
            self.total_tracks = "0"
            self.embedded_tracks = "0"
            self.last_sync = None
