from m3.actions.results import (
    OperationResult,
)
from objectpack.actions import (
    BaseAction,
)

from m3_data_import.actions import (
    BaseImportPack,
)
from m3_data_import.utils import (
    replace_action,
    write_to_disc,
)


class AbstractBulkImportPack(BaseImportPack):
    """Пак массового импорта."""

    title = 'Массовый импорт'
    extensions_allowed = ('zip', )
    task_cls = None

    def get_task(self):
        assert self.task_cls, type(self.task_cls)
        return self.task_cls()

    def __init__(self):
        super(AbstractBulkImportPack, self).__init__()
        replace_action(self, 'import_action', BulkImportAction())

    def set_window_params(self, params):
        """Установка параметров окна."""
        params = super(AbstractBulkImportPack, self).set_window_params(params)
        params['extensions'] = self.extensions_allowed
        return params


class BulkImportAction(BaseAction):
    """Экшн, запускающий задачу массового импорта данных."""

    task_applied_msg = (
        'Задача массового импорта поставлена в очередь. '
        'Результат выполнения будет доступен в реестре фоновых задач.'
    )

    def run(self, request, context):
        file_path = write_to_disc(request.FILES['file_uploaded'])

        args = ()
        kwargs = {'file_path': file_path}
        self.parent.get_task().apply_async(args, kwargs)

        return OperationResult(
            message=self.task_applied_msg
        )
