%define gtk2_version 2.13.1
%define glib2_version 2.15.3
%define libgnomeui_version 2.6.0
%define libglade_version 2.3.6
%define libart_version 2.3.16
%define gnome_desktop_version 2.10.0
%define gnome_icon_theme_version 2.17.1
%define desktop_file_utils_version 0.9
%define gail_version 1.2.0
%define libexif_version 0.6.12
%define _default_patch_fuzz 999

Summary: Eye of GNOME image viewer
Name:    eog
Version: 2.28.2
Release: 4%{?dist}
URL: http://projects.gnome.org/eog/
Source: http://download.gnome.org/sources/eog/2.28/%{name}-%{version}.tar.bz2
Patch0: libxml.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=613641
Patch1: eog-dir-prefix.patch

# Make docs show up in rarian/yelp
Patch2: eog-doc-category.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589190
Patch3: eog-translations.patch

# The GFDL has an "or later version" clause embedded inside the license.
# There is no need to add the + here.
License: GPLv2+ and GFDL
Group: User Interface/Desktops
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: libglade2-devel >= %{libglade_version}
BuildRequires: gail-devel >= %{gail_version}
BuildRequires: libexif-devel >= %{libexif_version}
BuildRequires: exempi-devel
BuildRequires: lcms-devel
BuildRequires: libart_lgpl-devel >= %{libart_version}
BuildRequires: intltool
BuildRequires: libjpeg-devel
BuildRequires: scrollkeeper
BuildRequires: gettext
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: gnome-doc-utils
BuildRequires: gnome-desktop-devel >= %{gnome_desktop_version}
BuildRequires: gnome-icon-theme >= %{gnome_icon_theme_version}
BuildRequires: libXt-devel
BuildRequires: libxml2-devel

Requires(post): desktop-file-utils >= %{desktop_file_utils_version}
Requires(post): scrollkeeper
Requires(post): GConf2
Requires(pre): GConf2
Requires(preun): GConf2

Requires(postun): desktop-file-utils >= %{desktop_file_utils_version}
Requires(postun): scrollkeeper

%description
The Eye of GNOME image viewer (eog) is the official image viewer for the
GNOME desktop. It can view single image files in a variety of formats, as
well as large image collections.

eog is extensible through a plugin system.

%package devel
Summary: Support for developing plugins for the eog image viewer
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig
Requires: gtk-doc
Requires: gtk2-devel
Requires: libglade2-devel
Requires: GConf2-devel

%description devel
The Eye of GNOME image viewer (eog) is the official image viewer for the
GNOME desktop. This package allows you to develop plugins that add new
functionality to eog.

%prep
%setup -q
%patch0 -p1 -b .libxml
%patch1 -p1 -b .dir-prefix
%patch2 -p1 -b .doc-category
%patch3 -p1 -b .translations

echo "NoDisplay=true" >> data/eog.desktop.in
# just in case
echo "NoDisplay=true" >> data/eog.desktop.in.in

%build

%configure --disable-scrollkeeper
make

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor gnome --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --remove-category Application				    \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

%find_lang %{name} --with-gnome

# grr, --disable-scrollkeeper seems broken
rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

mkdir -p $RPM_BUILD_ROOT%{_libdir}/eog/plugins

# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done


%clean
rm -rf $RPM_BUILD_ROOT

%post
update-desktop-database -q
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/eog.schemas > /dev/null || :
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/eog.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/eog.schemas > /dev/null || :
fi

