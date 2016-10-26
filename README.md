# rsnapshot_diamond_collector

### Overview
This collector will inspect a directory containing rsnapshot logs and post the last know runtime duration by taking the differnce in time from when a host started a rsnapshot job via `echo pid > /var/run/rsnap_name.pid` and the completion of that same job by finding `rm -f /var/run/rsnap_name.pid` that follows. All start times that don't have a corresponding stop time are thrown out as we assume the server had a failure mid rsnap job. 

### How to install

#### Puppet implementation

* install garethr/garethr-diamond module
  
  ```
  # mod for managing diamond
    mod 'garethr-diamond',
      :git    => 'https://github.com/fasrc/garethr-diamond.git',
  ```
  
* configuration in yaml format:

  ```---
  profiles::diamond::collectors:
    'RsnapshotRuntimeCollector':
      options:
        path_prefix: "diamond.%{::datacenter}"
        rsnap_log_home: "/var/log/rsnapshot"
  profiles::diamond::collector_installs:
    'rsnapshot_diamond_collector':
      repo_url: 'https://github.com/fasrc/rsnapshot_diamond_collector.git'
      repo_revision: 'master'
 ```
#### Manual install

* installing diamond
  * Read the [documentation](http://diamond.readthedocs.org)
  * Install via `pip install diamond`.
    The releases on GitHub are not recommended for use.
    Use `pypi-install diamond` on Debian/Ubuntu systems with python-stdeb installed to build packages.
  * Copy the `diamond.conf.example` file to `diamond.conf`.
  * Optional: Run `diamond-setup` to help set collectors in `diamond.conf`.
  * Modify `diamond.conf` for your needs.
  * Run diamond with one of: `diamond` or `initctl start diamond` or `/etc/init.d/diamond restart`.

* Add the following lines to the daimond collectors config area:

  CentOS => /etc/diamond/collectors/RsnapshotRuntimeCollector.conf
  ```enabled=True
  path_prefix = <prefix_path>
  rsnap_log_home = </var/log/rsnapshot> 
  ```
* Add the script to diamond collectors repository section:

`CentOS => /usr/share/diamond/collectors/rsnapshotruntimecollector/rsnapshotruntimecollector.py`
