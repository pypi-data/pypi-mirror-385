from os import (
    makedirs,
    path,
)

from django.core.files.base import (
    File,
)
from django.core.files.storage import (
    default_storage,
)


def write_to_disc(file_obj):
    """Выполняет сохранение файла на диск (Django default storage)."""

    storage = default_storage
    fname = path.basename(file_obj.name)
    copy_name = storage.get_available_name(
        path.join('imports', fname)
    )

    destination = storage.path(copy_name)

    destination_dir = path.dirname(destination)
    if not path.exists(destination_dir):
        makedirs(destination_dir)

    with storage.open(destination, 'wb+') as copied:
        for chunk in File(file_obj).chunks():
            copied.write(chunk)

    return destination


def replace_action(pack, action_attr_name, new_action):
    """Замена действия в паке.

    :param pack: ActionPack
    :param basestring action_attr_name: имя атрибута действия в паке
    :param new_action: Action
    """

    if hasattr(pack, action_attr_name):
        pack.actions.remove(getattr(pack, action_attr_name))
    setattr(pack, action_attr_name, new_action)
    pack.actions.append(getattr(pack, action_attr_name))
