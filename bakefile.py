from bake import *

@task()
def buildpkg(runtime):
    Path('dist').rmtree(True)
    runtime.shell('python setup.py sdist bdist_wheel')
    Path('build').rmtree()
    Path('scheme.egg-info').rmtree()

@task()
def buildhtml(runtime):
    runtime.execute('sphinx.html', sourcedir='docs')

@task()
def clean(runtime):
    for target in ('build', 'cover', 'dist', 'scheme.egg-info'):
        Path(target).rmtree(True)

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
