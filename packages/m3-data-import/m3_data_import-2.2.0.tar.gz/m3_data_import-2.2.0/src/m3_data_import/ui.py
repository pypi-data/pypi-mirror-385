from django.utils.safestring import (
    mark_safe,
)

from m3_ext.ui.controls.buttons import (
    ExtButton,
)
from m3_ext.ui.fields.complex import (
    ExtFileUploadField,
)
from objectpack.ui import (
    BaseEditWindow,
    BaseWindow,
)


class ImportWindow(BaseEditWindow):
    """Базовое окно загрузки шаблона импорта."""

    def _init_components(self):
        super(ImportWindow, self)._init_components()
        self.file_field = ExtFileUploadField(
            anchor='100%', allow_blank=False,
            name='uploaded', label="Файл для загрузки",
        )

    def _do_layout(self):
        super(ImportWindow, self)._do_layout()
        self.form.items.append(self.file_field)

    def set_params(self, params):
        super(ImportWindow, self).set_params(params)
        self.height = 110

        self.form.file_upload = True
        self.save_btn.text = 'Загрузить'
        if params.get('extensions'):
            self.file_field.possible_file_extensions = params['extensions']


class ResultWindow(BaseWindow):
    """Окно отображения результатов импорта."""

    def _init_components(self):
        super(ResultWindow, self)._init_components()
        self.force_load_btn = ExtButton(
            text=u'Загрузить данные, не содержащие ошибок',
            handler='forceLoad'
        )
        self.close_btn = ExtButton(
            text=u'Отмена', handler=u'closeWindow'
        )

    def _do_layout(self):
        super(ResultWindow, self)._do_layout()
        self.buttons.extend((
            self.force_load_btn, self.close_btn
        ))

    def set_params(self, params):
        super(ResultWindow, self).set_params(params)
        self.params = params
        self.template_globals = 'data-import-result-window.js'

        self.title = params.get('title', 'Отчет')
        self.modal = True
        self.width = 800

        self.force_load_btn.hidden = self.close_btn.hidden = (
            not params.get('show_buttons', False)
        )

        self.html = mark_safe('<br/>'.join(params['log']))
