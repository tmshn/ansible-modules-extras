#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

DOCUMENTATION = '''
---
module: timedatectl
short_description: Execute `timedatectl` command to set timezone, etc
description:
  - Execute `timedatectl` command to set timezone, date/time or enable NTP.
  - See `man timedatectl` for details.
version_added: "2.1.0"
options:
  ntp:
    description:
      - Enable/Disable clock synchronization using NTP.
      - Default is to keep current setting.
    required: false
    choices: [ "yes", "no" ]
    default: null
  time:
    description:
      - Set current date and/or time of the system clock, specified in the format I(2012-10-30 18:17:16).
      - Default is to keep current setting.
    required: false
    default: null
  timezone:
    description:
      - Set time zone of the system clock, specified in the format I(Asia/Tokyo).
      - Default is to keep current setting.
    required: false
    default: null
requirements: [ "timedatectl command" ]
author: "Shinichi TAMURA @tmshn"
'''

EXAMPLES='''
- name: set timezone to Asia/Tokyo
  timedatectl: timezone=Asia/Tokyo
'''


def main():
    # Arguments setting
    # * 'name' is not required key to construct AnsibleModule,
    #   but it is used to check if change will happen.
    arguments = dict(
        ntp       = dict(default=None,  required=False, type='bool',    name='NTP enabled'),
        time      = dict(default=None,  required=False, type='str',     name='Local time'),
        timezone  = dict(default=None,  required=False, type='str',     name='Timezone'),
    )

    # Construct 'module'
    module = AnsibleModule(
        argument_spec       = arguments,
        supports_check_mode = True,
        required_one_of     = [ arguments.keys() ],
    )
    # Commands to execute to make some change.
    # (shell command will be added if needed)
    commands = []

    # Check the current state
    old_state = module.run_command('timedatectl status', check_rc=True)[1] # Get stdout
    # module.exit_json(changed=False, msg=old_state)

    for arg,spec in arguments.iteritems():
        # Check old value, which is written in `old_state`.
        # Below regex is to find the value.
        regex     = re.compile(spec['name']+r':\s*([^\n]+)\n')
        old_value = regex.search(old_state).group(1)
        new_value = module.params[arg]
        if (new_value is not None) and (new_value not in old_value):
            # then, change should happen!
            commands.append('timedatectl set-%s %s' % (arg, new_value))

    # Make changes
    if not module.check_mode:
        for command in commands:
            module.run_command(command, check_rc=True)

    # Check the current state and return.
    new_state = module.run_command('timedatectl status', check_rc=True)[1] # Get stdout
    message   = old_state + "\n|\nv\n\n" + new_state
    module.exit_json(changed=( len(commands)>0 ), msg=message)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
