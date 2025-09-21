%undefine _debugsource_packages
%define         appname com.system76.CosmicGreeter
Name:           cosmic-greeter
Version:        1.0.0
%define beta beta.1
Release:        %{?beta:0.%{beta}.}1
Summary:        COSMIC greeter for greetd
License:        GPL-3.0-only
URL:            https://github.com/pop-os/cosmic-greeter
Source0:        https://github.com/pop-os/cosmic-greeter/archive/epoch-%{version}%{?beta:-%{beta}}/%{name}-epoch-%{version}%{?beta:-%{beta}}.tar.gz
Source1:        vendor.tar.xz
Source2:        cargo_config

Source3:        %{name}.service
Source4:        %{name}-daemon.service
Source5:	cosmic-greeter.pam
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
cp %{SOURCE2} .cargo/config

%build
# Build failure workaround: https://github.com/pop-os/cosmic-files/issues/392#issuecomment-2308954953
export VERGEN_GIT_COMMIT_DATE="$(date --utc '+%Y-%m-%d %H:%M:%S %z')"
export VERGEN_GIT_SHA=$_commit
just build-release

%install
just rootdir=%{buildroot} prefix=%{_prefix} install
install -d %{buildroot}%{_sharedstatedir}/%{name}
install -D -m 0644 %{name}.toml %{buildroot}%{_sysconfdir}/greetd/%{name}.toml
chmod 0644 %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
chmod -x %{buildroot}%{_datadir}/dbus-1/system.d/%{appname}.conf
install -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}-daemon.service
rm -f %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dm0644 %{SOURCE5} %{buildroot}/%{_sysconfdir}/pam.d/%{name}
mkdir -p %{buildroot}/var/lib/greetd

%post
%systemd_post %{name}.service 
%systemd_post %{name}-daemon.service


%preun
%systemd_preun %{name}.service 
%systemd_preun %{name}-daemon.service

%postun
%systemd_postun %{name}.service
%systemd_postun %{name}-daemon.service

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
%attr(700, greeter, greeter) /var/lib/greetd
%{_sysconfdir}/pam.d/%{name}
