%undefine _debugsource_packages
%define         appname com.system76.CosmicGreeter
Name:           cosmic-greeter
Version:        1.0.0
Release:        0.alpha1.0
Summary:        COSMIC greeter for greetd
License:        GPL-3.0-only
URL:            https://github.com/pop-os/cosmic-greeter
Source0:        https://github.com/pop-os/cosmic-greeter/archive/epoch-%{version}-alpha.1/%{name}-epoch-%{version}-alpha.1.tar.gz
Source1:        vendor.tar.xz
Source2:        cargo_config

Source3:        %{name}.service
Source4:        %{name}-daemon.service
Patch0:         fix-dbus-conf.patch
Patch1:         switch-to-greetd-user.patch

BuildRequires:  rust-packaging
BuildRequires:  clang-devel
BuildRequires:  git-core
BuildRequires:  greetd
BuildRequires:  just
BuildRequires:  llvm-devel
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libudev)
%if 0%{?suse_version} < 1600
BuildRequires:  pam-devel
%else
BuildRequires:  pkgconfig(pam)
%endif
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(xkbcommon)
Requires:       bash
Requires:       cosmic-comp
#Requires:       mozilla-fira-fonts
Requires:       greetd >= 0.10
%systemd_requires

%description
libcosmic greeter for greetd, which can be run inside cosmic-comp

%prep
%autosetup -n %{name}-epoch-%{version}-alpha.1 -a1 -p1
mkdir .cargo
cp %{SOURCE2} .cargo/config

%build
just build-release

%install
just rootdir=%{buildroot} prefix=%{_prefix} install
install -d %{buildroot}%{_sharedstatedir}/%{name}
install -D -m 0644 %{name}.toml %{buildroot}%{_sysconfdir}/greetd/%{name}.toml
chmod 0644 %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
chmod -x %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
install -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-daemon.service
rm -f %{buildroot}%{_sysusersdir}/%{name}.conf

%pre
%service_add_pre %{name}.service %{name}-daemon.service

%post
%service_add_post %{name}.service %{name}-daemon.service
%tmpfiles_create %{_prefix}/lib/tmpfiles.d/%{name}.conf

%preun
%service_del_preun %{name}.service %{name}-daemon.service

%postun
%service_del_postun %{name}.service %{name}-daemon.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}-daemon
%config(noreplace) %{_sysconfdir}/greetd/%{name}.toml
%{_prefix}/lib/tmpfiles.d/%{name}.conf
%{_datadir}/dbus-1/system.d/%{appname}.conf
%{_sharedstatedir}/%{name}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-daemon.service
