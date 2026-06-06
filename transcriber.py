from tempfile import NamedTemporaryFile

import gigaam # type: ignore[import-untyped]

class TranscriberError(Exception):
    pass

class Transcriber:
    def __init__(self, model_name: str = "v3_e2e_rnnt"):
        self.model = gigaam.load_model(model_name)
        print("Using device:", self.model._device) # pyright: ignore[reportPrivateUsage]

    def transcribe(self, buffer: bytes) -> str:
        with NamedTemporaryFile(delete_on_close=False) as file:
            file.write(buffer)
            file.close()

            try:
                return self.model.transcribe_longform(file.name).text # type: ignore[no-any-return]
            except RuntimeError as err:
                if str(err) == "Failed to load audio":
                    raise TranscriberError("Не удалось загрузить аудио") from err
                else:
                    raise
