#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
import shutil

# since the file isn't named valet.py, "import valet" doesn't work
import imp
imp.load_source('valet', 'valet')
import valet

class SetUpValetTests(unittest.TestCase):
    test_dir = 'test-content'
    test_utf8_file = os.path.join(test_dir, u'utf8 Σὲ γνωρίζω.md')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

class ValetDirectoryTests(SetUpValetTests):
    test_dir = SetUpValetTests.test_dir
    test_subdir = os.path.join(test_dir, 'subdir_level_1')
    test_subdir_file = os.path.join(test_subdir, 'test.md')

    def setUp(self):
        if os.path.isdir(self.test_dir): return
        os.mkdir(self.test_dir)
        os.mkdir(self.test_subdir)

        f = open(self.test_subdir_file, 'w')
        f.write('# Markdown level 1\n##Markdown level 2')
        f.close()

    def test_directory_view(self):
        """Verifies that viewing a directory does something at all"""
        self.assertTrue(valet.view(self.test_dir).startswith("<HTML>"))
    def test_subdir_view(self):
        """Verifies that viewing a subdirectory does something at all"""
        self.assertTrue(valet.view(self.test_subdir).startswith("<HTML>"))
    def test_subdir_file_view(self):
        """Verifies that viewing a file in a subdirectory does something at all"""
        self.assertTrue(valet.view(self.test_subdir_file).startswith("<HTML>"))
    def test_directory_no_edit(self):
        """Verifies that the 'edit' link is absent on directories"""
        self.assertFalse(valet.view(self.test_subdir)
                         .find(self.test_subdir + "?edit") >= 0)
    def test_directory_no_log(self):
        """Verifies that the 'log' link is absent on directories"""
        self.assertFalse(valet.view(self.test_subdir)
                         .find(self.test_subdir + "?log") >= 0)
    def test_directory_no_raw(self):
        """Verifies that the 'raw' link is absent on directories"""
        self.assertFalse(valet.view(self.test_subdir)
                         .find(self.test_subdir + "?raw") >= 0)

class ValetBasicFileTests(SetUpValetTests):
    test_dir = SetUpValetTests.test_dir
    test_file = os.path.join(test_dir, 'test.txt')

    def setUp(self):
        if os.path.isdir(self.test_dir): return
        os.mkdir(self.test_dir)

        f = open(self.test_file, 'w')
        f.write('file contents present')
        f.close()

    def test_file_view(self):
        """Verifies that viewing a file does something at all"""
        self.assertTrue(valet.view(self.test_file).startswith("<HTML>"))
    def test_file_contents(self):
        """Verifies that viewing a file contains the correct contents"""
        self.assertTrue(valet.view(self.test_file)
                        .find("file contents present") >= 0)
    def test_edit_link(self):
        """Verifies that the 'edit' link is present and has the correct URL"""
        initial = valet.READONLY
        valet.READONLY = False
        self.assertTrue(valet.view(self.test_file).find(self.test_file + "?edit") >= 0)
        valet.READONLY = initial
    def test_readonly_edit_link_absent(self):
        """Verifies that the 'edit' link is absent in read-only mode"""
        initial = valet.READONLY
        valet.READONLY = True
        self.assertTrue(valet.view(self.test_file).find(self.test_file + "?edit") < 0)
        valet.READONLY = initial
    def test_raw_link(self):
        """Verifies that the 'raw' link is present and has the correct URL"""
        self.assertTrue(valet.view(self.test_file).find(self.test_file + "?raw") >= 0)


class ValetPythonFileTests(SetUpValetTests):
    test_dir = SetUpValetTests.test_dir
    test_python_file = os.path.join(test_dir, 'test.py')

    def setUp(self):
        if os.path.isdir(self.test_dir): return
        os.mkdir(self.test_dir)

        f = open(self.test_python_file, 'w')
        f.write('import os\nif __name__ == "__main__":\n    print "Hello, world!"')
        f.close()

    def test_python_pygments(self):
        """Verifies that a file is properly syntax-highlighted if pygments exists"""
        try:
            import pygments
        except ImportError:
            return
        self.assertTrue(valet.view(self.test_python_file).find('<span class="n">__name__</span>') >= 0)

class ValetUTF8FileTests(SetUpValetTests):
    test_dir = SetUpValetTests.test_dir
    test_utf8_file = os.path.join(test_dir, u'utf8 Σὲ γνωρίζω.md')

    def setUp(self):
        if os.path.isdir(self.test_dir): return
        os.mkdir(self.test_dir)

        f = open(self.test_utf8_file, 'w')
        f.write(u'Οὐχὶ ταὐτὰ παρίσταταί μοι γιγνώσκειν, ὦ ἄνδρες ᾿Αθηναῖοι,'
                .encode('utf-8'))
        f.close()

    def test_utf8_file_view(self):
        """Verifies that viewing a UTF-8 file does something at all"""
        self.assertTrue(valet.view(self.test_utf8_file).startswith("<HTML>"))
    def test_utf8_file_correctness(self):
        """Verifies that viewing a UTF-8 file has the right content"""
        self.assertTrue(valet.view(self.test_utf8_file).find(u'ταὐτὰ παρίσταταί') >= 0)

if __name__ == '__main__':
    unittest.main()
