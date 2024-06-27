"""Automatization of building project."""
import glob
import shutil

from doit.task import clean_targets


DOIT_CONFIG = {'default_tasks': ['test', 'sdist', 'wheel', 'rm_db']}


def task_gen_pot():
    """Generate .pot template."""
    return {
            'actions': ['pybabel extract finchecker -o i18n/client.pot'],
            'file_dep': glob.glob('finchecker/client/*.py'),
            'targets': ['i18n/client.pot'],
            'doc': 'Create/re-create ".pot" patterns.',
            'clean': [clean_targets],
    }


def task_upd_po():
    """Generate .po file."""
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -l ru_RU.UTF-8\
                        -i i18n/client.pot -D gui -d i18n/po'],
            'file_dep': ['i18n/client.pot'],
            'targets': ['i18n/po/ru_RU.UTF-8/LC_MESSAGES/gui.po'],
            'doc': 'Update translation',
    }


def task_gen_mo():
    """Generate .mo file."""
    return {
            'actions': ['mkdir -p finchecker/po/ru_RU.UTF-8/LC_MESSAGES/',
                        'pybabel compile -l ru_RU.UTF-8 -i i18n/po/ru_RU.UTF-8/LC_MESSAGES/gui.po -D gui -d finchecker/po'],
            'file_dep': ['i18n/po/ru_RU.UTF-8/LC_MESSAGES/gui.po'],
            'targets': ['finchecker/po/ru_RU.UTF-8/LC_MESSAGES/gui.mo'],
            'doc': 'compile translations',
            'clean': [clean_targets],
    }


def task_rm_db():
    """Remove generated files."""
    return {
            'actions': ['rm .*.db'],
            'doc': 'Remove "doit" db.',
    }


def task_i18n():
    """Update translation of project."""
    return {
            'actions': None,
            'task_dep': ['gen_pot', 'upd_po', 'gen_mo'],
            'doc': 'Generate translation.',
    }


def task_gen_html():
    """Generate html documentation."""
    return {
            'actions': ['sphinx-build -M html ./docs/source ./finchecker/docs/build'],
            'file_dep': glob.glob('docs/source/*.rst') + glob.glob('finchecker/*/*.py'),
            'targets': ['finchecker/docs/build'],
            'clean': [(shutil.rmtree, ["finchecker/docs/build"])],
    }


def task_test():
    """Run tests."""
    return {
            'actions': ['python3 -m unittest server_test.py'],
            'task_dep': ['i18n'],
            'doc': 'Test client and server.',
    }


def task_del_uncommited():
    """Delete uncommited files."""
    return {
            'actions': ['git clean -xdf'],
            'doc': 'Clean uncommited files',
            }


def task_sdist():
    """Build project."""
    return {
            'actions': ['python3 -m build -s -n'],
            'task_dep': ['del_uncommited'],
            'doc': 'Generate source distribution',
            }


def task_wheel():
    """Create wheel."""
    return {
            'actions': ['python3 -m build -w'],
            'task_dep': ['i18n', 'gen_html'],
            'doc': 'Generate wheel',
            }