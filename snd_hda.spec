%define kmod_name		snd_hda
%define kmod_driver_version	1.0.21.6.3.0
%define kmod_rpm_release	1
%define kmod_git_hash		b5435d9eba68ec9af045ba9beab36202ebf957ec
%define kmod_kernel_version	2.6.32-220.el6
%define kmod_kbuild_dir		sound/pci/hda/


%{!?dist: %define dist .el6}

Source0:	%{kmod_name}-%{kmod_driver_version}.tar.bz2			
Source1:	%{kmod_name}.files			
Source2:	depmodconf			
Source3:	find-requires.ksyms			
Source4:	find-provides.ksyms			
Source5:	kmodtool			
Source6:	Module.symvers-i686			
Source7:	Module.symvers-x86_64			
Source8:	symbols.greylist-i686			
Source9:	symbols.greylist-x86_64			

%define __find_requires %_sourcedir/find-requires.ksyms
%define __find_provides %_sourcedir/find-provides.ksyms %{kmod_name} %{?epoch:%{epoch}:}%{version}-%{release}

Name:		%{kmod_name}
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	%{kmod_name} kernel module

Group:		System/Kernel
License:	GPLv2
URL:		http://www.kernel.org/
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	%kernel_module_package_buildreqs
ExclusiveArch:  i686 x86_64


# Build only for standard kernel variant(s); for debug packages, append "debug"
# after "default" (separated by space)
%kernel_module_package -s %{SOURCE5} -f %{SOURCE1}  default

%description
%{kmod_name} - driver update

%prep
%setup
set -- *
mkdir source
mv "$@" source/
cp %{SOURCE6} source/
cp %{SOURCE7} source/
cp %{SOURCE8} source/
cp %{SOURCE9} source/
mkdir obj

%build
for flavor in %flavors_to_build; do
	rm -rf obj/$flavor
	cp -r source obj/$flavor

	# update symvers file if existing
	symvers=source/Module.symvers-%{_target_cpu}
	if [ -e $symvers ]; then
		cp $symvers obj/$flavor/%{kmod_kbuild_dir}/Module.symvers
	fi

	make -C %{kernel_source $flavor} M=$PWD/obj/$flavor/%{kmod_kbuild_dir} \
		NOSTDINC_FLAGS="-I $PWD/obj/$flavor/include"
done

%{SOURCE2} %{name} %{kmod_kernel_version} obj > source/depmod.conf

greylist=source/symbols.greylist-%{_target_cpu}
if [ -f $greylist ]; then
	cp $greylist source/symbols.greylist
else
	touch source/symbols.greylist
fi

if [ -d source/firmware ]; then
	make -C source/firmware
fi

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{name}
for flavor in %flavors_to_build ; do
	make -C %{kernel_source $flavor} modules_install \
		M=$PWD/obj/$flavor/%{kmod_kbuild_dir}
	# Cleanup unnecessary kernel-generated module dependency files.
	find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;
done

install -m 644 -D source/depmod.conf $RPM_BUILD_ROOT/etc/depmod.d/%{kmod_name}.conf
install -m 644 -D source/symbols.greylist $RPM_BUILD_ROOT/usr/share/doc/kmod-%{kmod_name}/greylist.txt

if [ -d source/firmware ]; then
	make -C source/firmware INSTALL_PATH=$RPM_BUILD_ROOT INSTALL_DIR= install
fi

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Fri Apr 13 2012 Jiri Benc <jbenc@redhat.com> 1.0.21.6.3.0 1
- snd_hda DUP module
