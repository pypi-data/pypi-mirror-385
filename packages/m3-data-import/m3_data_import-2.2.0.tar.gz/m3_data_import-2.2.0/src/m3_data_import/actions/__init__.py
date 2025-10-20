from data_import import (
    import_file,
)
from data_import.configuration.utils import (
    dry_run,
)

from m3.actions.results import (
    OperationResult,
)
from objectpack.actions import (
    BaseAction,
    BasePack,
    BaseWindowAction,
)

from m3_data_import.ui import (
    ImportWindow,
    ResultWindow,
)
from m3_data_import.utils import (
    write_to_disc,
)


class BaseImportPack(BasePack):
    """Базовый пак иморта данных."""

    title = 'Импорт данных'
    window = ImportWindow
    result_window = ResultWindow

    SUCCESS_MESSAGE = 'Данные успешно импортированы'

    def __init__(self):
        super(BaseImportPack, self).__init__()
        self.import_window_action = ImportWindowAction()
        self.import_action = ImportAction()
        self.actions.extend((self.import_window_action, self.import_action))

    def declare_context(self, action):
        ctx = super(BaseImportPack, self).declare_context(action)
        if action is self.import_action:
            ctx['force'] = dict(type=bool, default=False)
        return ctx

    def get_default_action(self):
        """Возвращает действие по-умолчанию."""
        return self.import_window_action

    def get_import_url(self):
        """Возвращает URL действия импорта."""
        return self.import_action.get_absolute_url()

    def create_window(self, request, context):
        """Cоздание окна импорта."""
        return self.window()

    def set_window_params(self, params):
        """Установка параметров окна."""
        return params

    def get_result_window(self):
        """Cоздание окна отображения результата."""
        return self.result_window()

    def get_result_window_params(self, request, context):
        """Получение параметров окна результатов."""
        return {}

    def get_parser_params(self, request, context):
        """Получение параметров парсера."""
        return {}

    def get_loader_params(self, request, context):
        """Получение параметров загрузчика."""
        return {}

    def extend_menu(self, menu):
        """Метод, добавляющий пункт меню."""
        return menu.administry(
            menu.SubMenu(
                'Импорт',
                menu.Item(
                    self.title,
                    pack=self.get_default_action()
                )
            )
        )


class ImportPack(BaseImportPack):
    """Пак иморта данных."""

    config_cls = None

    def get_config(self, file_path=None):
        """Инстанцирование класса конфигурации."""
        return self.config_cls()

    def set_window_params(self, params):
        """Установка параметров окна."""
        params = super(ImportPack, self).set_window_params(params)
        params['extensions'] = self.config_cls.parser.extensions
        return params


class ImportWindowAction(BaseWindowAction):
    """Экшн показа окна импорта."""

    perm_code = 'import'

    def create_window(self):
        """Cоздание окна."""
        self.win = self.parent.create_window(self.request, self.context)

    def configure_window(self):
        """Конфигурирование окна."""
        self.win.save_btn.text = 'Загрузить'

    def set_window_params(self):
        """Задание параметров окна."""
        super(ImportWindowAction, self).set_window_params()
        params = self.win_params.copy()
        params['title'] = self.parent.title
        params['form_url'] = self.parent.get_import_url()
        self.win_params = self.parent.set_window_params(params)


class ImportAction(BaseAction):
    """Экшн, выполняющий импорт данных."""

    perm_code = 'import'

    def run(self, request, context):
        file_path = (
            getattr(context, 'file', None) or
            write_to_disc(request.FILES['file_uploaded'])
        )
        config = self.parent.get_config(file_path)
        parser_params = self.parent.get_parser_params(request, context)
        loader_params = self.parent.get_loader_params(request, context)

        if getattr(config, 'need_confirm', False) and not context.force:
            # Требуется подтверждение
            with dry_run(config):
                log = import_file(
                    file_path, config, parser_params, loader_params
                )
        else:
            log = import_file(
                file_path, config, parser_params, loader_params
            )

        success = not log

        result_window_params = self.parent.get_result_window_params(
            request, context
        )

        result_window_params['log'] = log or (self.parent.SUCCESS_MESSAGE, )

        if all((
            config.need_confirm, not success, not context.force
        )):
            result_window_params['show_buttons'] = True
            result_window_params['import_url'] = (
                self.parent.import_action.get_absolute_url()
            )
            result_window_params['title'] = u'Обнаружены ошибки'
            result_window_params['file'] = file_path

        result_window = self.parent.get_result_window()
        result_window.set_params(result_window_params)

        return OperationResult(
            success=True, code=result_window.get_script()
        )
