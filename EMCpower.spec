%define		_rel	0.1
Summary:	EMC PowerPath - multi-path with fail-over and load-sharing over SCSI
Summary(pl.UTF-8):	EMC PowerPath - multi-path z fail-over i dzieleniem obciążenia po SCSI
Name:		EMCpower
Version:	5.0.0
Release:	%{_rel}
License:	Proprietary (not distributable)
Group:		Base
Source0:	%{name}.LINUX-%{version}-157.sles10.i386.rpm
# NoSource0-md5:	9e687044c65d2ee368b71c339e639522
Source1:	%{name}.LINUX-%{version}-157.sles10.x86_64.rpm
# NoSource1-md5:	cf980fc4714f0be008de168333cefcb4
NoSource:	0
NoSource:	1
Patch0:		%{name}-init.patch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/something/bogus
%define		_sbindir	/sbin
# binaries and libraries are x86
%define		_libdir		/usr/lib

%description
Multi-path software providing fail-over and load-sharing for SCSI
disks.

%description -l pl.UTF-8
Oprogramowanie do multi-path z opcją fail-over i dzieleniem obciążenia
między dyski SCSI.


%prep
%setup -qcT
%ifarch %{ix86}
rpm2cpio %{SOURCE0} | cpio -dimu
%endif
%ifarch %{x8664}
rpm2cpio %{SOURCE1} | cpio -dimu
%endif
mv etc/opt/emcpower/EMCpower.LINUX-%{version}/* .
#%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/emc/ppme,%{_libdir},%{_sbindir},%{_mandir}/man1,/etc/modprobe.d,%{_datadir}/locale,/etc/rc.d/init.d}

cp -a man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
install modprobe.conf.pp $RPM_BUILD_ROOT/etc/modprobe.d/%{name}.conf
cp -a i18n/catalog/* $RPM_BUILD_ROOT%{_datadir}/locale
install PowerPath.rhel $RPM_BUILD_ROOT/etc/rc.d/init.d/powerpath
install bin/lib/* $RPM_BUILD_ROOT%{_libdir}
install bin/cmds/* $RPM_BUILD_ROOT%{_sbindir}
cp -a bin/.drivers_ext $RPM_BUILD_ROOT/etc/emc/drivers_ext

%find_lang EMCpower
%find_lang PowerPath
cat PowerPath.lang >> EMCpower.lang

# hardcoded paths. oh sigh
install -d $RPM_BUILD_ROOT/etc/opt/emcpower/.tmp
ln -s %{_sbindir}/emcpmgr $RPM_BUILD_ROOT/etc/opt/emcpower
ln -s %{_sbindir}/powercf $RPM_BUILD_ROOT/etc/opt/emcpower
touch $RPM_BUILD_ROOT/etc/opt/emcpower/.__emcp_db_global_lock
touch $RPM_BUILD_ROOT/etc/opt/emcpower/.__emcp_db_lock

install -d $RPM_BUILD_ROOT/opt/emcpower
install -d $RPM_BUILD_ROOT/etc/emcpower
touch $RPM_BUILD_ROOT/etc/emc/mpaa.{excluded,lams}

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%verifyscript
echo "These PowerPath modules are installed"
/sbin/lsmod | head -n 1
/sbin/lsmod | grep emc
echo "DONE"

%pre
# Check - Only install on a 2.6 kernel
expr `uname -r` : '2\.6' > /dev/null
if [ $? -ne 0 ]; then
	echo "This PowerPath package does not support this kernel."
	exit 1
fi

# Check - Make sure no devices are in use.
if [ "`/sbin/lsmod | grep -w emcp`" != "" ]; then
	/sbin/powermt save > /dev/null 2>&1
	/sbin/powermt remove dev=all > /dev/null 2>&1
	if [ "`powermt display dev=all 2>&1 | grep "not found"`" = "" ]; then
		echo "Unable to remove devices from the PowerPath configuration."
		echo "Please make sure no PowerPath devices are in use and retry."
		/sbin/powermt config > /dev/null 2>&1
		/sbin/powermt load > /dev/null 2>&1
		exit 1
	fi
	/sbin/powermt config > /dev/null 2>&1
	/sbin/powermt load > /dev/null 2>&1
fi
%endif

%files -f EMCpower.lang
%defattr(644,root,root,755)
%dir /etc/emc
%dir /etc/emc/ppme
/etc/emc/drivers_ext
%ghost /etc/emc/mpaa.excluded
%ghost /etc/emc/mpaa.lams
/etc/modprobe.d/EMCpower.conf
%attr(754,root,root) /etc/rc.d/init.d/powerpath
%attr(755,root,root) %{_sbindir}/emcpadm
%attr(755,root,root) %{_sbindir}/emcpdiscover
%attr(755,root,root) %{_sbindir}/emcpmgr
%attr(755,root,root) %{_sbindir}/emcppurge
%attr(755,root,root) %{_sbindir}/emcpreg
%attr(755,root,root) %{_sbindir}/powercf
%attr(755,root,root) %{_sbindir}/powermt
%attr(755,root,root) %{_sbindir}/powerprotect
%attr(755,root,root) %{_sbindir}/powermig
%attr(755,root,root) %{_sbindir}/pp_inq
%attr(755,root,root) %{_libdir}/libemcp.so
%attr(755,root,root) %{_libdir}/libemcp_core.so
%attr(755,root,root) %{_libdir}/libemcp_lam.so
%attr(755,root,root) %{_libdir}/libemcp_lic_rtl.so
%attr(755,root,root) %{_libdir}/libemcp_mp_rtl.so
%attr(755,root,root) %{_libdir}/libemcpmp.so
%attr(755,root,root) %{_libdir}/libpn.so
%{_mandir}/man1/emcpadm.1*
%{_mandir}/man1/emcpreg.1*
%{_mandir}/man1/emcpupgrade.1*
%{_mandir}/man1/powerformat.1*
%{_mandir}/man1/powermig.1*
%{_mandir}/man1/powermt.1*
%{_mandir}/man1/powerprotect.1*

# hardcoded paths. oh sigh
%dir /etc/opt/emcpower
%ghost /etc/opt/emcpower/.__emcp_db_global_lock
%ghost /etc/opt/emcpower/.__emcp_db_lock
/opt/emcpower
%dir /etc/emcpower
