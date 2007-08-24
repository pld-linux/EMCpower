#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# build kernel modules
%bcond_with	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

# just don't want to build it :)
%ifarch %{x8664}
%undefine	with_up
%endif

%define	__kernel_ver	2.6.16.21-0.8
%define	__kernel_rpmvr	%{__kernel_ver}

%define	releq_kernel_smp	kernel-smp = 0:%{__kernel_ver}
%define	releq_kernel_up		kernel-up = 0:%{__kernel_ver}

%define		_rel	1
Summary:	EMC PowerPath - multi-path with fail-over and load-sharing over SCSI
Summary(pl.UTF-8):	EMC PowerPath - multi-path z fail-over i dzieleniem obciążenia po SCSI
Name:		EMCpower
Version:	5.0.0
Release:	%{_rel}
License:	Proprietary (not distributable)
Group:		Base
%ifarch %{ix86}
Source0:	%{name}.LINUX-%{version}-157.sles10.i386.rpm
# NoSource0-md5:	9e687044c65d2ee368b71c339e639522
NoSource:	0
%endif
%ifarch %{x8664}
Source1:	%{name}.LINUX-%{version}-157.sles10.x86_64.rpm
# NoSource1-md5:	cf980fc4714f0be008de168333cefcb4
NoSource:	1
%endif
Source2:	PowerPath.init
Requires(post,preun):	/sbin/chkconfig
Obsoletes:	EMCpower.LINUX
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/something/bogus
%define		_sbindir	/sbin

%description
Multi-path software providing fail-over and load-sharing for SCSI
disks.

%description -l pl.UTF-8
Oprogramowanie do multi-path z opcją fail-over i dzieleniem obciążenia
między dyski SCSI.

# kernel subpackages.

%package -n kernel-block-emc
Summary:	Linux driver for emc
Summary(pl.UTF-8):	Sterownik dla Linuksa do emc
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

%description -n kernel-block-emc -l pl.UTF-8
Sterownik dla Linuksa do emc.

Ten pakiet zawiera moduł jądra Linuksa.

%package -n kernel-smp-block-emc
Summary:	Linux SMP driver for emc
Summary(pl.UTF-8):	Sterownik dla Linuksa SMP do emc
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

%description -n kernel-smp-block-emc -l pl.UTF-8
Sterownik dla Linuksa do emc.

Ten pakiet zawiera moduł jądra Linuksa SMP.

%prep
%setup -qcT
%ifarch %{ix86}
rpm2cpio %{SOURCE0} | cpio -dimu
%endif
%ifarch %{x8664}
rpm2cpio %{SOURCE1} | cpio -dimu
%endif
mv etc/opt/emcpower/EMCpower.LINUX-%{version}/* .
echo 'options emcp managedclass=symm,clariion,hitachi,invista,hpxp,ess,hphsx' >> modprobe.conf.pp

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
install -d $RPM_BUILD_ROOT{/etc/emc/ppme,%{_libdir},%{_sbindir},%{_mandir}/man1,/etc/modprobe.d,%{_datadir}/locale,/etc/rc.d/init.d}

cp -a man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
cp -a i18n/catalog/* $RPM_BUILD_ROOT%{_datadir}/locale
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/PowerPath
install bin/lib/* $RPM_BUILD_ROOT%{_libdir}
install bin/cmds/* $RPM_BUILD_ROOT%{_sbindir}
cp -a bin/.drivers_* $RPM_BUILD_ROOT/etc/emc

%find_lang EMCpower
%find_lang PowerPath
cat PowerPath.lang >> EMCpower.lang

# hardcoded paths. oh sigh
install -d $RPM_BUILD_ROOT/etc/opt/emcpower/.tmp
mv $RPM_BUILD_ROOT{%{_sbindir},/etc/opt/emcpower}/emcpmgr
mv $RPM_BUILD_ROOT{%{_sbindir},/etc/opt/emcpower}/powercf
touch $RPM_BUILD_ROOT/etc/opt/emcpower/.__emcp_db_global_lock
touch $RPM_BUILD_ROOT/etc/opt/emcpower/.__emcp_db_lock

install -d $RPM_BUILD_ROOT/opt/emcpower
install -d $RPM_BUILD_ROOT/etc/emcpower
touch $RPM_BUILD_ROOT/etc/emc/mpaa.{excluded,lams}
%endif

%if %{with kernel}
%if %{with up}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block
install -D modprobe.conf.pp $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}/%{name}.conf

brand=sles10; type=default
%ifarch %{x8664}
type=${type}_x8664
%endif
for a in emcp emcpdm emcpgpx emcpioc emcplib emcpmpx; do
	install bin/driver/${a}_$brand$type $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/$a.ko
done
%endif

%if %{with smp} && %{with dist_kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block
install -D modprobe.conf.pp $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}-smp/%{name}.conf
brand=sles10; type=smp
%ifarch %{x8664}
type=${type}_x8664
%endif
for a in emcp emcpdm emcpgpx emcpioc emcplib emcpmpx; do
	install bin/driver/${a}_$brand$type $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block/$a.ko
done
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add PowerPath

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del PowerPath
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
/etc/modprobe.d/%{_kernel_ver}/%{name}.conf
/lib/modules/%{_kernel_ver}/kernel/drivers/block/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-block-emc
%defattr(644,root,root,755)
/etc/modprobe.d/%{_kernel_ver}-smp/%{name}.conf
/lib/modules/%{_kernel_ver}-smp/kernel/drivers/block/*.ko*
%endif
%endif

%if %{with userspace}
%files -f EMCpower.lang
%defattr(644,root,root,755)
%dir /etc/emc
%dir /etc/emc/ppme
/etc/emc/.drivers_*
%ghost /etc/emc/mpaa.excluded
%ghost /etc/emc/mpaa.lams
%attr(754,root,root) /etc/rc.d/init.d/PowerPath
%attr(755,root,root) %{_sbindir}/emcpadm
%attr(755,root,root) %{_sbindir}/emcpdiscover
%attr(755,root,root) %{_sbindir}/emcppurge
%attr(755,root,root) %{_sbindir}/emcpreg
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
%attr(755,root,root) /etc/opt/emcpower/emcpmgr
%attr(755,root,root) /etc/opt/emcpower/powercf
%ghost /etc/opt/emcpower/.__emcp_db_global_lock
%ghost /etc/opt/emcpower/.__emcp_db_lock
%dir /opt/emcpower
%dir /etc/emcpower
%endif
