=======================================
Auto-generation of sample configuration
=======================================

This generate_sample.sh tool is used to generate etc/solum/solum.conf.sample

Run it from the top-level working directory i.e.

  $> ./tools/config/generate_sample.sh -b ./ -p solum -o etc/solum

Watch out for warnings about modules like libvirt, qpid and zmq not
being found - these warnings are significant because they result
in options not appearing in the generated config file.


The analyze_opts.py tool is used to find options which appear in
/etc/solum/solum.conf but not in etc/solum/solum.conf.sample
This helps identify options in the solum.conf file which are not used by solum.
The tool also identifies any options which are set to the default value.

Run it from the top-level working directory i.e.

  $> ./tools/config/analyze_opts.py

