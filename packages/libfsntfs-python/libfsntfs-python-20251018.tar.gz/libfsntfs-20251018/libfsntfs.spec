Name: libfsntfs
Version: 20251018
Release: 1
Summary: Library to access the New Technology File System (NTFS) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libfsntfs
               
BuildRequires: gcc               

%description -n libfsntfs
Library to access the New Technology File System (NTFS) format

%package -n libfsntfs-static
Summary: Library to access the New Technology File System (NTFS) format
Group: Development/Libraries
Requires: libfsntfs = %{version}-%{release}

%description -n libfsntfs-static
Static library version of libfsntfs.

%package -n libfsntfs-devel
Summary: Header files and libraries for developing applications for libfsntfs
Group: Development/Libraries
Requires: libfsntfs = %{version}-%{release}

%description -n libfsntfs-devel
Header files and libraries for developing applications for libfsntfs.

%package -n libfsntfs-python3
Summary: Python 3 bindings for libfsntfs
Group: System Environment/Libraries
Requires: libfsntfs = %{version}-%{release} python3
BuildRequires: python3-devel python3-setuptools

%description -n libfsntfs-python3
Python 3 bindings for libfsntfs

%package -n libfsntfs-tools
Summary: Several tools for reading New Technology File System (NTFS) volumes
Group: Applications/System
Requires: libfsntfs = %{version}-%{release} openssl fuse3-libs  
BuildRequires: openssl-devel fuse3-devel  

%description -n libfsntfs-tools
Several tools for reading New Technology File System (NTFS) volumes

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libfsntfs
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libfsntfs-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libfsntfs-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libfsntfs.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libfsntfs-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libfsntfs-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Sat Oct 18 2025 Joachim Metz <joachim.metz@gmail.com> 20251018-1
- Auto-generated

