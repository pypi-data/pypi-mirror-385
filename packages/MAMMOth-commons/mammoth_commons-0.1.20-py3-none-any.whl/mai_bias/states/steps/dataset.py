from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QThread, Signal, QMutex
from mai_bias.backend.loaders import registry
import traceback
from mai_bias.states.step import Step, save_all_runs
from mammoth_commons import integration_callback


global items


class DatasetLoaderThread(QThread):
    finished_success = Signal(object)
    finished_failure = Signal(str)
    canceled = Signal()
    notify = Signal(str)

    def __init__(self, pipeline):
        super().__init__()
        self.setTerminationEnabled(True)
        self.pipeline = pipeline
        self._is_canceled = False
        self.mutex = QMutex()
        integration_callback.register_progress_callback(self.progress_callback)

    def progress_callback(self, progress, message):
        progress = min(1, max(progress, 0))
        progress_blocks = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
        full_blocks = int(progress * 40)
        partial_block_index = int((progress * 40 - full_blocks) * len(progress_blocks))
        bar = "█" * full_blocks
        if full_blocks < 40:
            bar += progress_blocks[partial_block_index]
        bar += "&nbsp;" * (40 - len(bar))
        self.mutex.lock()
        self.notify.emit(
            "<span style='color: blue; background: lightgray; font-family: monospace;'>"
            + bar
            + "</span><br>"
            + message
        )
        self.mutex.unlock()

    def run(self):
        try:
            self.mutex.lock()
            if self._is_canceled:
                self.mutex.unlock()
                self.canceled.emit()
                return
            self.mutex.unlock()

            self.pipeline["dataset"]["return"] = registry.name_to_runnable[
                self.pipeline["dataset"]["module"]
            ](**self.pipeline["dataset"]["params"])

            self.mutex.lock()
            if self._is_canceled:
                self.mutex.unlock()
                self.canceled.emit()
                return
            self.mutex.unlock()

            self.finished_success.emit(self.pipeline)
        except Exception as e:
            traceback.print_exception(e)
            if not self._is_canceled:
                self.pipeline["status"] = "failed"
                traceback.print_exception(e)
                self.finished_failure.emit(str(e))
            else:
                self.mutex.lock()
                if self._is_canceled:
                    self.mutex.unlock()
                    self.canceled.emit()
                    return
                self.mutex.unlock()

    def cancel(self):
        self.mutex.lock()
        self._is_canceled = True
        self.mutex.unlock()
        self.terminate()


class SelectDataset(Step):
    def next(self):
        self.save("dataset")
        save_all_runs("history.json", self.dataset)

        self.loading_message = QMessageBox(self)
        self.loading_message.setWindowTitle("Loading Dataset")
        self.loading_message.setText("Please wait while the dataset is loading...")
        self.loading_message.setStandardButtons(QMessageBox.StandardButton.Cancel)
        self.loading_message.setModal(True)
        self.loading_message.button(QMessageBox.StandardButton.Cancel).clicked.connect(
            self.cancel_loading
        )
        self.loading_message.show()

        self.thread = DatasetLoaderThread(self.runs[-1])
        self.thread.finished_success.connect(self.on_success)
        self.thread.finished_failure.connect(self.on_failure)
        self.thread.canceled.connect(self.on_cancel)
        self.thread.notify.connect(self.on_notify)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_success(self, pipeline):
        self.loading_message.done(0)
        self.stacked_widget.slideToWidget(2)

    def on_failure(self, error_message):
        self.loading_message.done(0)
        self.show_error_message(error_message)

    def on_cancel(self):
        self.loading_message.done(0)

    def on_notify(self, message):
        self.loading_message.setText(message)

    def cancel_loading(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.cancel()
            self.loading_message.done(0)

    def showEvent(self, event):
        self.description_input.setText(self.runs[-1]["description"])
        self.dataset_selector.clear()
        self.dataset_selector.addItems(
            ["Select a dataset loader"] + list(self.dataset_loaders.keys())
        )
        self.defaults = self.runs[-1].get("dataset", dict()).get("params", dict())
        # self.update_param_form(self.runs[-1].get("dataset", dict()).get("module", "Select a dataset loader"))
        self.dataset_selector.setCurrentIndex(
            self.dataset_selector.findText(
                self.runs[-1]
                .get("dataset", dict())
                .get("module", "Select a dataset loader")
            )
        )
        super().showEvent(event)

    def switch_to_dashboard(self):
        self.save("dataset")
        self.runs[-1]["status"] = "saved"
        self.stacked_widget.slideToWidget(0)
        save_all_runs("history.json", self.dataset)

    def closeEvent(self, event):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.cancel()
            self.thread.wait()  # Ensure the thread has finished
        event.accept()
