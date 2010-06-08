# -*- python -*-
VERSION = '2.31.4'
APPNAME = 'hamster-applet'
top = '.'
out = 'build'

import intltool, gnome

def configure(conf):
    conf.check_tool('python')
    conf.check_tool('misc')
    conf.check_python_version((2,4,2))

    conf.check_tool('gnome intltool dbus')

    conf.define('ENABLE_NLS', 1)


    conf.define('HAVE_BIND_TEXTDOMAIN_CODESET', 1)

    conf.define('VERSION', VERSION)
    conf.define('GETTEXT_PACKAGE', "hamster-applet")
    conf.define('PACKAGE', "hamster-applet")
    conf.define('PYEXECDIR', conf.env["PYTHONDIR"]) # i don't know the difference
    conf.define('prefix', conf.env["PREFIX"]) # to keep compatibility for now


    conf.sub_config("help")

def build(bld):
    bld.install_files('${LIBDIR}/hamster-applet', 'src/hamster-applet', chmod = 0755)
    bld.install_files('${BINDIR}',
                      """src/hamster-standalone
                         src/hamster-client
                         src/hamster-service""",
                      chmod = 0755)
    bld.symlink_as('${BINDIR}/gnome-time-tracker', 'hamster-standalone')


    # set correct flags in defs.py
    bld.new_task_gen("subst",
                     source= "src/hamster/defs.py.in",
                     target= "src/hamster/defs.py",
                     install_path="${PYTHONDIR}/hamster",
                     dict = bld.env
                    )

    bld.install_files('${PYTHONDIR}/hamster', 'src/hamster/*.py')
    bld.install_files('${PYTHONDIR}/hamster/widgets', 'src/hamster/widgets/*.py')

    bld.new_task_gen("subst",
                     source= "org.gnome.hamster.service.in",
                     target= "org.gnome.hamster.service",
                     install_path="${DATADIR}/dbus-1/services",
                     dict = bld.env
                    )

    bld.add_subdirs("po help data")


    def post(ctx):
        # Postinstall tasks:
        # gnome.postinstall_scrollkeeper('hamster-applet') # Installing the user docs
        gnome.postinstall_schemas('hamster-applet') # Installing GConf schemas
        gnome.postinstall_icons() # Updating the icon cache

    bld.add_post_fun(post)


def copy_help(ctx):
    import os
    os.system('cp -R build/default/help/ .')

def push_release(ctx):
    """copies generated page files to sources so that they are packaged on dist
       then creates the tarball and pushes to git master
       TODO - this should depend and fail if distcheck fails. also it looks
              suspiciously non-native
    """
    tarball = dist(APPNAME, VERSION)

    import os
    os.system('scp %s tbaugis@master.gnome.org:/home/users/tbaugis' % tarball)
    os.system("ssh tbaugis@master.gnome.org 'install-module %s'" % tarball)

def release(ctx):
    """packaging a version"""
    import Scripting
    Scripting.commands += ['build', 'copy_help', 'push_release']
