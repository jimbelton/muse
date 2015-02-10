muse
====

Python program for backing up, restoring, and comparing your music library

Description
===========
*muse* is a command line program that back ups, restores, and helps you manage your music library.
Running it with the --help option will give you a detailed manual page.

Commands
========

<table>
<tr><td><b>Command</b></td><td><b>Description</b></td></tr>
<tr><td>--backup</td><td>Backup music from your library</td></tr>
<tr><td>--cmp</td><td>Compare your library to your backup</td></tr>
<tr><td>--display</td><td>Display the contents of your library or backup</td></tr>
<tr><td>--help</td><td>Display the help file</td></tr>
<tr><td>--restore</td><td>Restore files from your backup to your libary</td></tr>
</table>

Options
=======

<table>
<tr><td><b>Option</b></td><td><b>Description</b></td></tr>
<tr><td>--fail-on-warning</td><td>Stop if any warning is encountered</td></tr>
<tr><td>--fix</td><td>When displaying, fix file names. When backing up, make the backup like the libary. When restoring, make the
libary like the backup.</td></tr>
<tr><td>--ignore-error</td><td>Ignore errors, treating them like warnings</td></tr>
<tr><td>--library</td><td>Override the default location of the library</td></tr>
<tr><td>--metadata</td><td>Include ID3 frames in display</td></tr>
<tr><td>--noaction</td><td>Tell what a command would do but take no action</td></tr>
<tr><td>--quiet</td><td>Supress warnings</td></tr>
<tr><td>--verbose</td><td>Display actions taken</td></tr>
</table>

