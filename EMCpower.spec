#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%ifarch %{x8664}
%undefine	with_up
%endif

%define	__kernel_ver	2.6.5-7.252
%define	__kernel_rpmvr	%{__kernel_ver}

#
# main package.
#
%define		_rel	0.13
Summary:	EMC PowerPath - multi-path with fail-over and load-sharing over SCSI
Summary(pl):	EMC PowerPath - multi-path z fail-over i dzieleniem obci±¿enia po SCSI
Name:		EMCpower
Version:	4.5.1
Release:	%{_rel}
License:	Proprietary (not distributable)
Group:		Base/Kernel
Source0:	%{name}.LINUX-%{version}-022.sles.i386.rpm
# NoSource0-md5:	ed93c4daa2169b992c888ef5c27a6334
Source1:	%{name}.LINUX-%{version}-022.sles.x86_64.rpm
# NoSource1-md5:	b9e452479cff19640dee5431ff96f56c
NoSource:	0
NoSource:	1
Patch0:		%{name}-init.patch
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.286
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/emc
%define		_sbindir	/sbin
# binaries and libraries are x86
%define		_libdir		/usr/lib

%description
Multi-path software providing fail-over and load-sharing for SCSI
disks.

%description -l pl
Oprogramowanie do multi-path z opcj± fail-over i dzieleniem obci±¿enia
miêdzy dyski SCSI.

# kernel subpackages.

%package -n kernel-block-emc
Summary:	Linux driver for emc
Summary(pl):	Sterownik dla Linuksa do emc
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-block-emc
This is driver for emc for Linux.

This package contains Linux module.

%description -n kernel-block-emc -l pl
Sterownik dla Linuksa do emc.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-block-emc
Summary:	Linux SMP driver for emc
Summary(pl):	Sterownik dla Linuksa SMP do emc
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-block-emc
This is driver for emc for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-block-emc -l pl
Sterownik dla Linuksa do emc.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -qcT
%ifarch %{ix86}
rpm2cpio %{SOURCE0} | cpio -dimu
%endif
%ifarch %{x8664}
rpm2cpio %{SOURCE1} | cpio -dimu
%endif
mv etc/opt/emcpower/EMCpower.LINUX-%{version}/* .
%patch0 -p1

ln -s emcplib.Makefile bin/driver/Makefile

%build
cd bin/driver

%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts -j1
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
#
#	patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv emcplib{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_libdir},%{_sbindir},%{_mandir}/man1,/etc/modprobe.d,%{_datadir}/locale,/etc/rc.d/init.d}

cp -a man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
install modprobe.conf.pp $RPM_BUILD_ROOT/etc/modprobe.d/%{name}.conf
cp -a i18n/catalog/* $RPM_BUILD_ROOT%{_datadir}/locale
install PowerPath.rhel $RPM_BUILD_ROOT/etc/rc.d/init.d/powerpath
install bin/lib/* $RPM_BUILD_ROOT%{_libdir}
install bin/cmds/* $RPM_BUILD_ROOT%{_sbindir}
cp -a bin/.drivers_ext $RPM_BUILD_ROOT%{_sysconfdir}/drivers_ext

%find_lang EMCpower
%find_lang PowerPath
cat PowerPath.lang >> EMCpower.lang

# hardcoded paths. oh sigh
install -d $RPM_BUILD_ROOT/etc/opt/emcpower
ln -s %{_sbindir}/emcpmgr $RPM_BUILD_ROOT/etc/opt/emcpower
ln -s %{_sbindir}/powercf $RPM_BUILD_ROOT/etc/opt/emcpower
install -d $RPM_BUILD_ROOT/opt/emcpower
%endif

%if %{with kernel}
cd bin/driver
%if %{with up}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block
install emcplib-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/emcplib.ko

brand=sles; type=default
%ifarch %{x8664}
type=${type}_x8664
%endif
for a in emcplib emcp emcphr emcpioc emcpmp emcpmpaa emcpmpap emcpmpc; do
	install ${a}_$brand$type $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/$a.ko
done
%endif

%if %{with smp} && %{with dist_kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block
install emcplib-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block/emcplib.ko

brand=sles; type=smp
%ifarch %{x8664}
type=${type}_x8664
%endif
 for a in emcplib emcp emcphr emcpioc emcpmp emcpmpaa emcpmpap emcpmpc; do
	install ${a}_$brand$type $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block/$a.ko
done
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

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

%post	-n kernel-block-emc
%depmod %{_kernel_ver}

%postun	-n kernel-block-emc
%depmod %{_kernel_ver}

%post	-n kernel-smp-block-emc
%depmod %{_kernel_ver}-smp

%postun	-n kernel-smp-block-emc
%depmod %{_kernel_ver}-smp

%if %{with kernel}
%if %{with up}
%files -n kernel-block-emc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/block/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-block-emc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block/*.ko*
%endif
%endif

%if %{with userspace}
%files -f EMCpower.lang
%defattr(644,root,root,755)
%dir %{_sysconfdir}
%{_sysconfdir}/drivers_ext
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
%{_mandir}/man1/powermig.1*
%{_mandir}/man1/powermt.1*
%{_mandir}/man1/powerprotect.1*

# hardcoded paths. oh sigh
/etc/opt/emcpower
/opt/emcpower
%endif
