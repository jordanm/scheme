from bake import *

@task()
def buildhtml(runtime):
    runtime.execute('sphinx.html', sourcedir='docs')

@task()
def runtests(runtime):
    try:
        import coverage
    except ImportError:
        coverage = None

    cmdline = ['nosetests']
    if coverage:
        cmdline.extend(['--with-coverage', '--cover-html', '--cover-erase',
            '--cover-package=scheme'])

    runtime.shell(cmdline, passthrough=True)
