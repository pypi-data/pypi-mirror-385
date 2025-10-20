=======================
Подсистема импорта - UI
=======================

Интерфейсная часть подсистемы импорта

Установка пакета
================

``pip install m3-data-import``

Подключение
===========


1. Определение пака
*******************
Пак определяет класс конфигурации и дополнительные параметры импорта

**Пример:**

.. code-block:: python

    from m3_data_import.actions import ImportPack as Pack

    class ImportPack(Pack):

        title = u'Импорт учреждений'
        config_cls = ImportConfig

        def get_parser_params(self):
            params = super(ImportPack, self).get_parser_params()
            params['skip_sheets'] = ('Справочник', )
            return params

    from .dataimport import ImportPack

    def register_actions():
      """Регистрация пака в контроллере."""

      action_controller.packs.extend([
          ImportPack()
      ])


Описание класса конфигурации см. в пакете data-import

2. Массовый импорт
******************

Массовый импорт - загрузка множества файлов данных, запакованных в архив. Подсистема определяет соответствие файла и конфигурации, порядок загрузки. Для активации массового импорта необходимо:

- Подключить пак массового импорта

  .. code-block:: python

    from m3_data_import.actions.bulk import BulkImportPack
    action_controller.packs.extend((
        BulkImportPack(),
    ))

- Зарегистрировать имеющиеся конфигурации в реестре конфигураций:

  .. code-block:: python

    from unit.dataimport import UnitConfig
    from group.dataimport import GroupConfig

    data_import.configuration.registry = Registry(
      (UnitConfig, GroupConfig)
    )

  **Порядок классов в кортеже определяет приоритет загрузки!**

Тесты
=====

Запуск тестов осуществляется через `tox <https://tox.readthedocs.io/en/latest/>`_
