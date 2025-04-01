%undefine _debugsource_packages

%define         appname com.system76.CosmicGreeter
Name:           cosmic-greeter
Version:        1.0.0
%define beta alpha.6
Release:        %{?beta:0.%{beta}.}1
Summary:        COSMIC greeter for greetd
License:        GPL-3.0-only
URL:            https://github.com/pop-os/cosmic-greeter
Source0:        https://github.com/pop-os/cosmic-greeter/archive/epoch-%{version}%{?beta:-%{beta}}/%{name}-epoch-%{version}%{?beta:-%{beta}}.tar.gz
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
%autosetup -n %{name}-epoch-%{version}%{?beta:-%{beta}} -a1 -p1
mkdir .cargo
cp %{SOURCE2} .cargo/config.toml

%build
just build-release

%install
just rootdir=%{buildroot} prefix=%{_prefix} install
chmod 0644 %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
chmod -x %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
install -Dm0644 debian/cosmic-greeter.sysusers %{buildroot}/%{_sysusersdir}/cosmic-greeter.conf
install -Dm0644 debian/cosmic-greeter.tmpfiles %{buildroot}/%{_tmpfilesdir}/cosmic-greeter.conf
install -Dm0644 cosmic-greeter.toml %{buildroot}/%{_sysconfdir}/greetd/cosmic-greeter.toml
install -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}-daemon.service

install -d %{buildroot}%{_sysconfdir}/pam.d
ln -s %{_sysconfdir}/pam.d/greetd %{buildroot}/%{_sysconfdir}/pam.d/%{name}

install -D -m 0644 %{name}.toml %{buildroot}%{_sysconfdir}/greetd/%{name}.toml
install -d %{buildroot}%{_sharedstatedir}/%{name}
# rm -f {buildroot}{_sysusersdir}/{name}.conf

# pre
# sysusers_create_compat debian/cosmic-greeter.sysusers

%post
%systemd_post cosmic-greeter.service
%systemd_post cosmic-greeter-daemon.service

%preun
%systemd_preun cosmic-greeter.service
%systemd_preun cosmic-greeter-daemon.service

%postun
%systemd_postun cosmic-greeter.service
%systemd_postun cosmic-greeter-daemon.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}-daemon
%{_datadir}/dbus-1/system.d/%{appname}.conf
%{_sysusersdir}/cosmic-greeter.conf
%{_tmpfilesdir}/cosmic-greeter.conf
%{_sysconfdir}/greetd/cosmic-greeter.toml
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-daemon.service
%{_sysconfdir}/pam.d/cosmic-greeter
%{_sharedstatedir}/%{name}

