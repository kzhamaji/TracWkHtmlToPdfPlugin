# vim: ts=8:sts=4:sw=4:et

import subprocess
import tempfile
import re
import os

from trac.core import *
from trac.mimeview.api import IContentConverter
from trac.env import ISystemInfoProvider
from trac.config import Option, ListOption
from trac.util import lazy

class TracWkHtmlToPdfPlugin (Component):

    implements(IContentConverter, ISystemInfoProvider)
    #implements(IContentConverter)

    wkhtmltopdf_path = Option('wkhtmltopdf', 'wkhtmltopdf', '/usr/local/bin/wkhtmltopdf')
    xvfb_run_path = Option('wkhtmltopdf', 'xvfb_run', '/bin/xvfb-run')

    wkhtmltopdf_args = ListOption('wkhtmltopdf', 'wkhtmltopdf_args',
                                  '--print-media-type, --page-size, A4, --disable-external-links')

    # IContentConverter methods
    def get_supported_conversions(self):
        yield ('pdf', 'PDF', 'pdf', 'text/x-trac-wiki', 'application/pdf', 7)

    def convert_content(self, req, input_type, text, output_type):
        args = [self.xvfb_run_path, '--', self.wkhtmltopdf_path]
        args.append('--quiet')
        args.append('--encoding')
        args.append('utf-8')

        args.append('--cookie')
        args.append('trac_auth')
        args.append(req.incookie['trac_auth'].value)

        _args = req.args.copy()
        del _args['format']
        page = _args.pop('page')

        args.append('--title')
        args.append(re.sub(r'[/]', '_', page))

        args += self.wkhtmltopdf_args

        
        url = req.abs_href.wiki(page, _args)
        args.append(url)
        
        with tempfile.NamedTemporaryFile(delete=True) as temp:
            args.append(temp.name)
            self.run_command(args, False)
            fo = open(temp.name, 'rb')
            out = fo.read()
            fo.close()

        return (out, 'application/pdf')


    # ISystemInfoProvider methods
    def get_system_info(self):
        yield 'wkhtmltopdf', self.wkhtmltopdf_version
        yield 'xvfb-run', self.xvfb_run_version

    @lazy
    def wkhtmltopdf_version (self):
        try:
            version = self.wkhtmltopdf_version_()
        except TracError, e:
            version = "Executable not found or unexpected error"
        return version

    @lazy
    def xvfb_run_version (self):
        try:
            version = self.xvfb_run_version_()
        except TracError, e:
            version = "Executable not found or unexpected error"
        return version

    def wkhtmltopdf_version_ (self):
        _, version, err = self.run_command((self.wkhtmltopdf_path, '--version'))
        self.env.log.debug("Using wkhtmltopdf_path %s", version)
        return version

    def xvfb_run_version_ (self):
        _, version, err = self.run_command((self.xvfb_run_path, '--help'))
        self.env.log.debug("Using xvfb_run_path %s", version)
        return "OK"

    def run_command (self, args, strict=True):
        try:
            new_env = os.environ.copy()
            new_env['LANG'] = 'ja_JP.UTF-8'
            proc = subprocess.Popen(args, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env)
            out, err = proc.communicate()
            if strict and proc.returncode != 0:
                raise TracError("Fail to run %s: %s: %s" % (proc.returncode, args, err))
            return (proc.returncode, out, err)
        except OSError, e:
            raise TracError(e)
