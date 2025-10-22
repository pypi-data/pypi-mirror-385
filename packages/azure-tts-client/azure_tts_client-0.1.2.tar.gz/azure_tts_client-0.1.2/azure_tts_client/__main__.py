import os
import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, TextArea, Button, Select, Static, Label, Input, OptionList
from textual.widgets.option_list import Option
from textual.binding import Binding
from textual.screen import ModalScreen
import azure.cognitiveservices.speech as speechsdk
import tkinter as tk
from tkinter import filedialog
from . import __version__


class ThemeSwitcherScreen(ModalScreen):
    """Modal screen for theme selection."""

    CSS = """
    ThemeSwitcherScreen {
        align: center middle;
    }

    #theme-dialog {
        width: 50;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #theme-title {
        width: 100%;
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    #theme-list {
        width: 100%;
        height: auto;
        max-height: 15;
        margin-bottom: 1;
    }
    """

    THEMES = [
        "textual-dark",
        "textual-light",
        "gruvbox",
        "nord",
        "monokai",
        "dracula",
        "catppuccin-mocha",
        "tokyo-night",
    ]

    def compose(self) -> ComposeResult:
        with Container(id="theme-dialog"):
            yield Static("Choose Theme", id="theme-title")
            yield OptionList(
                *[Option(theme) for theme in self.THEMES],
                id="theme-list"
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle theme selection."""
        self.dismiss(str(event.option.prompt))


class ApiKeyInputScreen(ModalScreen):
    """Modal screen for API key input."""

    CSS = """
    ApiKeyInputScreen {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #dialog-title {
        width: 100%;
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    #dialog-message {
        width: 100%;
        margin-bottom: 1;
    }

    #api-key-input {
        width: 100%;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #button-container Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Azure Speech API Key Required", id="dialog-title")
            yield Static(
                "Please enter your Azure Speech API key.\nIt will be saved to ~/.azure_tts_client",
                id="dialog-message"
            )
            yield Input(
                placeholder="Enter your API key here...",
                password=True,
                id="api-key-input"
            )
            with Horizontal(id="button-container"):
                yield Button("Save", variant="primary", id="save-key-btn")
                yield Button("Cancel", variant="default", id="cancel-key-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-key-btn":
            input_widget = self.query_one("#api-key-input", Input)
            api_key = input_widget.value.strip()
            if api_key:
                self.dismiss(api_key)
            else:
                input_widget.placeholder = "API key cannot be empty!"
        elif event.button.id == "cancel-key-btn":
            self.app.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        api_key = event.value.strip()
        if api_key:
            self.dismiss(api_key)


class TTSClient(App):
    """Azure TTS Terminal Client"""

    CSS = """
    #header-bar {
        dock: top;
        height: 1;
        background: $panel;
        padding: 0 2;
    }

    #header-title {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
    }

    #version-label {
        width: auto;
        content-align: right middle;
        color: $text-muted;
        text-style: dim;
    }

    #main-container {
        height: 100%;
        padding: 1 2;
    }

    #text-input-container {
        height: 1fr;
        border: solid $primary;
        margin-bottom: 1;
    }

    #text-input-container Label {
        padding: 0 1;
        text-style: bold;
    }

    #text-input {
        height: 100%;
    }

    #controls-container {
        height: auto;
        margin-bottom: 1;
    }

    #controls-row {
        height: auto;
        align: center middle;
    }

    #voice-select {
        width: 1fr;
        min-width: 20;
        margin-right: 1;
    }

    Button {
        margin: 0;
        margin-left: 1;
        min-width: 8;
        width: auto;
    }

    #status-container {
        height: auto;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }

    #log-container {
        height: 10;
        border: solid $secondary;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+d", "quit", "Quit", show=False),
        Binding("ctrl+t", "switch_theme", "Theme", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.speech_config = None
        self.synthesizer = None
        self.is_playing = False
        self.config_file = Path.home() / ".azure_tts_client"

        # Available voices (common ones)
        self.voices = [
            ("en-US-JennyNeural", "English (US) - Jenny (Female)"),
            ("en-US-GuyNeural", "English (US) - Guy (Male)"),
            ("en-US-AriaNeural", "English (US) - Aria (Female)"),
            ("en-GB-SoniaNeural", "English (UK) - Sonia (Female)"),
            ("en-GB-RyanNeural", "English (UK) - Ryan (Male)"),
            ("fr-FR-DeniseNeural", "French - Denise (Female)"),
            ("de-DE-KatjaNeural", "German - Katja (Female)"),
            ("es-ES-ElviraNeural", "Spanish - Elvira (Female)"),
            ("zh-CN-XiaoxiaoNeural", "Chinese - Xiaoxiao (Female)"),
        ]

        # Load saved theme
        self._load_theme()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Horizontal(id="header-bar"):
            yield Static("Azure TTS Client", id="header-title")
            yield Static(f"v{__version__}", id="version-label")

        with Container(id="main-container"):
            # Text input area
            with Vertical(id="text-input-container"):
                yield Label("Text to speak:")
                yield TextArea(
                    id="text-input",
                    text="Hello! This is Azure Text-to-Speech. Type your text here and press Play.",
                )

            # Controls
            with Vertical(id="controls-container"):
                with Horizontal(id="controls-row"):
                    yield Select(
                        [(label, value) for value, label in self.voices],
                        id="voice-select",
                        prompt="Select Voice",
                        value=self._load_voice()
                    )
                    yield Button("Play", id="play-btn", variant="primary")
                    yield Button("Clear Text", id="clear-btn", variant="warning")
                    yield Button("Save", id="save-btn", variant="success")

            # Status
            with Vertical(id="status-container"):
                yield Static("Ready", id="status-text")

            # Log
            with Vertical(id="log-container"):
                yield Static("📋 Log:\n> Initializing...", id="log-text")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize Azure Speech SDK on app start."""
        self.run_worker(self.initialize_azure())

    async def initialize_azure(self) -> None:
        """Set up Azure Speech configuration."""
        try:
            # Try to read from config file
            config_file = self.config_file

            if not config_file.exists():
                self.log_message(f"⚠ Config file not found at {config_file}", "warning")
                self.update_status("Waiting for API key input...", "warning")

                # Prompt user for API key
                api_key = await self.push_screen_wait(ApiKeyInputScreen())

                if not api_key:
                    self.log_message("⚠ API key input cancelled", "error")
                    self.update_status("Error: No API key provided", "error")
                    return

                # Save API key to file
                try:
                    config_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(config_file, 'w') as f:
                        f.write(f"SPEECH_KEY={api_key}\n")
                    os.chmod(config_file, 0o600)  # Set secure permissions
                    self.log_message(f"✓ API key saved to {config_file}", "success")
                except Exception as e:
                    self.log_message(f"⚠ Failed to save config: {str(e)}", "error")
                    self.log_message(f"⚠ Path attempted: {config_file}", "error")
                    self.update_status("Error: Could not save config", "error")
                    return

                speech_key = api_key
            else:
                # Read config file
                speech_key = None

                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('SPEECH_KEY='):
                            speech_key = line.split('=', 1)[1].strip('"').strip("'")

                if not speech_key:
                    self.log_message("⚠ SPEECH_KEY not found in config file", "warning")
                    self.update_status("Waiting for API key input...", "warning")

                    # Prompt user for API key
                    api_key = await self.push_screen_wait(ApiKeyInputScreen())

                    if not api_key:
                        self.log_message("⚠ API key input cancelled", "error")
                        self.update_status("Error: No API key provided", "error")
                        return

                    # Save API key to file
                    try:
                        config_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(config_file, 'w') as f:
                            f.write(f"SPEECH_KEY={api_key}\n")
                        os.chmod(config_file, 0o600)  # Set secure permissions
                        self.log_message(f"✓ API key saved to {config_file}", "success")
                    except Exception as e:
                        self.log_message(f"⚠ Failed to save config: {str(e)}", "error")
                        self.log_message(f"⚠ Path attempted: {config_file}", "error")
                        self.update_status("Error: Could not save config", "error")
                        return

                    speech_key = api_key

            # Hardcoded endpoint
            endpoint = "https://eastus.api.cognitive.microsoft.com/"

            # Create speech config with endpoint
            self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=endpoint)
            self.speech_config.speech_synthesis_voice_name = self.voices[0][0]

            # Use default speaker
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            self.synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            self.log_message("✓ Azure TTS initialized successfully", "success")
            self.update_status("Ready to synthesize speech")

        except Exception as e:
            self.log_message(f"⚠ Initialization error: {str(e)}", "error")
            self.update_status(f"Error: {str(e)}", "error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "play-btn":
            self.action_play()
        elif event.button.id == "save-btn":
            self.save_audio()
        elif event.button.id == "clear-btn":
            self.action_clear()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle voice selection change."""
        if event.select.id == "voice-select" and self.speech_config:
            voice = event.value
            self.speech_config.speech_synthesis_voice_name = voice

            # Recreate synthesizer with new voice
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            self.synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Save the voice selection
            self._save_voice(voice)

            self.log_message(f"🎤 Voice changed to: {voice}", "success")

    def action_play(self) -> None:
        """Play TTS from text input."""
        if not self.synthesizer:
            self.log_message("⚠ Azure TTS not initialized", "error")
            return

        text_area = self.query_one("#text-input", TextArea)
        text = text_area.text.strip()

        if not text:
            self.log_message("⚠ Please enter some text", "warning")
            return

        self.is_playing = True
        self.update_status("🔊 Synthesizing speech...", "success")
        self.log_message(f"▶ Playing: {text[:50]}...", "success")

        # Run synthesis in background
        asyncio.create_task(self.synthesize_speech(text))

    async def synthesize_speech(self, text: str) -> None:
        """Synthesize speech asynchronously."""
        try:
            # Run synthesis in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.synthesizer.speak_text_async(text).get
            )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.log_message("✓ Speech synthesis completed", "success")
                self.update_status("Ready")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                self.log_message(f"⚠ Synthesis canceled: {cancellation.reason}", "error")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    self.log_message(f"⚠ Error details: {cancellation.error_details}", "error")
                self.update_status("Error occurred", "error")

        except Exception as e:
            self.log_message(f"⚠ Synthesis error: {str(e)}", "error")
            self.update_status(f"Error: {str(e)}", "error")
        finally:
            self.is_playing = False

    def action_clear(self) -> None:
        """Clear text input area."""
        text_area = self.query_one("#text-input", TextArea)
        text_area.clear()
        self.log_message("🗑 Text area cleared", "success")
        self.update_status("Ready")

    def save_audio(self) -> None:
        """Save audio to file."""
        if not self.synthesizer:
            self.log_message("⚠ Azure TTS not initialized", "error")
            return

        text_area = self.query_one("#text-input", TextArea)
        text = text_area.text.strip()

        if not text:
            self.log_message("⚠ Please enter some text", "warning")
            return

        # Create a hidden tkinter window for the file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring dialog to front

        # Open file save dialog
        output_file = filedialog.asksaveasfilename(
            title="Save audio file",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile="output.wav"
        )

        root.destroy()  # Clean up tkinter window

        if not output_file:
            self.log_message("⚠ Save cancelled", "warning")
            return

        self.log_message(f"💾 Saving audio to {output_file}...", "success")
        asyncio.create_task(self.save_audio_async(text, output_file))

    async def save_audio_async(self, text: str, filename: str) -> None:
        """Save audio file asynchronously."""
        try:
            # Create new synthesizer with file output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
            file_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                file_synthesizer.speak_text_async(text).get
            )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.log_message(f"✓ Audio saved to {filename}", "success")
            else:
                self.log_message(f"⚠ Failed to save audio", "error")

        except Exception as e:
            self.log_message(f"⚠ Save error: {str(e)}", "error")

    def update_status(self, message: str, style: str = "") -> None:
        """Update status display."""
        status = self.query_one("#status-text", Static)
        if style:
            status.update(f"[{style}]{message}[/{style}]")
        else:
            status.update(message)

    def log_message(self, message: str, style: str = "") -> None:
        """Add message to log."""
        log = self.query_one("#log-text", Static)

        if style:
            new_line = f"[{style}]{message}[/{style}]"
        else:
            new_line = message

        # Keep last 8 lines
        current_text = str(log.render())
        lines = current_text.split('\n')
        lines.append(new_line)
        lines = lines[-8:]

        log.update('\n'.join(lines))

    def action_switch_theme(self) -> None:
        """Show theme switcher dialog."""
        self.push_screen(ThemeSwitcherScreen(), callback=self._handle_theme_change)

    def _handle_theme_change(self, theme: str | None) -> None:
        """Handle theme change callback."""
        if theme:
            self.theme = theme
            self._save_theme(theme)
            self.log_message(f"🎨 Theme changed to: {theme}", "success")

    def _load_theme(self) -> None:
        """Load saved theme from config file."""
        # Set default theme first
        self.theme = "gruvbox"

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('THEME='):
                            saved_theme = line.split('=', 1)[1].strip('"').strip("'")
                            if saved_theme:
                                self.theme = saved_theme
                            break
            except Exception:
                pass  # Use default theme if reading fails

    def _load_voice(self) -> str:
        """Load saved voice from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('VOICE='):
                            saved_voice = line.split('=', 1)[1].strip('"').strip("'")
                            if saved_voice:
                                return saved_voice
            except Exception:
                pass
        return self.voices[0][0]  # Return default voice

    def _save_voice(self, voice: str) -> None:
        """Save voice to config file."""
        try:
            # Read existing config
            config_lines = []
            voice_found = False

            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('VOICE='):
                            config_lines.append(f'VOICE={voice}\n')
                            voice_found = True
                        else:
                            config_lines.append(line)

            # Add voice if not found
            if not voice_found:
                config_lines.append(f'VOICE={voice}\n')

            # Write back
            with open(self.config_file, 'w') as f:
                f.writelines(config_lines)

            os.chmod(self.config_file, 0o600)
        except Exception as e:
            self.log_message(f"⚠ Failed to save voice: {str(e)}", "warning")

    def _save_theme(self, theme: str) -> None:
        """Save theme to config file."""
        try:
            # Read existing config
            config_lines = []
            theme_found = False

            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('THEME='):
                            config_lines.append(f'THEME={theme}\n')
                            theme_found = True
                        else:
                            config_lines.append(line)

            # Add theme if not found
            if not theme_found:
                config_lines.append(f'THEME={theme}\n')

            # Write back
            with open(self.config_file, 'w') as f:
                f.writelines(config_lines)

            os.chmod(self.config_file, 0o600)
        except Exception as e:
            self.log_message(f"⚠ Failed to save theme: {str(e)}", "warning")


def main():
    """Run the TTS client application."""
    app = TTSClient()
    app.run()


if __name__ == "__main__":
    main()