%postun
update-desktop-database -q
scrollkeeper-update -q
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING NEWS README
%{_datadir}/eog
%{_datadir}/applications/*
%{_datadir}/omf/*
%{_datadir}/icons/hicolor/*/apps/*
%{_bindir}/*
%{_sysconfdir}/gconf/schemas/*.schemas
%{_libdir}/eog

%files devel
%defattr(-,root,root)
%{_includedir}/eog-2.20
%{_libdir}/pkgconfig/eog.pc
%{_datadir}/gtk-doc/html/eog

%changelog
* Fri May  7 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-4
- Updated translations
Resolves: #589190

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-3
- Make docs show up in yelp
Resolves: #588530

* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> 2.28.2-2
Resolves: #575932
- Support relocatable .gnome2

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-1
- Update to 2.28.2, sync with Fedora 12

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-1
- Update to 2.28.1

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> 2.28.0-1
- Update to 2.28.0

* Tue Sep  8 2009 Matthias Clasen <mclasen@redhat.com> 2.27.92-1
- Update to 2.27.92

* Mon Aug 24 2009 Matthias Clasen <mclasen@redhat.com> 2.27.91-1
- Update to 2.27.91

* Fri Aug 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.90-1
- 2.27.90

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-1
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.4-1
- Update to 2.27.4

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> 2.27.3-1
- Update to 2.27.3

* Wed May 27 2009 Bastien Nocera <bnocera@redhat.com> 2.27.2-1
- Update to 2.27.2

* Sat May 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.1-1
- Update to 2.27.1

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/eog/2.26/eog-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Tue Mar  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Tue Jan 20 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.4-1
- Update to 2.25.4

* Wed Dec 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.3-2
- Update to 2.25.3

* Wed Dec  3 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.2-1
- Update to 2.25.2

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.1-5
- Better URL

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.1-4
- Tweak %%summary and %%description

* Wed Nov 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.1-3
- Update to 2.25.1

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Thu Oct  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-2
- Save some space

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Tue Aug 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-2
- Add a possible fix for a deadlock

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Fri Aug  1 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-2
- Use standard icon names

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-1
- Update to 2.23.4.1

* Wed Jun  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Wed May 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.23.2-2
- fix license tag

* Tue May 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2-1
- Update to 2.23.2

* Fri Apr 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-1
- Update to 2.23.1
 
* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Wed Feb 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Mon Jan 14 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.4-1
- Update to 2.21.4

* Tue Dec 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Tue Dec  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Tue Nov 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.1-1
- Update to 2.21.1

* Tue Oct 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Rebuild against new dbus-glib

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (bug fixes and translation updates)

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Mon Sep  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Thu Aug 16 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-3
- Hide it from the menus _again_

* Tue Aug 14 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-2
- Build with XMP support

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Thu Aug  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-4
- Hide it from the menus again

* Mon Aug  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-3
- Update license field
- Use %%find_lang for help files, too

* Tue Jul 24 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-2
- Fix a undefined macro use (#248689)

* Tue Jul 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-1
- Update to 2.19.4

* Fri Jul  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-2
- Fix a directory ownership issue

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2
- Split off a -devel package
- Small spec fixes

* Sun Apr  1 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0.1-27
- Fix a problem with the svgz patch

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0.1-1
- Update to 2.18.0.1

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Mon Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.4-1
- Update to 2.17.4

* Tue Jan 09 2007 Behdad Esfahbod <besfahbo@redhat.com> - 2.17.3-2
- Handle svgz images
- Resolves: #219782

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.3-1
- Update to 2.17.3

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Fri Oct 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.1-1
- Update to 2.17.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0.1-3
- Fix scripts according to the packaging guidelines

* Thu Sep  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0.1-2.fc6
- Fix some directory ownership issues

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0.1-1.fc6
- Update to 2.16.0.1

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-1.fc6
- Update to 2.15.92

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.91-1.fc6
- Update to 2.15.91

* Wed Aug  2 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.90-1.fc6
- Update to 2.15.90

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.4-1
- Update to 2.15.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.3-1.1
- rebuild

* Tue Jun 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.3-1
- Update to 2.15.3

* Mon May 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2-1
- Update to 2.15.2

* Sat May 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-2
- Add missing BuildRequires (#129025)

* Tue May  9 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1
- Remove workaround for a long-fixed bug

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Sat Mar  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.92-1
- Update to 2.13.92
- Drop upstreamed patch

* Wed Feb 15 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-2
- silence excessive debug output

* Wed Feb 15 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Mon Feb 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.90-2
- Append NoDisplay=true to the right file

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 30 2006 Matthias Clasen <mclasen@redhat.com> 2.13.90-1
- Update to 2.13.90

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> 2.13.5-1
- Update to 2.13.5

* Fri Jan 13 2006 Matthias Clasen <mclasen@redhat.com> 2.13.4-1
- Update to 2.13.4

* Wed Dec 14 2005 Matthias Clasen <mclasen@redhat.com> 2.13.3-1
- Update to 2.13.3

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Matthias Clasen <mclasen@redhat.com> 2.13.2-1
- Update to 2.13.2

* Thu Oct  6 2005 Matthias Clasen <mclasen@redhat.com> 2.12.1-1
- Update to 2.12.1

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 2.12.0-1
- Update to 2.12.0

* Tue Aug 16 2005 Matthias Clasen <mclasen@redhat.com> 
- Rebuilt

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-1
- Newer upstream version

* Fri Jul  8 2005 Matthias Clasen <mclasen@redhat.com> 2.11.0-1
- Update to 2.11.0

* Mon Mar 28 2005 Matthias Clasen <mclasen@redhat.com> 2.10.0-1
- Update to 2.10.0

* Thu Mar  3 2005 Marco Pesenti Gritti <mpg@redhat.com> 2.9.0-2
- Rebuild

* Mon Jan 31 2005 Matthias Clasen <mclasen@redhat.com> 2.9.0-1
- Update to 2.9.0

* Sat Nov  6 2004 Marco Pesenti Gritti <mpg@redhat.com> 2.8.1-1
- Update to 2.8.1

* Thu Sep 30 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-3
- Prereq desktop-file-utils >= 0.9
- update-desktop-database on uninstall

* Sun Sep 26 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-2
- Remove the graphics menu entry (#131724)

* Wed Sep 22 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-1
- Update to 2.8.0

* Wed Aug 19 2004 Christopher Aillon <caillon@redhat.com> 2.7.1-1
- Update to 2.7.1

* Mon Aug 16 2004 Christopher Aillon <caillon@redhat.com> 2.7.0-3
- Use update-desktop-database instead of rebuild-mime-info-cache

* Sun Aug 15 2004 Christopher Aillon <caillon@redhat.com> 2.7.0-2
- Rebuild MIME info cache

* Sun Aug 15 2004 Christopher Aillon <caillon@redhat.com> 2.7.0-1
- Update to 2.7.0

* Tue Jun 29 2004 Christopher Aillon <caillon@redhat.com> 2.6.1-1
- Update to 2.6.1

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat Apr 10 2004 Warren Togami <wtogami@redhat.com> 2.6.0-2
- BR intltool libjpeg-devel scrollkeeper gettext

* Fri Apr  2 2004 Alex Larsson <alexl@redhat.com> 2.6.0-1
- update to 2.6.0

* Wed Mar 10 2004 Alex Larsson <alexl@redhat.com> 2.5.90-1
- update to 2.5.90

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.6-1
- update to 2.5.6

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jan 30 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- update to 2.5.3

* Fri Oct  3 2003 Alexander Larsson <alexl@redhat.com> 2.4.0-1
- 2.4.0

* Fri Aug 29 2003 Alexander Larsson <alexl@redhat.com> 2.3.5-2
- prereq gconf2 (#90698)

* Tue Aug 19 2003 Alexander Larsson <alexl@redhat.com> 2.3.5-1
- update for gnome 2.3

* Tue Jul 29 2003 Havoc Pennington <hp@redhat.com> 2.2.2-2
- rebuild

* Mon Jul  7 2003 Havoc Pennington <hp@redhat.com> 2.2.2-1
- 2.2.2
- remove arg-escaping patch now upstream

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Apr  1 2003 Havoc Pennington <hp@redhat.com> 2.2.0-2
- add patch to better escape filenames passed in as arguments
- add eel2-devel buildreq

* Thu Feb  6 2003 Havoc Pennington <hp@redhat.com> 2.2.0-1
- 2.2.0
- fix dependency versions

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Dec 13 2002 Tim Powers <timp@redhat.com> 1.1.3-1
- update to 1.1.3
- include glade file

* Sun Dec  1 2002 Havoc Pennington <hp@redhat.com>
- 1.1.2

* Tue Aug  6 2002 Havoc Pennington <hp@redhat.com>
- 1.0.2
- remove --copy-generic-name-to-name because there's no GenericName
  anymore
- include libexecdir stuff

* Mon Jul 29 2002 Havoc Pennington <hp@redhat.com>
- copy generic name to name and move to -Extra

* Mon Jul 29 2002 Havoc Pennington <hp@redhat.com>
- 1.0.1, rebuild with new gail

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 1.0.0
- use desktop-file-install

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun 05 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment
- build requires libgnomeprint

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 0.118.0

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 0.117.0

* Thu Apr 25 2002 Havoc Pennington <hp@redhat.com>
- initial build



