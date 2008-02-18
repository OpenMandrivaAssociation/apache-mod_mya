#Module-Specific definitions
%define mod_name mod_mya
%define mod_conf 80_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	3.0.1
Release:	%mkrel 6
Group:		System/Servers
License:	GPL
URL:		http://www.synthemesc.com/mod_mya/
Source0:	%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	mysql-devel
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
mod_mya is an Apache Web Server module allowing basic
authentication data to be stored in a MySQL database thus
deprecating file based configuration.
 
%prep

%setup -q -n %{mod_name}-%{version}
perl -pi -e "s/my_connect/mya_connect/g;" *.c

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
%{_sbindir}/apxs -DHAVE_STDDEF_H -I%{_includedir}/mysql -L%{_libdir} -Wl,-lmysqlclient -c mod_mya.c
    
%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*


